"""UCS - Expands lowest path cost first. Optimal when edges have different costs."""
import heapq
import time
from typing import Tuple
from .graph import SearchGraph, SearchResult


def ucs(graph: SearchGraph, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    t0 = time.perf_counter()
    # heap entries: (cumulative_cost, node, path)
    heap = [(0.0, start, [start])]
    visited = {}
    nodes_expanded = 0

    while heap:
        cost, node, path = heapq.heappop(heap)

        if node in visited:
            continue
        visited[node] = cost
        nodes_expanded += 1

        if node == goal:
            return SearchResult("UCS", start, goal, path, cost, nodes_expanded,
                                (time.perf_counter() - t0) * 1000, True)

        for neighbor, edge_cost, road_id in graph.neighbors(node):
            if neighbor not in visited:
                new_cost = cost + edge_cost
                heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))

    return SearchResult("UCS", start, goal, [], float('inf'), nodes_expanded,
                        (time.perf_counter() - t0) * 1000, False)
