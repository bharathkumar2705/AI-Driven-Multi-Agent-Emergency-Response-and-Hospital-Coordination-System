"""
Patient Agent - represents an emergency patient.

PEAS:
  Performance: Emergency handled quickly with correct specialist
  Environment: City grid, hospitals, ambulances
  Actuators: Generate emergency request, update condition
  Sensors: Own location, severity level, available ambulances
"""
from .base_agent import BaseAgent
from typing import Dict, Any, List
import uuid, datetime


class PatientAgent(BaseAgent):
    def __init__(self, patient_data: dict):
        super().__init__(patient_data["patient_id"], "PatientAgent")
        self.goal = "Receive emergency medical treatment as fast as possible"
        self.state = {
            "patient_id": patient_data["patient_id"],
            "name": patient_data.get("name", "Unknown"),
            "location": patient_data["location"],
            "emergency_type": patient_data.get("emergency_type", "GENERAL"),
            "severity": patient_data.get("severity", "MODERATE"),
            "required_specialist": patient_data.get("required_specialist", ""),
            "required_resources": patient_data.get("required_resources", []),
            "status": patient_data.get("status", "WAITING"),
            "assigned_ambulance": None,
            "assigned_hospital": None,
        }
        self.knowledge = {
            "my_severity": self.state["severity"],
            "my_requirements": self.state["required_resources"],
            "emergency_generated": False
        }

    def sense(self, environment: dict):
        # Patient senses its own current status from the environment
        for p in environment.get("patients", []):
            if p["patient_id"] == self.agent_id:
                self.state["status"] = p.get("status", self.state["status"])

    def decide(self) -> str:
        if self.state["status"] == "WAITING":
            return "GENERATE_EMERGENCY"
        elif self.state["status"] == "EMERGENCY_GENERATED":
            return "WAIT_FOR_AMBULANCE"
        elif self.state["status"] == "AMBULANCE_ASSIGNED":
            return "WAIT_FOR_PICKUP"
        return "IDLE"

    def act(self, environment: dict) -> List[dict]:
        action = self.decide()
        effects = []
        self.current_action = action

        if action == "GENERATE_EMERGENCY" and not self.knowledge["emergency_generated"]:
            self.state["status"] = "EMERGENCY_GENERATED"
            self.knowledge["emergency_generated"] = True
            self.send_message(
                "AmbulanceDispatcher",
                "EMERGENCY_REQUEST",
                f"Emergency {self.agent_id}: {self.state['severity']} {self.state['emergency_type']}",
                {
                    "patient_id": self.agent_id,
                    "location": self.state["location"],
                    "severity": self.state["severity"],
                    "required_specialist": self.state["required_specialist"],
                    "required_resources": self.state["required_resources"]
                }
            )
            effects.append({"type": "EMERGENCY_GENERATED", "patient_id": self.agent_id})
        return effects

    def _handle_message(self, msg: dict):
        if msg["type"] == "AMBULANCE_ASSIGNED":
            self.state["status"] = "AMBULANCE_ASSIGNED"
            self.state["assigned_ambulance"] = msg["data"].get("ambulance_id")
            self.knowledge["assigned_ambulance"] = self.state["assigned_ambulance"]
        elif msg["type"] == "EN_ROUTE":
            self.state["status"] = "EN_ROUTE"
        elif msg["type"] == "ARRIVED_AT_HOSPITAL":
            self.state["status"] = "ARRIVED"
            self.state["assigned_hospital"] = msg["data"].get("hospital_id")
