"""
Emergency Planning Engine.
Creates a sequential 11-step plan for each emergency.
Monitors plan validity and triggers replanning when the environment changes.
"""
from typing import List, Optional, Dict, Any
import uuid
import datetime


PLAN_STEPS_TEMPLATE = [
    "Detect emergency",
    "Determine priority",
    "Assign ambulance",
    "Dispatch ambulance to patient",
    "Evaluate hospitals",
    "Select optimal hospital",
    "Calculate route to hospital",
    "Transport patient",
    "Assign doctor",
    "Reserve resources",
    "Complete treatment"
]


class PlanStep:
    def __init__(self, number: int, description: str):
        self.step_number = number
        self.description = description
        self.status = "PENDING"   # PENDING | IN_PROGRESS | COMPLETED | FAILED
        self.details: Optional[str] = None
        self.timestamp: Optional[str] = None

    def start(self, details: str = None):
        self.status = "IN_PROGRESS"
        self.details = details
        self.timestamp = _now()

    def complete(self, details: str = None):
        self.status = "COMPLETED"
        if details:
            self.details = details
        self.timestamp = _now()

    def fail(self, reason: str):
        self.status = "FAILED"
        self.details = reason
        self.timestamp = _now()

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "description": self.description,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp
        }


class EmergencyPlan:
    def __init__(self, emergency_id: str, patient_id: str):
        self.plan_id = str(uuid.uuid4())[:8]
        self.emergency_id = emergency_id
        self.patient_id = patient_id
        self.version = 1
        self.status = "ACTIVE"   # ACTIVE | INVALID | COMPLETED
        self.steps: List[PlanStep] = [
            PlanStep(i+1, desc) for i, desc in enumerate(PLAN_STEPS_TEMPLATE)
        ]
        self.current_step_index = 0
        self.selected_hospital: Optional[str] = None
        self.selected_ambulance: Optional[str] = None
        self.route: List[List[int]] = []
        self.invalidation_reason: Optional[str] = None
        self.created_at = _now()
        self.events: List[dict] = []

    @property
    def current_step(self) -> Optional[PlanStep]:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self, details: str = None):
        """Complete current step and move to next."""
        if self.current_step:
            self.current_step.complete(details)
            self.current_step_index += 1
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index].start()

    def start_current(self, details: str = None):
        if self.current_step:
            self.current_step.start(details)

    def invalidate(self, reason: str) -> 'EmergencyPlan':
        """Invalidate this plan and return a new one."""
        self.status = "INVALID"
        self.invalidation_reason = reason
        self.events.append({
            "type": "PLAN_INVALIDATED",
            "reason": reason,
            "timestamp": _now(),
            "old_plan_id": self.plan_id,
            "old_version": self.version
        })
        return self

    def create_new_version(self) -> 'EmergencyPlan':
        """Create a new plan version after invalidation."""
        new_plan = EmergencyPlan(self.emergency_id, self.patient_id)
        new_plan.version = self.version + 1
        new_plan.plan_id = self.plan_id  # keep same ID, different version
        # Resume from step 5 (evaluate hospitals) since ambulance may already be dispatched
        for i in range(4):
            new_plan.steps[i].complete(f"Carried over from plan v{self.version}")
        new_plan.current_step_index = 4
        new_plan.steps[4].start()
        new_plan.selected_ambulance = self.selected_ambulance
        new_plan.events = list(self.events)
        new_plan.events.append({
            "type": "NEW_PLAN_GENERATED",
            "timestamp": _now(),
            "version": new_plan.version
        })
        return new_plan

    def complete(self):
        self.status = "COMPLETED"
        for step in self.steps:
            if step.status == "PENDING":
                step.complete("Auto-completed")

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "emergency_id": self.emergency_id,
            "patient_id": self.patient_id,
            "version": self.version,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "current_step_index": self.current_step_index,
            "selected_hospital": self.selected_hospital,
            "selected_ambulance": self.selected_ambulance,
            "route": self.route,
            "invalidation_reason": self.invalidation_reason,
            "created_at": self.created_at,
            "events": self.events
        }


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")
