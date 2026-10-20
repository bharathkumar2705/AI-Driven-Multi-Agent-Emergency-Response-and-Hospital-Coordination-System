"""
Forward Chaining Inference Engine.
Starts from known facts and applies rules until no new facts can be derived (fixpoint).
Returns a full derivation trace showing which rule fired and what was derived.
"""
from typing import List, Dict, Any
from knowledge.knowledge_base import KnowledgeBase
import itertools


class DerivedFact:
    def __init__(self, fact: dict, rule_id: str, rule_desc: str, from_facts: List[str]):
        self.fact = fact
        self.rule_id = rule_id
        self.rule_desc = rule_desc
        self.from_facts = from_facts

    def to_dict(self) -> dict:
        return {
            "derived_fact": self.fact,
            "by_rule": self.rule_id,
            "rule_description": self.rule_desc,
            "from_facts": self.from_facts
        }


def forward_chain(kb: KnowledgeBase) -> List[DerivedFact]:
    """
    Run forward chaining over all facts and rules.
    Continues until fixpoint (no new facts derived in a pass).
    """
    derivations: List[DerivedFact] = []
    changed = True

    while changed:
        changed = False
        for rule in kb.rules:
            # Extract variable bindings from conditions
            bindings_list = _find_bindings(kb, rule.conditions)
            for bindings in bindings_list:
                conclusion = _instantiate(rule.conclusion, bindings)
                pred, args = _parse_fact_string(conclusion)
                if pred and not kb.query(pred, **args):
                    kb.assert_fact(pred, **args)
                    from_facts = [_instantiate(c, bindings) for c in rule.conditions]
                    derivations.append(DerivedFact(
                        {"predicate": pred, "args": args, "key": conclusion},
                        rule.rule_id,
                        rule.description,
                        from_facts
                    ))
                    changed = True

    return derivations


def _find_bindings(kb: KnowledgeBase, conditions: List[str]) -> List[Dict[str, str]]:
    """Find all variable bindings that satisfy all conditions simultaneously."""
    if not conditions:
        return [{}]

    all_bindings = [{}]
    for condition in conditions:
        new_bindings = []
        pred, vars_in_cond = _extract_pred_and_vars(condition)
        matching_facts = kb.query_all(pred)

        for current_binding in all_bindings:
            for fact in matching_facts:
                extended = _try_bind(current_binding, vars_in_cond, fact["args"])
                if extended is not None:
                    new_bindings.append(extended)
        all_bindings = new_bindings
        if not all_bindings:
            break

    return all_bindings


def _extract_pred_and_vars(pattern: str):
    """Extract predicate name and variable names from a pattern like 'foo({x},{y})'."""
    if '(' not in pattern:
        return pattern, {}
    pred = pattern[:pattern.index('(')]
    inner = pattern[pattern.index('(')+1:pattern.rindex(')')]
    vars_map = {}
    if inner:
        for part in inner.split(','):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                vars_map[k.strip()] = v.strip()
            elif part.startswith('{') and part.endswith('}'):
                varname = part[1:-1]
                vars_map[varname] = None  # unbound variable
    return pred, vars_map


def _try_bind(current: Dict, vars_in_cond: Dict, fact_args: Dict) -> Dict | None:
    """Try to extend current binding with fact_args. Returns None on conflict."""
    extended = dict(current)
    # vars_in_cond maps arg_name -> variable_name (or None for unbound)
    for arg_name, var_name in vars_in_cond.items():
        fact_val = fact_args.get(arg_name)
        if fact_val is None:
            continue
        if var_name is None:
            var_name = arg_name  # use arg name as variable name
        if var_name in extended:
            if extended[var_name] != fact_val:
                return None
        else:
            extended[var_name] = fact_val
    return extended


def _instantiate(pattern: str, bindings: Dict) -> str:
    """Replace {var} placeholders with bound values."""
    result = pattern
    for var, val in bindings.items():
        result = result.replace(f'{{{var}}}', str(val))
    return result


def _parse_fact_string(fact_str: str):
    """Parse 'pred(k1=v1,k2=v2)' into (pred, {k1:v1, k2:v2})."""
    if '(' not in fact_str:
        return fact_str, {}
    pred = fact_str[:fact_str.index('(')]
    inner = fact_str[fact_str.index('(')+1:fact_str.rindex(')')]
    args = {}
    if inner:
        for part in inner.split(','):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                args[k.strip()] = v.strip()
    return pred, args
