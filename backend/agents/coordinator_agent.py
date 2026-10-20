"""
Emergency Coordinator Agent - the central orchestrator.

PEAS:
  Performance: All emergencies resolved with minimum response time and resource waste
  Environment: All agents, city state
  Actuators: Dispatch ambulances, trigger replanning, assign doctors, coordinate resources
  Sensors: Messages from all agents, global state

This agent makes intelligent decisions based on received information,
not hard-coded rules. It uses the decision and planning engines.
"""
from .base_agent import BaseAgent
from typing import List, Dict, Optional, Any
import datetime


class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("CoordinatorAgent", "CoordinatorAgent")
        self.goal = "Coordinate all agents to resolve emergencies efficiently"
        self.state = {
            "active_emergencies": [],
            "pending_replan_requests": [],
            "resolved_emergencies": 0,
            "total_replans": 0,
            "ambulance_conflicts": []
        }
        self.knowledge = {
            "hospital_status": {},
            "doctor_status": {},
            "ambulance_status": {},
            "road_alerts": []
        }
        # Callbacks set by simulator
        self._on_replan: Optional[Any] = None
        self._on_dispatch: Optional[Any] = None

    def sense(self, environment: dict):
        for h in environment.get("hospitals", []):
            self.knowledge["hospital_status"][h["hospital_id"]] = h
        for d in environment.get("doctors", []):
            self.knowledge["doctor_status"][d["doctor_id"]] = d
        for a in environment.get("ambulances", []):
            self.knowledge["ambulance_status"][a["ambulance_id"]] = a

    def decide(self) -> str:
        if self.state["pending_replan_requests"]:
            return "TRIGGER_REPLAN"
        if self.state["active_emergencies"]:
            return "COORDINATE_EMERGENCIES"
        return "MONITOR"

    def act(self, environment: dict) -> List[dict]:
        action = self.decide()
        self.current_action = action
        effects = []

        if action == "TRIGGER_REPLAN":
            req = self.state["pending_replan_requests"].pop(0)
            self.state["total_replans"] += 1
            effects.append({
                "type": "REPLAN_TRIGGERED",
                "emergency_id": req.get("emergency_id", ""),
                "reason": req.get("reason", "Environment changed")
            })
            if self._on_replan:
                self._on_replan(req)

        return effects

    def register_emergency(self, emergency_id: str):
        if emergency_id not in self.state["active_emergencies"]:
            self.state["active_emergencies"].append(emergency_id)

    def resolve_emergency(self, emergency_id: str):
        if emergency_id in self.state["active_emergencies"]:
            self.state["active_emergencies"].remove(emergency_id)
        self.state["resolved_emergencies"] += 1

    def detect_ambulance_conflict(self, a1_id: str, a2_id: str, road_id: str) -> dict:
        """Called when two ambulances try to use the same road segment."""
        conflict = {
            "ambulance_1": a1_id,
            "ambulance_2": a2_id,
            "road_id": road_id,
            "timestamp": _now(),
            "resolution": "Lower priority ambulance will replan"
        }
        self.state["ambulance_conflicts"].append(conflict)
        self.send_message(
            a2_id, "ROAD_CONFLICT",
            f"Road {road_id} is in use by higher-priority ambulance {a1_id}. Replanning.",
            {"road_id": road_id, "priority_ambulance": a1_id}
        )
        return conflict

    def _handle_message(self, msg: dict):
        msg_type = msg["type"]

        if msg_type in ("ICU_UNAVAILABLE", "SPECIALIST_UNAVAILABLE", "ROAD_BLOCKED", "ROAD_CONGESTED"):
            self.knowledge["road_alerts"].append(msg)
            # Find affected emergencies and request replan
            for eid in self.state["active_emergencies"]:
                self.state["pending_replan_requests"].append({
                    "emergency_id": eid,
                    "reason": msg["content"],
                    "trigger": msg_type,
                    "data": msg["data"]
                })

        elif msg_type == "REPLAN_REQUEST":
            self.state["pending_replan_requests"].append({
                "emergency_id": msg["data"].get("emergency_id", ""),
                "ambulance_id": msg["data"].get("ambulance_id", ""),
                "reason": msg["data"].get("reason", "Unknown"),
                "trigger": "AMBULANCE_REQUEST"
            })

        elif msg_type == "DOCTOR_UNAVAILABLE":
            self.knowledge["doctor_status"][msg["data"].get("doctor_id", "")] = {"availability": False}
            for eid in self.state["active_emergencies"]:
                self.state["pending_replan_requests"].append({
                    "emergency_id": eid,
                    "reason": msg["content"],
                    "trigger": "DOCTOR_UNAVAILABLE"
                })

    def set_replan_callback(self, callback):
        self._on_replan = callback

    def get_stats(self) -> dict:
        return {
            "active_emergencies": len(self.state["active_emergencies"]),
            "resolved": self.state["resolved_emergencies"],
            "total_replans": self.state["total_replans"],
            "conflicts_resolved": len(self.state["ambulance_conflicts"])
        }


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")
