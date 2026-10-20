from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from simulation.simulator import get_simulator
from search.graph import SearchGraph
from search.bfs import bfs
from search.dfs import dfs
from search.ucs import ucs
from search.greedy import greedy
from search.astar import astar
from simulation.city_grid import get_city_graph

router = APIRouter()

class SearchRequest(BaseModel):
    algorithm: str
    start: List[int]
    goal: List[int]

ALGO_MAP = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "greedy": greedy, "astar": astar}

@router.post("/search/run")
def run_search(req: SearchRequest):
    sim = get_simulator()
    cg = sim.city_graph if sim._initialized else get_city_graph()
    sg = SearchGraph(cg)
    fn = ALGO_MAP.get(req.algorithm, astar)
    result = fn(sg, tuple(req.start), tuple(req.goal))
    return result.to_dict()

@router.post("/search/compare")
def compare_all(req: SearchRequest):
    sim = get_simulator()
    cg = sim.city_graph if sim._initialized else get_city_graph()
    sg = SearchGraph(cg)
    s, g = tuple(req.start), tuple(req.goal)
    results = {}
    for name, fn in ALGO_MAP.items():
        r = fn(sg, s, g)
        results[name] = r.to_dict()
    return results

@router.get("/search/graph")
def get_graph():
    sim = get_simulator()
    cg = sim.city_graph if sim._initialized else get_city_graph()
    return cg.to_dict()
