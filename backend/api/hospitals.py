from fastapi import APIRouter
from simulation.simulator import get_simulator
from simulation.seed_data import SCENARIO_DESCRIPTIONS

router = APIRouter()

@router.get("/hospitals")
def get_hospitals():
    sim = get_simulator()
    return [ha.state for ha in sim.hospital_agents.values()]

@router.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    sim = get_simulator()
    ha = sim.hospital_agents.get(hospital_id)
    if not ha:
        return {"error": "Hospital not found"}
    return ha.state

@router.get("/hospitals/{hospital_id}/availability")
def get_hospital_availability(hospital_id: str):
    sim = get_simulator()
    ha = sim.hospital_agents.get(hospital_id)
    if not ha:
        return {"error": "Not found"}
    return ha.report_availability()
