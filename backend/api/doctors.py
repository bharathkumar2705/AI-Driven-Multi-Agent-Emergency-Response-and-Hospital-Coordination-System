from fastapi import APIRouter
from simulation.simulator import get_simulator

router = APIRouter()

@router.get("/doctors")
def get_doctors():
    sim = get_simulator()
    return [da.state for da in sim.doctor_agents.values()]

@router.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    sim = get_simulator()
    da = sim.doctor_agents.get(doctor_id)
    if not da:
        return {"error": "Not found"}
    return da.state
