from fastapi import APIRouter
from simulation.simulator import get_simulator

router = APIRouter()

@router.get("/roads")
def get_roads():
    sim = get_simulator()
    if sim.traffic_agent:
        return sim.traffic_agent.get_all_roads_for_ui()
    return []

@router.get("/roads/states")
def get_road_states():
    sim = get_simulator()
    if sim.traffic_agent:
        return sim.traffic_agent.get_road_states()
    return {}
