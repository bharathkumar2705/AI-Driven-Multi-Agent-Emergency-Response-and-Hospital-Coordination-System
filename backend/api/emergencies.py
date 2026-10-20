from fastapi import APIRouter
from simulation.simulator import get_simulator

router = APIRouter()

@router.get("/emergencies")
def get_emergencies():
    sim = get_simulator()
    return list(sim.emergencies.values())

@router.get("/emergencies/{emergency_id}")
def get_emergency(emergency_id: str):
    sim = get_simulator()
    e = sim.emergencies.get(emergency_id)
    if not e:
        return {"error": "Not found"}
    return e

@router.get("/emergencies/{emergency_id}/plan")
def get_emergency_plan(emergency_id: str):
    sim = get_simulator()
    plan = sim.plans.get(emergency_id)
    if not plan:
        return {"error": "No plan found"}
    return plan.to_dict()
