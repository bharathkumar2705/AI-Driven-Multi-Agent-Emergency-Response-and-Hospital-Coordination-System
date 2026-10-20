"""BFS - Uninformed search, explores nodes level by level. Ignores edge costs."""
from collections import deque
import time
from typing import Tuple, Optional
from .graph import SearchGraph, SearchResult


def bfs(graph: SearchGraph, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    t0 = time.perf_counter()
    frontier = deque([(start, [start])])
    visited = {start}
    nodes_expanded = 0

    while frontier:
        node, path = frontier.popleft()
        nodes_expanded += 1

        if node == goal:
            cost = sum(
                min(c for n, c, _ in graph.neighbors(path[i]) if n == path[i+1])
                for i in range(len(path) - 1)
            ) if len(path) > 1 else 0
            return SearchResult("BFS", start, goal, path, float(cost), nodes_expanded,
                                (time.perf_counter() - t0) * 1000, True)

        for neighbor, edge_cost, road_id in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append((neighbor, path + [neighbor]))

    return SearchResult("BFS", start, goal, [], float('inf'), nodes_expanded,
                        (time.perf_counter() - t0) * 1000, False)
