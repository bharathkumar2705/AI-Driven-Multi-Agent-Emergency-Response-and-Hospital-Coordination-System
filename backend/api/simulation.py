from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from simulation.simulator import get_simulator
from simulation.seed_data import SCENARIO_DESCRIPTIONS
import asyncio

router = APIRouter()

class StartRequest(BaseModel):
    scenario: str = "scenario_1"

class EventRequest(BaseModel):
    event_type: str
    data: dict = {}

class PatientRequest(BaseModel):
    patient_id: str
    name: str
    location: dict
    emergency_type: str
    severity: str
    required_specialist: str
    required_resources: List[str] = []

@router.post("/simulation/start")
async def start_simulation(req: StartRequest):
    sim = get_simulator()
    await sim.start(req.scenario)
    return {"status": "started", "scenario": req.scenario}

@router.post("/simulation/pause")
async def pause_simulation():
    sim = get_simulator()
    await sim.pause()
    return {"status": "paused"}

@router.post("/simulation/resume")
async def resume_simulation():
    sim = get_simulator()
    await sim.resume()
    return {"status": "resumed"}

@router.post("/simulation/reset")
async def reset_simulation(req: StartRequest):
    sim = get_simulator()
    await sim.reset(req.scenario)
    return {"status": "reset", "scenario": req.scenario}

@router.get("/simulation/state")
def get_simulation_state():
    sim = get_simulator()
    return sim.get_full_state()

@router.post("/simulation/event")
async def inject_event(req: EventRequest):
    sim = get_simulator()
    result = await sim.inject_event(req.event_type, req.data)
    return result

@router.post("/simulation/emergency")
async def add_emergency(req: PatientRequest):
    sim = get_simulator()
    patient_data = req.model_dump()
    patient_data["status"] = "WAITING"
    await sim.inject_event("NEW_EMERGENCY", {"patient": patient_data})
    return {"status": "queued", "patient_id": req.patient_id}

@router.get("/simulation/scenarios")
def get_scenarios():
    return SCENARIO_DESCRIPTIONS

@router.get("/simulation/analytics")
def get_analytics():
    sim = get_simulator()
    return sim._get_analytics()
