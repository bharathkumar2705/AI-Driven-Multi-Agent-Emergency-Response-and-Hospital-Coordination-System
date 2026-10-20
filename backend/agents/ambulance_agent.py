"""
Ambulance Agent - navigates city, picks up patients, transports to hospitals.

PEAS:
  Performance: Minimise patient transport time; successful hospital delivery
  Environment: City grid with dynamic road conditions
  Actuators: Move along route, accept/reject dispatch, request replanning
  Sensors: Current location, road states, hospital availability, patient location
"""
from .base_agent import BaseAgent
from typing import List, Optional


class AmbulanceAgent(BaseAgent):
    def __init__(self, ambulance_data: dict):
        super().__init__(ambulance_data["ambulance_id"], "AmbulanceAgent")
        self.goal = "Reach patient and transport to best suitable hospital efficiently"
        loc = ambulance_data["current_location"]
        self.state = {
            "ambulance_id": self.agent_id,
            "current_location": loc,
            "status": "IDLE",
            "capacity": ambulance_data.get("capacity", 1),
            "assigned_patient": None,
            "assigned_hospital": None,
            "current_route": [],
            "route_index": 0,
            "priority": ambulance_data.get("priority", 1),
            "replan_requested": False
        }
        self.knowledge = {
            "known_hospitals": [],
            "known_road_states": {},
            "last_hospital_scores": []
        }

    def sense(self, environment: dict):
        # Update knowledge of road conditions
        for road in environment.get("roads", []):
            self.knowledge["known_road_states"][road["road_id"]] = road.get("state", "NORMAL")

    def decide(self) -> str:
        status = self.state["status"]
        if status == "IDLE":
            return "WAIT_FOR_DISPATCH"
        elif status == "DISPATCHED":
            return "START_NAVIGATION_TO_PATIENT"
        elif status == "EN_ROUTE_TO_PATIENT":
            if self.state["replan_requested"]:
                return "REPLAN_ROUTE"
            return "NAVIGATE_TO_PATIENT"
        elif status == "PATIENT_PICKED_UP":
            return "NAVIGATE_TO_HOSPITAL"
        elif status == "EN_ROUTE_TO_HOSPITAL":
            if self.state["replan_requested"]:
                return "REPLAN_ROUTE"
            return "NAVIGATE_TO_HOSPITAL"
        elif status == "ARRIVED":
            return "DELIVER_PATIENT"
        return "IDLE"

    def act(self, environment: dict) -> List[dict]:
        action = self.decide()
        self.current_action = action
        effects = []

        if action in ("NAVIGATE_TO_PATIENT", "NAVIGATE_TO_HOSPITAL"):
            moved = self._move_along_route()
            if moved:
                effects.append({
                    "type": "AMBULANCE_MOVED",
                    "ambulance_id": self.agent_id,
                    "new_location": self.state["current_location"]
                })

            # Check if reached destination
            route = self.state["current_route"]
            idx = self.state["route_index"]
            if route and idx >= len(route):
                if self.state["status"] == "EN_ROUTE_TO_PATIENT":
                    self.state["status"] = "PATIENT_PICKED_UP"
                    effects.append({"type": "PATIENT_PICKED_UP", "ambulance_id": self.agent_id,
                                    "patient_id": self.state["assigned_patient"]})
                    self.send_message(
                        self.state["assigned_patient"] or "Dispatcher",
                        "EN_ROUTE",
                        f"Ambulance {self.agent_id} picked up patient. En route to hospital.",
                        {"ambulance_id": self.agent_id}
                    )
                elif self.state["status"] == "EN_ROUTE_TO_HOSPITAL":
                    self.state["status"] = "ARRIVED"
                    effects.append({"type": "ARRIVED_AT_HOSPITAL", "ambulance_id": self.agent_id,
                                    "hospital_id": self.state["assigned_hospital"]})

        elif action == "DELIVER_PATIENT":
            effects.append({
                "type": "PATIENT_DELIVERED",
                "ambulance_id": self.agent_id,
                "patient_id": self.state["assigned_patient"],
                "hospital_id": self.state["assigned_hospital"]
            })
            self.state["status"] = "IDLE"
            self.state["assigned_patient"] = None
            self.state["assigned_hospital"] = None
            self.state["current_route"] = []
            self.state["route_index"] = 0

        return effects

    def assign_emergency(self, patient_id: str, patient_location: dict, priority: int = 1):
        self.state["status"] = "DISPATCHED"
        self.state["assigned_patient"] = patient_id
        self.state["priority"] = priority
        self.current_action = "DISPATCHED"
        self.send_message(
            patient_id, "AMBULANCE_ASSIGNED",
            f"Ambulance {self.agent_id} assigned to you",
            {"ambulance_id": self.agent_id}
        )

    def set_route_to_patient(self, route: List[List[int]]):
        self.state["current_route"] = route
        self.state["route_index"] = 0
        self.state["status"] = "EN_ROUTE_TO_PATIENT"
        self.state["replan_requested"] = False

    def set_route_to_hospital(self, hospital_id: str, route: List[List[int]]):
        self.state["assigned_hospital"] = hospital_id
        self.state["current_route"] = route
        self.state["route_index"] = 0
        self.state["status"] = "EN_ROUTE_TO_HOSPITAL"
        self.state["replan_requested"] = False

    def request_replan(self, reason: str):
        self.state["replan_requested"] = True
        self.send_message(
            "CoordinatorAgent", "REPLAN_REQUEST",
            f"Ambulance {self.agent_id} needs replanning: {reason}",
            {"ambulance_id": self.agent_id, "reason": reason}
        )

    def _move_along_route(self) -> bool:
        route = self.state["current_route"]
        idx = self.state["route_index"]
        if route and idx < len(route):
            self.state["current_location"] = {"row": route[idx][0], "col": route[idx][1]}
            self.state["route_index"] = idx + 1
            return True
        return False

    def _handle_message(self, msg: dict):
        if msg["type"] == "ROAD_BLOCKED":
            road_id = msg["data"].get("road_id")
            if road_id and self._is_road_in_current_route(road_id):
                self.request_replan(f"Road {road_id} is now blocked")
        elif msg["type"] == "HOSPITAL_UNAVAILABLE":
            hosp_id = msg["data"].get("hospital_id")
            if hosp_id == self.state.get("assigned_hospital"):
                self.request_replan(f"Hospital {hosp_id} is no longer available")

    def _is_road_in_current_route(self, road_id: str) -> bool:
        # Simplified check - in full system would check route segment road IDs
        return self.state["status"] in ("EN_ROUTE_TO_PATIENT", "EN_ROUTE_TO_HOSPITAL")
