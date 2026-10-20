"""
Main simulation engine - fixed version.
Manages all agents, ticks the simulation, handles events, and coordinates replanning.
"""
import asyncio
import datetime
import copy
from typing import Dict, List, Optional, Any

from simulation.city_grid import get_city_graph, reset_city_graph
from simulation.seed_data import HOSPITALS, AMBULANCES, DOCTORS, SCENARIO_PATIENTS, SCENARIO_DESCRIPTIONS

from agents.patient_agent import PatientAgent
from agents.ambulance_agent import AmbulanceAgent
from agents.hospital_agent import HospitalAgent
from agents.doctor_agent import DoctorAgent
from agents.traffic_agent import TrafficAgent
from agents.coordinator_agent import CoordinatorAgent

from search.graph import SearchGraph
from search.astar import astar
from search.bfs import bfs
from search.dfs import dfs
from search.ucs import ucs
from search.greedy import greedy

from knowledge.knowledge_base import get_knowledge_base, reset_knowledge_base
from reasoning.forward_chaining import forward_chain
from reasoning.backward_chaining import can_hospital_treat_patient

from decision.utility_engine import select_best_hospital
from planning.emergency_planner import EmergencyPlan

from communication.message_bus import get_message_bus, reset_message_bus
from database.mongo import get_db


class Simulator:
    def __init__(self):
        self.tick_count = 0
        self.status = "IDLE"  # IDLE | RUNNING | PAUSED
        self._tick_task: Optional[asyncio.Task] = None
        self.tick_interval = 1.0  # seconds per simulation tick

        self.city_graph = None

        # Agent registries
        self.patient_agents: Dict[str, PatientAgent] = {}
        self.ambulance_agents: Dict[str, AmbulanceAgent] = {}
        self.hospital_agents: Dict[str, HospitalAgent] = {}
        self.doctor_agents: Dict[str, DoctorAgent] = {}
        self.traffic_agent: Optional[TrafficAgent] = None
        self.coordinator: Optional[CoordinatorAgent] = None

        # Emergency and plan tracking
        self.emergencies: Dict[str, dict] = {}
        self.plans: Dict[str, EmergencyPlan] = {}
        # Maps patient_id -> emergency_id for quick lookup
        self._patient_to_emergency: Dict[str, str] = {}
        # Maps ambulance_id -> patient_id
        self._ambulance_to_patient: Dict[str, str] = {}

        self.analytics = {
            "total_emergencies": 0,
            "completed_emergencies": 0,
            "failed_emergencies": 0,
            "total_replans": 0,
            "total_messages": 0,
            "search_runs": []
        }
        self._emergency_start_ticks: Dict[str, int] = {}
        self._scheduled_events: List[dict] = []
        self._initialized = False

    # ─── Initialization ──────────────────────────────────────────────────────

    def initialize(self, scenario: str = "scenario_1"):
        self.scenario_name = scenario
        reset_message_bus()
        reset_knowledge_base()
        self.city_graph = reset_city_graph()

        self.patient_agents.clear()
        self.ambulance_agents.clear()
        self.hospital_agents.clear()
        self.doctor_agents.clear()
        self.emergencies.clear()
        self.plans.clear()
        self._patient_to_emergency.clear()
        self._ambulance_to_patient.clear()
        self.tick_count = 0
        self._scheduled_events.clear()
        self._emergency_start_ticks.clear()
        self.analytics = {
            "total_emergencies": 0, "completed_emergencies": 0,
            "failed_emergencies": 0, "total_replans": 0,
            "total_messages": 0, "search_runs": []
        }

        for h in HOSPITALS:
            self.hospital_agents[h["hospital_id"]] = HospitalAgent(copy.deepcopy(h))
        for a in AMBULANCES:
            self.ambulance_agents[a["ambulance_id"]] = AmbulanceAgent(copy.deepcopy(a))
        for d in DOCTORS:
            self.doctor_agents[d["doctor_id"]] = DoctorAgent(copy.deepcopy(d))

        self.traffic_agent = TrafficAgent(self.city_graph)
        self.coordinator = CoordinatorAgent()
        # Use a sync wrapper — the coordinator calls this; actual async work is
        # scheduled via asyncio.ensure_future inside
        self.coordinator.set_replan_callback(self._sync_replan_callback)

        patients = SCENARIO_PATIENTS.get(scenario, SCENARIO_PATIENTS["scenario_1"])
        for p in patients:
            pd = copy.deepcopy(p)
            self.patient_agents[pd["patient_id"]] = PatientAgent(pd)

        # Deep-copy auto_events so delay_ticks aren't mutated on the originals
        scenario_def = SCENARIO_DESCRIPTIONS.get(scenario, {})
        for event in scenario_def.get("auto_events", []):
            self._scheduled_events.append(copy.deepcopy(event))

        self._initialized = True
        bus = get_message_bus()
        bus.publish("Simulator", "ALL", "SIM_INITIALIZED",
                    f"Simulation initialized with {scenario}",
                    {"scenario": scenario, "patients": len(self.patient_agents)})

    def _sync_replan_callback(self, req: dict):
        """Synchronous bridge: schedule the async replan as a task."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self._handle_replan_request(req))
        except RuntimeError:
            pass

    # ─── Simulation Loop ─────────────────────────────────────────────────────

    async def start(self, scenario: str = "scenario_1"):
        if self.status == "RUNNING":
            return
        if not self._initialized:
            self.initialize(scenario)
        self.status = "RUNNING"
        self._tick_task = asyncio.create_task(self._run_loop())

    async def pause(self):
        self.status = "PAUSED"

    async def resume(self):
        if self.status == "PAUSED":
            self.status = "RUNNING"
            self._tick_task = asyncio.create_task(self._run_loop())

    async def reset(self, scenario: str = "scenario_1"):
        old_status = self.status
        self.status = "IDLE"
        if self._tick_task and not self._tick_task.done():
            self._tick_task.cancel()
            try:
                await self._tick_task
            except asyncio.CancelledError:
                pass
                
        # Log previous run to DB
        if self.tick_count > 0:
            db = get_db()
            if db is not None:
                try:
                    run_data = {
                        "scenario": getattr(self, "scenario_name", "unknown"),
                        "total_ticks": self.tick_count,
                        "analytics": copy.deepcopy(self.analytics),
                        "timestamp": _now()
                    }
                    await db["simulation_runs"].insert_one(run_data)
                except Exception:
                    pass

        self.initialize(scenario)

    async def _run_loop(self):
        while self.status == "RUNNING":
            await self._tick()
            await asyncio.sleep(self.tick_interval)

    async def _tick(self):
        self.tick_count += 1
        bus = get_message_bus()
        env = self._build_environment()

        # Fire scheduled auto-events
        for event in list(self._scheduled_events):
            if event.get("delay_ticks", 0) <= 0:
                await self.inject_event(event["type"], event)
                self._scheduled_events.remove(event)
            else:
                event["delay_ticks"] -= 1

        # Sense phase – all agents update their knowledge
        for agent in self._all_agents():
            agent.sense(env)

        # Patient agents act – may generate emergencies
        for pa in list(self.patient_agents.values()):
            effects = pa.act(env)
            bus.collect_agent_messages(pa.flush_outbox())
            for effect in effects:
                if effect["type"] == "EMERGENCY_GENERATED":
                    await self._handle_new_emergency(effect["patient_id"])

        # Coordinator acts (processes pending replan requests)
        self.coordinator.act(env)
        # Deliver coordinator outbox right now, before flushing bus
        self._deliver_outbox_to_agents(self.coordinator.flush_outbox())

        # Ambulance agents act (navigate step by step)
        for aa in list(self.ambulance_agents.values()):
            effects = aa.act(env)
            # Deliver ambulance outbox to coordinator
            for msg in aa.flush_outbox():
                bus.publish(msg["sender"], msg["receiver"],
                            msg["message_type"], msg["content"], msg.get("data", {}))
                self.coordinator.communicate(
                    msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))
            for effect in effects:
                await self._handle_ambulance_effect(effect)

        # Hospital agents act
        for ha in list(self.hospital_agents.values()):
            ha.act(env)
            for msg in ha.flush_outbox():
                bus.publish(msg["sender"], msg["receiver"],
                            msg["message_type"], msg["content"], msg.get("data", {}))
                self.coordinator.communicate(
                    msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))

        # Doctor agents act
        for da in list(self.doctor_agents.values()):
            da.act(env)
            for msg in da.flush_outbox():
                bus.publish(msg["sender"], msg["receiver"],
                            msg["message_type"], msg["content"], msg.get("data", {}))

        # Traffic agent messages
        for msg in self.traffic_agent.flush_outbox():
            bus.publish(msg["sender"], msg["receiver"],
                        msg["message_type"], msg["content"], msg.get("data", {}))
            if msg["receiver"] == "ALL_AMBULANCES":
                for aa in self.ambulance_agents.values():
                    aa.communicate(msg["sender"], msg["message_type"],
                                   msg["content"], msg.get("data", {}))
            self.coordinator.communicate(
                msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))

        # Update message count in analytics
        self.analytics["total_messages"] = bus.get_message_count()

        # Broadcast tick state to WebSocket clients
        tick_messages = bus.flush_tick_messages()
        state = self._build_sim_state(tick_messages)
        await bus.broadcast({"type": "SIM_TICK", "data": state})

    def _deliver_outbox_to_agents(self, outbox: List[dict]):
        """Route messages from coordinator outbox to target agents."""
        bus = get_message_bus()
        for msg in outbox:
            receiver = msg["receiver"]
            bus.publish(msg["sender"], receiver, msg["message_type"],
                        msg["content"], msg.get("data", {}))
            if receiver in self.ambulance_agents:
                self.ambulance_agents[receiver].communicate(
                    msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))
            elif receiver in self.hospital_agents:
                self.hospital_agents[receiver].communicate(
                    msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))
            elif receiver in self.doctor_agents:
                self.doctor_agents[receiver].communicate(
                    msg["sender"], msg["message_type"], msg["content"], msg.get("data", {}))

    # ─── Emergency Handling ────────────────────────────────────────────────

    async def _handle_new_emergency(self, patient_id: str):
        # Prevent duplicate emergencies for the same patient
        if patient_id in self._patient_to_emergency:
            return
        bus = get_message_bus()
        patient_agent = self.patient_agents.get(patient_id)
        if not patient_agent:
            return
        patient = patient_agent.state

        eid = f"E{len(self.emergencies)+1:03d}"
        self.emergencies[eid] = {
            "emergency_id": eid,
            "patient_id": patient_id,
            "severity": patient["severity"],
            "status": "ACTIVE",
            "assigned_ambulance": None,
            "assigned_hospital": None,
            "assigned_doctor": None,
            "utility_scores": {},
            "created_at": _now(),
            "replan_count": 0
        }
        self._patient_to_emergency[patient_id] = eid
        self._emergency_start_ticks[eid] = self.tick_count
        self.analytics["total_emergencies"] += 1
        self.coordinator.register_emergency(eid)

        bus.publish("PatientAgent", "CoordinatorAgent", "EMERGENCY_REQUEST",
                    f"Emergency {eid}: Patient {patient_id} — {patient['severity']} {patient['emergency_type']}",
                    {"emergency_id": eid, "patient_id": patient_id, "severity": patient["severity"]})

        # Plan steps 1-2: Detect and prioritize
        plan = EmergencyPlan(eid, patient_id)
        plan.steps[0].complete("Emergency detected")
        plan.steps[1].complete(f"Priority: {patient['severity']}")
        plan.current_step_index = 2
        plan.steps[2].start("Searching for available ambulance")
        self.plans[eid] = plan

        # Step 3: Assign ambulance (closest idle one)
        ambulance = self._find_best_ambulance(patient["location"])
        if not ambulance:
            self.emergencies[eid]["status"] = "FAILED"
            self.analytics["failed_emergencies"] += 1
            plan.steps[2].fail("No ambulance available")
            bus.publish("CoordinatorAgent", "Simulator", "NO_AMBULANCE",
                        f"No ambulance available for {eid}", {})
            return

        ambulance.assign_emergency(patient_id, patient["location"],
                                   priority=_severity_priority(patient["severity"]))
        self._ambulance_to_patient[ambulance.agent_id] = patient_id
        plan.steps[2].complete(f"Ambulance {ambulance.agent_id} assigned")
        plan.selected_ambulance = ambulance.agent_id
        self.emergencies[eid]["assigned_ambulance"] = ambulance.agent_id

        bus.publish("CoordinatorAgent", ambulance.agent_id, "DISPATCH",
                    f"Ambulance {ambulance.agent_id} dispatched for {eid}",
                    {"emergency_id": eid, "patient_id": patient_id})

        # Step 4: Calculate route to patient
        plan.current_step_index = 3
        plan.steps[3].start("Calculating route to patient")
        route = self._calculate_route(ambulance.state["current_location"], patient["location"])
        if route:
            ambulance.set_route_to_patient(route)
            plan.steps[3].complete(f"Route: {len(route)} steps via A*")
        else:
            plan.steps[3].fail("No route found")
            self.emergencies[eid]["status"] = "FAILED"
            self.analytics["failed_emergencies"] += 1
            return

        plan.current_step_index = 4
        plan.steps[4].start("Evaluating hospitals using utility function")

        # Steps 5-6 + KB + utility selection
        await self._select_and_plan_hospital(eid, plan, patient_agent, ambulance)

    async def _select_and_plan_hospital(self, eid: str, plan: EmergencyPlan,
                                         patient_agent: PatientAgent,
                                         ambulance: AmbulanceAgent):
        bus = get_message_bus()
        patient = patient_agent.state
        hospitals = [ha.state for ha in self.hospital_agents.values()]
        doctors = [da.state for da in self.doctor_agents.values()]
        amb_loc = ambulance.state["current_location"]
        amb_pos = [amb_loc["row"], amb_loc["col"]]

        # ── Knowledge Base: load facts ──
        kb = get_knowledge_base()
        kb.reset_derived_facts()
        kb.load_patient_facts(patient)
        for h in hospitals:
            kb.load_hospital_facts(h)
        for d in doctors:
            kb.load_doctor_facts(d)
        for road in self.city_graph.edges.values():
            kb.load_road_facts(road)

        # ── Forward Chaining: derive eligibility ──
        derivations = forward_chain(kb)
        bus.publish("KnowledgeBase", "DecisionEngine", "FC_COMPLETE",
                    f"Forward chaining derived {len(derivations)} new facts",
                    {"derivation_count": len(derivations)})

        # ── Utility-Based Decision: rank hospitals ──
        best_score, all_scores = select_best_hospital(
            hospitals, patient, doctors, self.city_graph, amb_pos)
        self.emergencies[eid]["utility_scores"] = {s["hospital_id"]: s for s in all_scores}

        if not best_score:
            plan.steps[4].fail("No eligible hospital found")
            plan.steps[5].fail("All hospitals rejected")
            self.emergencies[eid]["status"] = "FAILED"
            self.analytics["failed_emergencies"] += 1
            bus.publish("DecisionEngine", "CoordinatorAgent", "NO_HOSPITAL",
                        f"No suitable hospital for emergency {eid}", {})
            return

        selected_hid = best_score["hospital_id"]
        plan.steps[4].complete(f"Evaluated {len(hospitals)} hospitals")
        plan.steps[5].complete(
            f"Selected {selected_hid} (score={best_score['utility_score']:.3f})")
        plan.current_step_index = 6
        plan.selected_hospital = selected_hid
        self.emergencies[eid]["assigned_hospital"] = selected_hid

        bus.publish("DecisionEngine", ambulance.agent_id, "HOSPITAL_SELECTED",
                    f"Hospital {selected_hid} selected for {eid}",
                    {"hospital_id": selected_hid,
                     "utility_score": best_score["utility_score"],
                     "all_scores": all_scores})

        # Step 7: Calculate route from patient location to hospital
        plan.steps[6].start("Calculating A* route to hospital")
        hosp_loc = self.hospital_agents[selected_hid].state["location"]
        route_to_hosp = self._calculate_route(patient["location"], hosp_loc)
        if route_to_hosp:
            ambulance.set_route_to_hospital(selected_hid, route_to_hosp)
            plan.route = route_to_hosp
            plan.steps[6].complete(f"A* route: {len(route_to_hosp)} steps")
        else:
            plan.steps[6].fail("No route to hospital")
            self.emergencies[eid]["status"] = "FAILED"
            self.analytics["failed_emergencies"] += 1
            return

        plan.current_step_index = 7
        plan.steps[7].start("Transporting patient to hospital")

        bus.publish("SearchEngine", ambulance.agent_id, "ROUTE_CALCULATED",
                    f"Route to {selected_hid}: {len(route_to_hosp)} steps",
                    {"route": route_to_hosp, "hospital_id": selected_hid})

        # Step 10: Reserve resources
        needs_icu = "ICU" in patient.get("required_resources", [])
        self.hospital_agents[selected_hid].reserve_bed(patient["patient_id"], needs_icu)
        plan.steps[9].complete(f"Resources reserved at {selected_hid}")

        # Step 9: Assign doctor
        plan.steps[8].start("Assigning specialist doctor")
        req_spec = patient.get("required_specialist", "")
        doctor = self._find_available_doctor(selected_hid, req_spec)
        if doctor:
            doctor.assign_patient(patient["patient_id"])
            plan.steps[8].complete(f"{doctor.agent_id} assigned")
            self.emergencies[eid]["assigned_doctor"] = doctor.agent_id
            bus.publish("CoordinatorAgent", doctor.agent_id, "PATIENT_ASSIGNMENT",
                        f"{doctor.state['name']} assigned to {patient['patient_id']}",
                        {"patient_id": patient["patient_id"]})
        else:
            plan.steps[8].fail(
                f"No {req_spec} available at {selected_hid} — will use general practitioner")

    async def _handle_ambulance_effect(self, effect: dict):
        bus = get_message_bus()
        etype = effect.get("type")

        if etype == "PATIENT_PICKED_UP":
            amb_id = effect["ambulance_id"]
            patient_id = effect["patient_id"]
            eid = self._patient_to_emergency.get(patient_id)
            if eid and eid in self.plans:
                plan = self.plans[eid]
                if plan.steps[7].status in ("PENDING", "IN_PROGRESS"):
                    plan.steps[7].complete(f"Patient picked up by {amb_id}")
            bus.publish(amb_id, "CoordinatorAgent", "PATIENT_PICKED_UP",
                        f"{amb_id} has picked up patient {patient_id}", effect)

        elif etype == "ARRIVED_AT_HOSPITAL":
            amb_id = effect["ambulance_id"]
            hosp_id = effect["hospital_id"]
            patient_id = self._ambulance_to_patient.get(amb_id)
            eid = self._patient_to_emergency.get(patient_id) if patient_id else None
            if eid:
                self._complete_emergency(eid, amb_id, hosp_id)
            bus.publish(amb_id, hosp_id, "PATIENT_ARRIVED",
                        f"Patient arrived at {hosp_id}",
                        {"ambulance_id": amb_id, "hospital_id": hosp_id})

        elif etype == "PATIENT_DELIVERED":
            amb_id = effect["ambulance_id"]
            # Clean up mapping
            self._ambulance_to_patient.pop(amb_id, None)

    def _complete_emergency(self, eid: str, amb_id: str, hosp_id: str):
        bus = get_message_bus()
        plan = self.plans.get(eid)
        if plan and plan.status == "ACTIVE":
            plan.steps[7].complete("Patient transported successfully")
            plan.steps[10].complete("Emergency treatment initiated")
            plan.complete()

        self.emergencies[eid]["status"] = "COMPLETED"
        self.emergencies[eid]["completed_at"] = _now()
        self.coordinator.resolve_emergency(eid)
        self.analytics["completed_emergencies"] += 1

        db = get_db()
        if db is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    em_data = copy.deepcopy(self.emergencies[eid])
                    asyncio.create_task(db["emergencies"].insert_one(em_data))
            except Exception:
                pass

        ticks_taken = self.tick_count - self._emergency_start_ticks.get(eid, 0)
        bus.publish("Simulator", "ALL", "EMERGENCY_COMPLETED",
                    f"Emergency {eid} resolved in {ticks_taken} ticks",
                    {"emergency_id": eid, "response_ticks": ticks_taken})

    # ─── Replanning ───────────────────────────────────────────────────────

    async def _handle_replan_request(self, req: dict):
        bus = get_message_bus()
        eid = req.get("emergency_id", "")
        reason = req.get("reason", "Environment changed")

        # If no specific emergency, replan all active ones
        if not eid:
            active = [e for e in self.emergencies.values() if e["status"] == "ACTIVE"]
            for e in active:
                await self._do_replan(e["emergency_id"], reason)
            return

        if eid in self.emergencies and self.emergencies[eid]["status"] == "ACTIVE":
            await self._do_replan(eid, reason)

    async def _do_replan(self, eid: str, reason: str):
        bus = get_message_bus()
        old_plan = self.plans.get(eid)
        if not old_plan or old_plan.status != "ACTIVE":
            return

        old_plan.invalidate(reason)
        new_plan = old_plan.create_new_version()
        self.plans[eid] = new_plan
        self.emergencies[eid]["replan_count"] += 1
        self.analytics["total_replans"] += 1

        bus.publish("CoordinatorAgent", "ALL", "PLAN_INVALIDATED",
                    f"Plan for {eid} invalidated: {reason}",
                    {"emergency_id": eid, "reason": reason})
        bus.publish("CoordinatorAgent", "ALL", "NEW_PLAN_GENERATED",
                    f"New plan v{new_plan.version} for {eid}",
                    {"emergency_id": eid, "version": new_plan.version})

        # Re-run hospital selection with current state
        amb_id = new_plan.selected_ambulance
        patient_id = self.emergencies[eid]["patient_id"]
        ambulance = self.ambulance_agents.get(amb_id)
        patient_agent = self.patient_agents.get(patient_id)

        if ambulance and patient_agent and ambulance.state["status"] not in ("IDLE", "ARRIVED"):
            await self._select_and_plan_hospital(eid, new_plan, patient_agent, ambulance)

    # ─── Event Injection ──────────────────────────────────────────────────

    async def inject_event(self, event_type: str, data: dict = None):
        data = data or {}
        bus = get_message_bus()

        if event_type == "ROAD_CONGESTED":
            road_id = data.get("road_id", "R045")
            self.traffic_agent.set_road_state(road_id, "CONGESTED")
            for msg in self.traffic_agent.flush_outbox():
                bus.publish(msg["sender"], msg["receiver"],
                            msg["message_type"], msg["content"], msg.get("data", {}))
                if msg["receiver"] == "ALL_AMBULANCES":
                    for aa in self.ambulance_agents.values():
                        aa.communicate(msg["sender"], msg["message_type"],
                                       msg["content"], msg.get("data", {}))
                self.coordinator.communicate(msg["sender"], msg["message_type"],
                                             msg["content"], msg.get("data", {}))

        elif event_type == "ROAD_BLOCKED":
            road_id = data.get("road_id", "R045")
            self.traffic_agent.set_road_state(road_id, "BLOCKED")
            for msg in self.traffic_agent.flush_outbox():
                bus.publish(msg["sender"], msg["receiver"],
                            msg["message_type"], msg["content"], msg.get("data", {}))
                if msg["receiver"] == "ALL_AMBULANCES":
                    for aa in self.ambulance_agents.values():
                        aa.communicate(msg["sender"], msg["message_type"],
                                       msg["content"], msg.get("data", {}))
                self.coordinator.communicate(msg["sender"], msg["message_type"],
                                             msg["content"], msg.get("data", {}))

        elif event_type == "HOSPITAL_ICU_FULL":
            hosp_id = data.get("hospital_id", "H1")
            if hosp_id in self.hospital_agents:
                ha = self.hospital_agents[hosp_id]
                ha.set_icu_available(0)
                for msg in ha.flush_outbox():
                    bus.publish(msg["sender"], msg["receiver"],
                                msg["message_type"], msg["content"], msg.get("data", {}))
                    self.coordinator.communicate(msg["sender"], msg["message_type"],
                                                 msg["content"], msg.get("data", {}))

        elif event_type == "DOCTOR_UNAVAILABLE":
            doc_id = data.get("doctor_id", "D01")
            if doc_id in self.doctor_agents:
                da = self.doctor_agents[doc_id]
                da.become_unavailable("Event triggered")
                for msg in da.flush_outbox():
                    bus.publish(msg["sender"], msg["receiver"],
                                msg["message_type"], msg["content"], msg.get("data", {}))
                    self.coordinator.communicate(msg["sender"], msg["message_type"],
                                                 msg["content"], msg.get("data", {}))

        elif event_type == "NEW_EMERGENCY":
            patient_data = data.get("patient", {})
            if patient_data and patient_data.get("patient_id"):
                pid = patient_data["patient_id"]
                if pid not in self.patient_agents:
                    self.patient_agents[pid] = PatientAgent(patient_data)

        elif event_type == "HOSPITAL_SPECIALIST_UNAVAILABLE":
            hosp_id = data.get("hospital_id", "H1")
            spec = data.get("specialization", "Cardiologist")
            if hosp_id in self.hospital_agents:
                ha = self.hospital_agents[hosp_id]
                ha.set_specialist_unavailable(spec)
                for msg in ha.flush_outbox():
                    bus.publish(msg["sender"], msg["receiver"],
                                msg["message_type"], msg["content"], msg.get("data", {}))
                    self.coordinator.communicate(msg["sender"], msg["message_type"],
                                                 msg["content"], msg.get("data", {}))

        return {"status": "injected", "event_type": event_type}

    # ─── Search ────────────────────────────────────────────────────────────

    def _calculate_route(self, start_loc: dict, end_loc: dict) -> List[List[int]]:
        start = (start_loc["row"], start_loc["col"])
        end = (end_loc["row"], end_loc["col"])
        sg = SearchGraph(self.city_graph)
        result = astar(sg, start, end)
        if result.success:
            self.analytics["search_runs"].append(result.to_dict())
            return [list(p) for p in result.path]
        return []

    def run_search(self, algorithm: str, start: List[int], goal: List[int]) -> dict:
        s, g = tuple(start), tuple(goal)
        sg = SearchGraph(self.city_graph)
        algo_map = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "greedy": greedy, "astar": astar}
        fn = algo_map.get(algorithm, astar)
        result = fn(sg, s, g)
        r = result.to_dict()
        self.analytics["search_runs"].append(r)
        
        db = get_db()
        if db is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    search_data = copy.deepcopy(r)
                    search_data["algorithm"] = algorithm
                    asyncio.create_task(db["search_results"].insert_one(search_data))
            except Exception:
                pass
                
        return r

    # ─── Helpers ───────────────────────────────────────────────────────────

    def _find_best_ambulance(self, patient_location: dict) -> Optional[AmbulanceAgent]:
        idle = [a for a in self.ambulance_agents.values() if a.state["status"] == "IDLE"]
        if not idle:
            return None
        ploc = patient_location
        def dist(a):
            loc = a.state["current_location"]
            return abs(loc["row"] - ploc["row"]) + abs(loc["col"] - ploc["col"])
        return min(idle, key=dist)

    def _find_available_doctor(self, hospital_id: str, specialization: str) -> Optional[DoctorAgent]:
        for da in self.doctor_agents.values():
            if (da.state["hospital_id"] == hospital_id
                    and da.state["availability"]
                    and da.state["specialization"] == specialization):
                return da
        return None

    def _all_agents(self):
        agents = list(self.patient_agents.values())
        agents += list(self.ambulance_agents.values())
        agents += list(self.hospital_agents.values())
        agents += list(self.doctor_agents.values())
        if self.traffic_agent:
            agents.append(self.traffic_agent)
        if self.coordinator:
            agents.append(self.coordinator)
        return agents

    def _build_environment(self) -> dict:
        return {
            "tick": self.tick_count,
            "patients": [pa.state for pa in self.patient_agents.values()],
            "ambulances": [aa.state for aa in self.ambulance_agents.values()],
            "hospitals": [ha.state for ha in self.hospital_agents.values()],
            "doctors": [da.state for da in self.doctor_agents.values()],
            "roads": self.traffic_agent.get_all_roads_for_ui() if self.traffic_agent else []
        }

    def _build_sim_state(self, tick_messages: List[dict]) -> dict:
        plans_dict = {eid: p.to_dict() for eid, p in self.plans.items()}
        return {
            "tick": self.tick_count,
            "status": self.status,
            "patients": [pa.state for pa in self.patient_agents.values()],
            "ambulances": [aa.state for aa in self.ambulance_agents.values()],
            "hospitals": [ha.state for ha in self.hospital_agents.values()],
            "doctors": [da.state for da in self.doctor_agents.values()],
            "roads": self.traffic_agent.get_all_roads_for_ui() if self.traffic_agent else [],
            "emergencies": list(self.emergencies.values()),
            "messages": tick_messages,
            "active_plans": plans_dict,
            "agent_states": {a.agent_id: a.to_dict() for a in self._all_agents()},
            "analytics": self._get_analytics(),
            "coordinator_stats": self.coordinator.get_stats() if self.coordinator else {}
        }

    def _get_analytics(self) -> dict:
        a = dict(self.analytics)
        a["hospital_utilization"] = {
            hid: {
                "name": ha.state.get("name", hid),
                "bed_usage_pct": round(
                    (1 - ha.state["available_beds"] / max(ha.state["total_beds"], 1)) * 100, 1),
                "icu_usage_pct": round(
                    (1 - ha.state["icu_available"] / max(ha.state["icu_total"], 1)) * 100, 1),
            }
            for hid, ha in self.hospital_agents.items()
        }
        a["ambulance_utilization"] = {
            aid: {"status": aa.state["status"]}
            for aid, aa in self.ambulance_agents.items()
        }
        return a

    def get_full_state(self) -> dict:
        if not self._initialized:
            return {"status": "NOT_INITIALIZED", "tick": 0,
                    "emergencies": [], "ambulances": [], "hospitals": [],
                    "patients": [], "doctors": [], "roads": [],
                    "messages": [], "active_plans": {}, "agent_states": {},
                    "analytics": {}, "coordinator_stats": {}}
        return self._build_sim_state([])

    def get_knowledge_snapshot(self) -> dict:
        return get_knowledge_base().snapshot()


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def _severity_priority(severity: str) -> int:
    return {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}.get(severity, 1)


# ── Global singleton ──────────────────────────────────────────────────────────
_simulator: Optional[Simulator] = None

def get_simulator() -> Simulator:
    global _simulator
    if _simulator is None:
        _simulator = Simulator()
    return _simulator
