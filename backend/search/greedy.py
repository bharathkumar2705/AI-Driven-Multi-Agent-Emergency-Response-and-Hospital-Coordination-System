"""Greedy Best-First Search - expands node with lowest heuristic h(n). Fast but not optimal."""
import heapq
import time
from typing import Tuple
from .graph import SearchGraph, SearchResult


def greedy(graph: SearchGraph, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    t0 = time.perf_counter()
    # heap ordered by heuristic h(n) only
    heap = [(graph.heuristic(start, goal), 0.0, start, [start])]
    visited = set()
    nodes_expanded = 0

    while heap:
        h, cost, node, path = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)
        nodes_expanded += 1

        if node == goal:
            return SearchResult("Greedy", start, goal, path, cost, nodes_expanded,
                                (time.perf_counter() - t0) * 1000, True)

        for neighbor, edge_cost, road_id in graph.neighbors(node):
            if neighbor not in visited:
                h_val = graph.heuristic(neighbor, goal)
                heapq.heappush(heap, (h_val, cost + edge_cost, neighbor, path + [neighbor]))

    return SearchResult("Greedy", start, goal, [], float('inf'), nodes_expanded,
                        (time.perf_counter() - t0) * 1000, False)
