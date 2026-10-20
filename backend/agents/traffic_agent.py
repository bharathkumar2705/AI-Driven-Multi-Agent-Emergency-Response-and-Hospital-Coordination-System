"""
Traffic Agent - monitors and updates road conditions across the city.

PEAS:
  Performance: Maintain accurate real-time road condition data for all agents
  Environment: City road network (grid graph)
  Actuators: Update road states, broadcast congestion alerts
  Sensors: Road sensors, incident reports
"""
from .base_agent import BaseAgent
from typing import List
import random


class TrafficAgent(BaseAgent):
    def __init__(self, city_graph):
        super().__init__("TrafficAgent", "TrafficAgent")
        self.goal = "Maintain accurate road condition data and alert affected agents"
        self._graph = city_graph
        self.state = {
            "monitored_roads": len(city_graph.edges),
            "congested_roads": [],
            "blocked_roads": [],
            "incidents": []
        }
        self.knowledge = {
            "road_states": dict(city_graph.road_states)
        }

    def sense(self, environment: dict):
        self.knowledge["road_states"] = dict(self._graph.road_states)
        self.state["congested_roads"] = [
            rid for rid, s in self.knowledge["road_states"].items()
            if s in ("CONGESTED", "BLOCKED")
        ]

    def decide(self) -> str:
        return "MONITOR_AND_BROADCAST"

    def act(self, environment: dict) -> List[dict]:
        self.current_action = "MONITORING"
        return []  # Traffic changes are injected via events, not auto-generated

    def set_road_state(self, road_id: str, state: str) -> dict:
        """Inject a road condition change."""
        old_state = self._graph.road_states.get(road_id, "NORMAL")
        self._graph.set_road_state(road_id, state)
        self.knowledge["road_states"][road_id] = state

        incident = {
            "road_id": road_id,
            "old_state": old_state,
            "new_state": state
        }
        self.state["incidents"].append(incident)

        msg_type = "ROAD_CONGESTED" if state == "CONGESTED" else \
                   "ROAD_BLOCKED" if state == "BLOCKED" else "ROAD_CLEARED"

        self.send_message(
            "ALL_AMBULANCES", msg_type,
            f"Road {road_id}: {old_state} → {state}",
            {"road_id": road_id, "old_state": old_state, "new_state": state}
        )
        self.send_message(
            "CoordinatorAgent", msg_type,
            f"Traffic update: Road {road_id} is now {state}",
            {"road_id": road_id, "new_state": state}
        )
        return incident

    def get_road_states(self) -> dict:
        return dict(self.knowledge["road_states"])

    def get_all_roads_for_ui(self) -> List[dict]:
        roads = []
        for rid, edge in self._graph.edges.items():
            roads.append({
                "road_id": rid,
                "from_node": edge["from_node"],
                "to_node": edge["to_node"],
                "state": edge["state"],
                "base_cost": edge["base_cost"]
            })
        return roads
