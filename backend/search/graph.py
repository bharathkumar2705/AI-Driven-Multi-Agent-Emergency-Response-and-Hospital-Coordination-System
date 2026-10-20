"""Generic graph interface used by all search algorithms."""
from typing import Tuple, List, Dict, Any, Optional, Callable


class SearchGraph:
    """
    Adapter that wraps CityGraph for use by search algorithms.
    All algorithms receive a SearchGraph and work uniformly.
    """

    def __init__(self, city_graph, blocked_roads: set = None):
        self._city = city_graph
        self._blocked = blocked_roads or set()

    def neighbors(self, node: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float, str]]:
        """Return [(neighbor_node, cost, road_id), ...]"""
        result = []
        for adj in self._city.get_neighbors(node):
            if adj["road_id"] in self._blocked:
                continue
            if adj["cost"] == float('inf'):
                continue
            result.append((adj["neighbor"], adj["cost"], adj["road_id"]))
        return result

    def heuristic(self, node: Tuple[int, int], goal: Tuple[int, int]) -> float:
        return self._city.heuristic(node, goal)

    def all_nodes(self):
        return self._city.nodes


class SearchResult:
    def __init__(self, algorithm: str, start, goal, path, cost, nodes_expanded, exec_time_ms, success):
        self.algorithm = algorithm
        self.start = start
        self.goal = goal
        self.path = path
        self.cost = cost
        self.nodes_expanded = nodes_expanded
        self.execution_time_ms = exec_time_ms
        self.success = success

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "start": list(self.start),
            "goal": list(self.goal),
            "path": [list(p) for p in self.path],
            "cost": self.cost,
            "nodes_expanded": self.nodes_expanded,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "success": self.success
        }
