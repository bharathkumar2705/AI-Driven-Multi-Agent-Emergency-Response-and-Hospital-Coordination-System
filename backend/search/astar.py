"""
A* Search - combines path cost g(n) and heuristic h(n): f(n) = g(n) + h(n).
Optimal and complete when heuristic is admissible (never overestimates).
Heuristic: Manhattan distance, scaled by minimum possible edge cost (1.0).
"""
import heapq
import time
from typing import Tuple
from .graph import SearchGraph, SearchResult


def astar(graph: SearchGraph, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    t0 = time.perf_counter()

    h_start = graph.heuristic(start, goal)
    # heap: (f=g+h, g, node, path)
    heap = [(h_start, 0.0, start, [start])]
    g_cost = {start: 0.0}
    nodes_expanded = 0

    while heap:
        f, g, node, path = heapq.heappop(heap)

        if g > g_cost.get(node, float('inf')):
            continue  # stale entry
        nodes_expanded += 1

        if node == goal:
            return SearchResult("A*", start, goal, path, g, nodes_expanded,
                                (time.perf_counter() - t0) * 1000, True)

        for neighbor, edge_cost, road_id in graph.neighbors(node):
            new_g = g + edge_cost
            if new_g < g_cost.get(neighbor, float('inf')):
                g_cost[neighbor] = new_g
                h = graph.heuristic(neighbor, goal)
                heapq.heappush(heap, (new_g + h, new_g, neighbor, path + [neighbor]))

    return SearchResult("A*", start, goal, [], float('inf'), nodes_expanded,
                        (time.perf_counter() - t0) * 1000, False)
