"""
Doctor Agent - manages doctor availability and patient assignments.

PEAS:
  Performance: Treat assigned patients; maintain accurate availability status
  Environment: Hospital, patient list
  Actuators: Accept/reject patient, become busy/available
  Sensors: Own availability, current patient workload
"""
from .base_agent import BaseAgent
from typing import List, Optional


class DoctorAgent(BaseAgent):
    def __init__(self, doctor_data: dict):
        super().__init__(doctor_data["doctor_id"], "DoctorAgent")
        self.goal = "Treat patients matching my specialization when available"
        self.state = {
            "doctor_id": self.agent_id,
            "name": doctor_data.get("name", "Dr. Unknown"),
            "specialization": doctor_data.get("specialization", "General"),
            "hospital_id": doctor_data.get("hospital_id", ""),
            "availability": doctor_data.get("availability", True),
            "current_patient": doctor_data.get("current_patient", None)
        }
        self.knowledge = {
            "patients_treated": 0,
            "pending_assignments": []
        }

    def sense(self, environment: dict):
        pass  # Doctors sense incoming assignments via messages

    def decide(self) -> str:
        if self.knowledge["pending_assignments"] and self.state["availability"]:
            return "ACCEPT_PATIENT"
        if self.state["availability"]:
            return "REPORT_AVAILABLE"
        return "TREATING_PATIENT"

    def act(self, environment: dict) -> List[dict]:
        action = self.decide()
        self.current_action = action
        effects = []

        if action == "ACCEPT_PATIENT" and self.knowledge["pending_assignments"]:
            patient_id = self.knowledge["pending_assignments"].pop(0)
            self.state["availability"] = False
            self.state["current_patient"] = patient_id
            self.knowledge["patients_treated"] += 1
            self.send_message(
                "CoordinatorAgent", "DOCTOR_ASSIGNED",
                f"Dr. {self.state['name']} assigned to {patient_id}",
                {"doctor_id": self.agent_id, "patient_id": patient_id,
                 "specialization": self.state["specialization"]}
            )
            effects.append({"type": "DOCTOR_ASSIGNED", "doctor_id": self.agent_id, "patient_id": patient_id})

        return effects

    def assign_patient(self, patient_id: str):
        if self.state["availability"]:
            self.knowledge["pending_assignments"].append(patient_id)

    def become_available(self):
        self.state["availability"] = True
        self.state["current_patient"] = None
        self.send_message(
            "CoordinatorAgent", "DOCTOR_AVAILABLE",
            f"Dr. {self.state['name']} is now available",
            {"doctor_id": self.agent_id, "specialization": self.state["specialization"]}
        )

    def become_unavailable(self, reason: str = "Off duty"):
        self.state["availability"] = False
        self.send_message(
            "CoordinatorAgent", "DOCTOR_UNAVAILABLE",
            f"Dr. {self.state['name']} is unavailable: {reason}",
            {"doctor_id": self.agent_id, "reason": reason,
             "specialization": self.state["specialization"]}
        )

    def _handle_message(self, msg: dict):
        if msg["type"] == "PATIENT_ASSIGNMENT":
            self.assign_patient(msg["data"].get("patient_id"))
        elif msg["type"] == "BECOME_UNAVAILABLE":
            self.become_unavailable(msg["data"].get("reason", ""))
