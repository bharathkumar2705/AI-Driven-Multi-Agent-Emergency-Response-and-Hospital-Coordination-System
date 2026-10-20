from fastapi import APIRouter
from simulation.simulator import get_simulator
from communication.message_bus import get_message_bus

router = APIRouter()

@router.get("/agents")
def get_all_agents():
    sim = get_simulator()
    agents = []
    for a in sim._all_agents():
        agents.append(a.to_dict())
    return agents

@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    sim = get_simulator()
    for a in sim._all_agents():
        if a.agent_id == agent_id:
            return a.to_dict()
    return {"error": "Agent not found"}

@router.get("/agents/messages/all")
def get_all_messages(limit: int = 100):
    bus = get_message_bus()
    return bus.get_all_messages(limit)

@router.get("/agents/messages/count")
def get_message_count():
    bus = get_message_bus()
    return {"count": bus.get_message_count()}
