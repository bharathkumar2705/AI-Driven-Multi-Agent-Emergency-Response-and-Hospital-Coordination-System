from fastapi import APIRouter
from simulation.simulator import get_simulator

router = APIRouter()

@router.get("/ambulances")
def get_ambulances():
    sim = get_simulator()
    return [aa.state for aa in sim.ambulance_agents.values()]

@router.get("/ambulances/{ambulance_id}")
def get_ambulance(ambulance_id: str):
    sim = get_simulator()
    aa = sim.ambulance_agents.get(ambulance_id)
    if not aa:
        return {"error": "Not found"}
    return aa.state
