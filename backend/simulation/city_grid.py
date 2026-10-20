"""
City represented as a 10x10 grid graph.
Nodes are (row, col) tuples. Edges are road segments with costs.
"""
from typing import Dict, List, Tuple, Optional
import math

GRID_SIZE = 10

# Road state cost multipliers
STATE_MULTIPLIER = {
    "NORMAL": 1.0,
    "MODERATE": 1.5,
    "CONGESTED": 2.5,
    "BLOCKED": float('inf')
}


class CityGraph:
    def __init__(self):
        self.nodes: List[Tuple[int, int]] = []
        self.edges: Dict[str, dict] = {}          # road_id -> edge info
        self.adjacency: Dict[Tuple, List[dict]] = {}  # node -> list of {neighbor, road_id, cost}
        self.road_states: Dict[str, str] = {}     # road_id -> state string
        self._build_grid()

    def _build_grid(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                node = (r, c)
                self.nodes.append(node)
                self.adjacency[node] = []

        # Predefined varied road costs so algorithms produce different metrics.
        # Pattern: simulates realistic city where highways (low cost) vs side streets (high cost)
        VARIED_COSTS = [1.0, 1.5, 2.0, 1.0, 3.0, 1.0, 2.5, 1.5, 1.0, 2.0,
                        1.5, 1.0, 1.0, 2.0, 1.5, 3.0, 1.0, 1.0, 2.5, 1.0]

        edge_count = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Horizontal edge
                if c + 1 < GRID_SIZE:
                    road_id = f"R{edge_count:03d}"
                    base_cost = VARIED_COSTS[(r * GRID_SIZE + c) % len(VARIED_COSTS)]
                    self._add_edge(road_id, (r, c), (r, c+1), base_cost)
                    edge_count += 1
                # Vertical edge
                if r + 1 < GRID_SIZE:
                    road_id = f"R{edge_count:03d}"
                    base_cost = VARIED_COSTS[(r * GRID_SIZE + c + 5) % len(VARIED_COSTS)]
                    self._add_edge(road_id, (r, c), (r+1, c), base_cost)
                    edge_count += 1

    def _add_edge(self, road_id: str, n1: Tuple, n2: Tuple, base_cost: float):
        self.edges[road_id] = {
            "road_id": road_id,
            "from_node": list(n1),
            "to_node": list(n2),
            "base_cost": base_cost,
            "state": "NORMAL"
        }
        self.road_states[road_id] = "NORMAL"
        self.adjacency[n1].append({"neighbor": n2, "road_id": road_id, "base_cost": base_cost})
        self.adjacency[n2].append({"neighbor": n1, "road_id": road_id, "base_cost": base_cost})

    def get_edge_cost(self, road_id: str) -> float:
        edge = self.edges[road_id]
        mult = STATE_MULTIPLIER.get(edge["state"], 1.0)
        if mult == float('inf'):
            return float('inf')
        return edge["base_cost"] * mult

    def get_neighbors(self, node: Tuple[int, int]) -> List[dict]:
        result = []
        for adj in self.adjacency.get(node, []):
            cost = self.get_edge_cost(adj["road_id"])
            result.append({
                "neighbor": adj["neighbor"],
                "road_id": adj["road_id"],
                "cost": cost
            })
        return result

    def set_road_state(self, road_id: str, state: str):
        if road_id in self.edges:
            self.edges[road_id]["state"] = state
            self.road_states[road_id] = state

    def get_road_by_nodes(self, n1: Tuple, n2: Tuple) -> Optional[str]:
        for adj in self.adjacency.get(n1, []):
            if adj["neighbor"] == n2:
                return adj["road_id"]
        return None

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        # Manhattan distance as baseline heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def to_dict(self) -> dict:
        return {
            "grid_size": GRID_SIZE,
            "edges": list(self.edges.values()),
            "road_states": self.road_states
        }


# Singleton city graph shared across all agents
_city_graph: Optional[CityGraph] = None

def get_city_graph() -> CityGraph:
    global _city_graph
    if _city_graph is None:
        _city_graph = CityGraph()
    return _city_graph

def reset_city_graph():
    global _city_graph
    _city_graph = CityGraph()
    return _city_graph
