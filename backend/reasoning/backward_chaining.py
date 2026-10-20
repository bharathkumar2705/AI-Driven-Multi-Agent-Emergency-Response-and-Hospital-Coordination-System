"""
Backward Chaining Inference Engine.
Goal-directed: starts from the goal and works backwards through rules to prove it from facts.
Returns a proof tree with each step visible for UI display.
"""
from typing import List, Dict, Optional, Any
from knowledge.knowledge_base import KnowledgeBase


class ProofStep:
    def __init__(self, goal: str, result: str, method: str, children: List['ProofStep'] = None):
        self.goal = goal
        self.result = result   # "PROVED" | "FAILED" | "FACT"
        self.method = method   # "DIRECT_FACT" | "RULE:<rule_id>" | "NOT_FOUND"
        self.children = children or []

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "result": self.result,
            "method": self.method,
            "children": [c.to_dict() for c in self.children]
        }


class ProofResult:
    def __init__(self, goal: str, proved: bool, steps: ProofStep):
        self.goal = goal
        self.proved = proved
        self.steps = steps

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "proved": self.proved,
            "proof_tree": self.steps.to_dict()
        }


def backward_chain(goal_predicate: str, goal_args: Dict, kb: KnowledgeBase,
                   depth: int = 0, max_depth: int = 10) -> ProofStep:
    """
    Recursively prove a goal using backward chaining.
    First checks direct facts, then tries rules whose conclusion matches the goal.
    """
    goal_str = _make_goal_str(goal_predicate, goal_args)

    if depth > max_depth:
        return ProofStep(goal_str, "FAILED", "MAX_DEPTH_EXCEEDED")

    # Check if goal is directly in the KB as a fact
    if kb.query(goal_predicate, **goal_args):
        return ProofStep(goal_str, "PROVED", "DIRECT_FACT")

    # Try to prove via rules whose conclusion matches this goal
    for rule in kb.rules:
        bindings = _match_conclusion(rule.conclusion, goal_predicate, goal_args)
        if bindings is None:
            continue

        # Try to prove all conditions of this rule
        child_steps = []
        all_proved = True
        for condition in rule.conditions:
            cond_pred, cond_vars = _extract_pred_and_vars(condition)
            cond_args = _instantiate_args(cond_vars, bindings)
            child = backward_chain(cond_pred, cond_args, kb, depth + 1, max_depth)
            child_steps.append(child)
            if child.result != "PROVED":
                all_proved = False
                break

        if all_proved:
            return ProofStep(goal_str, "PROVED", f"RULE:{rule.rule_id}", child_steps)

    return ProofStep(goal_str, "FAILED", "NOT_FOUND")


def can_hospital_treat_patient(hospital_id: str, patient_id: str, kb: KnowledgeBase) -> ProofResult:
    """High-level query: Can hospital H treat patient P?"""
    goal_predicate = "hospital_eligible_for_patient"
    goal_args = {"hospital": hospital_id, "patient": patient_id}
    step = backward_chain(goal_predicate, goal_args, kb)
    return ProofResult(f"Can {hospital_id} treat {patient_id}?", step.result == "PROVED", step)


def _make_goal_str(pred: str, args: dict) -> str:
    arg_str = ",".join(f"{k}={v}" for k, v in sorted(args.items()))
    return f"{pred}({arg_str})"


def _match_conclusion(conclusion_pattern: str, target_pred: str, target_args: Dict) -> Optional[Dict]:
    """Try to unify conclusion_pattern with target. Returns bindings if successful."""
    if '(' not in conclusion_pattern:
        if conclusion_pattern == target_pred:
            return {}
        return None

    pred = conclusion_pattern[:conclusion_pattern.index('(')]
    if pred != target_pred:
        return None

    inner = conclusion_pattern[conclusion_pattern.index('(')+1:conclusion_pattern.rindex(')')]
    bindings = {}
    for part in inner.split(','):
        part = part.strip()
        if not part:
            continue
        # parts look like "k={var}" or "k=value"
        if '=' in part:
            k, v = part.split('=', 1)
            k, v = k.strip(), v.strip()
            if k in target_args:
                if v.startswith('{') and v.endswith('}'):
                    varname = v[1:-1]
                    bindings[varname] = target_args[k]
                elif v != target_args[k]:
                    return None
    return bindings


def _extract_pred_and_vars(pattern: str):
    if '(' not in pattern:
        return pattern, {}
    pred = pattern[:pattern.index('(')]
    inner = pattern[pattern.index('(')+1:pattern.rindex(')')]
    vars_map = {}
    for part in inner.split(','):
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            vars_map[k.strip()] = v.strip()
    return pred, vars_map


def _instantiate_args(vars_map: Dict, bindings: Dict) -> Dict:
    result = {}
    for arg_name, var_or_val in vars_map.items():
        if var_or_val.startswith('{') and var_or_val.endswith('}'):
            varname = var_or_val[1:-1]
            result[arg_name] = bindings.get(varname, var_or_val)
        else:
            result[arg_name] = var_or_val
    return result
