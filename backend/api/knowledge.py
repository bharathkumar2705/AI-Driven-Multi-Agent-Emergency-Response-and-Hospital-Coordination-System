from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from simulation.simulator import get_simulator
from knowledge.knowledge_base import get_knowledge_base
from reasoning.forward_chaining import forward_chain
from reasoning.backward_chaining import can_hospital_treat_patient

router = APIRouter()

class BackwardChainRequest(BaseModel):
    hospital_id: str
    patient_id: str

class FactRequest(BaseModel):
    predicate: str
    args: dict = {}

@router.get("/knowledge/snapshot")
def get_snapshot():
    sim = get_simulator()
    return sim.get_knowledge_snapshot()

@router.get("/knowledge/facts")
def get_facts():
    kb = get_knowledge_base()
    return kb.get_all_facts()

@router.get("/knowledge/rules")
def get_rules():
    kb = get_knowledge_base()
    return kb.get_rules()

@router.post("/knowledge/forward-chain")
def run_forward_chain():
    sim = get_simulator()
    kb = get_knowledge_base()
    # Load current state into KB
    kb.reset_derived_facts()
    for ha in sim.hospital_agents.values():
        kb.load_hospital_facts(ha.state)
    for da in sim.doctor_agents.values():
        kb.load_doctor_facts(da.state)
    derivations = forward_chain(kb)
    return {
        "derivations": [d.to_dict() for d in derivations],
        "new_facts_count": len(derivations)
    }

@router.post("/knowledge/backward-chain")
def run_backward_chain(req: BackwardChainRequest):
    kb = get_knowledge_base()
    result = can_hospital_treat_patient(req.hospital_id, req.patient_id, kb)
    return result.to_dict()

@router.post("/knowledge/assert")
def assert_fact(req: FactRequest):
    kb = get_knowledge_base()
    kb.assert_fact(req.predicate, **req.args)
    return {"status": "asserted", "fact": req.predicate}
