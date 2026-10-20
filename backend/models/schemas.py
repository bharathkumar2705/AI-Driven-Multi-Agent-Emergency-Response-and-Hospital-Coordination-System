"""Pydantic v2 schemas for all domain entities."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class Severity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RoadState(str, Enum):
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    CONGESTED = "CONGESTED"
    BLOCKED = "BLOCKED"


class AmbulanceStatus(str, Enum):
    IDLE = "IDLE"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE_TO_PATIENT = "EN_ROUTE_TO_PATIENT"
    PATIENT_PICKED_UP = "PATIENT_PICKED_UP"
    EN_ROUTE_TO_HOSPITAL = "EN_ROUTE_TO_HOSPITAL"
    ARRIVED = "ARRIVED"


class PatientStatus(str, Enum):
    WAITING = "WAITING"
    EMERGENCY_GENERATED = "EMERGENCY_GENERATED"
    AMBULANCE_ASSIGNED = "AMBULANCE_ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ARRIVED = "ARRIVED"
    TREATED = "TREATED"


class EmergencyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GridPosition(BaseModel):
    row: int
    col: int


class SearchRequest(BaseModel):
    algorithm: str
    start: List[int]
    goal: List[int]


class EventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any] = {}


class StartRequest(BaseModel):
    scenario: str = "scenario_1"


class BackwardChainRequest(BaseModel):
    hospital_id: str
    patient_id: str


class FactRequest(BaseModel):
    predicate: str
    args: Dict[str, str] = {}


class PatientRequest(BaseModel):
    patient_id: str
    name: str
    location: Dict[str, int]
    emergency_type: str
    severity: str
    required_specialist: str
    required_resources: List[str] = []
