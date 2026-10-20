from fastapi import APIRouter
from simulation.simulator import get_simulator

router = APIRouter()

@router.get("/patients")
def get_patients():
    sim = get_simulator()
    return [pa.state for pa in sim.patient_agents.values()]

@router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    sim = get_simulator()
    pa = sim.patient_agents.get(patient_id)
    if not pa:
        return {"error": "Not found"}
    return pa.state
