"""DFS - Uninformed search using a stack. May not find optimal path. Used for environment exploration."""
import time
from typing import Tuple
from .graph import SearchGraph, SearchResult


def dfs(graph: SearchGraph, start: Tuple[int, int], goal: Tuple[int, int],
        depth_limit: int = 50) -> SearchResult:
    t0 = time.perf_counter()
    stack = [(start, [start], 0)]
    visited = {start}
    nodes_expanded = 0

    while stack:
        node, path, depth = stack.pop()
        nodes_expanded += 1

        if node == goal:
            cost = sum(
                min(c for n, c, _ in graph.neighbors(path[i]) if n == path[i+1])
                for i in range(len(path) - 1)
            ) if len(path) > 1 else 0
            return SearchResult("DFS", start, goal, path, cost, nodes_expanded,
                                (time.perf_counter() - t0) * 1000, True)

        if depth < depth_limit:
            for neighbor, edge_cost, road_id in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor], depth + 1))

    return SearchResult("DFS", start, goal, [], float('inf'), nodes_expanded,
                        (time.perf_counter() - t0) * 1000, False)
