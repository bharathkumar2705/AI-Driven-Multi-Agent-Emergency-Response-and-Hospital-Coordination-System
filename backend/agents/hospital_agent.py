"""
Hospital Agent - manages hospital resources and communicates availability.

PEAS:
  Performance: Maximise treated patients; maintain resource availability reporting
  Environment: Hospital building, patients, doctors
  Actuators: Accept/reject patient, reserve bed/ICU, update resource status
  Sensors: Current bed count, ICU count, specialist availability, incoming requests
"""
from .base_agent import BaseAgent
from typing import List


class HospitalAgent(BaseAgent):
    def __init__(self, hospital_data: dict):
        super().__init__(hospital_data["hospital_id"], "HospitalAgent")
        self.goal = "Provide accurate resource availability and accept appropriate patients"
        self.state = dict(hospital_data)
        self.state["reserved_for"] = []   # list of patient_ids with reservations
        self.knowledge = {
            "pending_requests": [],
            "accepted_patients": []
        }

    def sense(self, environment: dict):
        pass  # Hospital state is updated by the simulator directly

    def decide(self) -> str:
        if self.knowledge["pending_requests"]:
            return "EVALUATE_REQUEST"
        return "REPORT_AVAILABILITY"

    def act(self, environment: dict) -> List[dict]:
        action = self.decide()
        self.current_action = action
        effects = []

        if action == "EVALUATE_REQUEST":
            req = self.knowledge["pending_requests"].pop(0)
            result = self._evaluate_patient_request(req)
            effects.append(result)

        return effects

    def _evaluate_patient_request(self, request: dict) -> dict:
        patient_id = request.get("patient_id", "")
        needs_icu = "ICU" in request.get("required_resources", [])
        can_accept = self.state.get("available_beds", 0) > 0
        if needs_icu and self.state.get("icu_available", 0) == 0:
            can_accept = False

        if can_accept:
            return {"type": "PATIENT_ACCEPTED", "hospital_id": self.agent_id, "patient_id": patient_id}
        else:
            reason = "ICU full" if needs_icu else "No beds"
            return {"type": "PATIENT_REJECTED", "hospital_id": self.agent_id,
                    "patient_id": patient_id, "reason": reason}

    def reserve_bed(self, patient_id: str, needs_icu: bool = False) -> bool:
        if self.state.get("available_beds", 0) <= 0:
            return False
        if needs_icu and self.state.get("icu_available", 0) <= 0:
            return False
        self.state["available_beds"] = max(0, self.state["available_beds"] - 1)
        if needs_icu:
            self.state["icu_available"] = max(0, self.state["icu_available"] - 1)
        self.state["reserved_for"].append(patient_id)
        self.knowledge["accepted_patients"].append(patient_id)
        self.send_message(
            "CoordinatorAgent", "BED_RESERVED",
            f"Hospital {self.agent_id} reserved bed for {patient_id}",
            {"hospital_id": self.agent_id, "patient_id": patient_id, "icu": needs_icu}
        )
        return True

    def set_icu_available(self, count: int):
        self.state["icu_available"] = count
        if count == 0:
            self.send_message(
                "CoordinatorAgent", "ICU_UNAVAILABLE",
                f"Hospital {self.agent_id} ICU is now full",
                {"hospital_id": self.agent_id}
            )

    def set_specialist_unavailable(self, specialization: str):
        specs = self.state.get("available_specialists", [])
        if specialization in specs:
            specs.remove(specialization)
        self.send_message(
            "CoordinatorAgent", "SPECIALIST_UNAVAILABLE",
            f"Hospital {self.agent_id}: {specialization} is unavailable",
            {"hospital_id": self.agent_id, "specialization": specialization}
        )

    def report_availability(self) -> dict:
        return {
            "hospital_id": self.agent_id,
            "name": self.state.get("name", self.agent_id),
            "available_beds": self.state.get("available_beds", 0),
            "icu_available": self.state.get("icu_available", 0),
            "available_specialists": self.state.get("available_specialists", []),
            "status": self.state.get("status", "OPERATIONAL")
        }

    def _handle_message(self, msg: dict):
        if msg["type"] == "AVAILABILITY_REQUEST":
            self.knowledge["pending_requests"].append(msg["data"])
