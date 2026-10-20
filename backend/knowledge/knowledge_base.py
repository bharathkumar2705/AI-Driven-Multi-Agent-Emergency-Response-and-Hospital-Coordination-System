"""
Knowledge Base: stores facts and rules, supports assertion, retraction, and querying.
Facts are stored as structured dicts for easy serialization.
"""
from typing import List, Dict, Any, Optional
from .rules import EMERGENCY_RULES, Rule
import copy


class KnowledgeBase:
    def __init__(self):
        self.facts: List[Dict[str, Any]] = []
        self.rules: List[Rule] = list(EMERGENCY_RULES)
        self._fact_set: set = set()  # for fast lookup

    def assert_fact(self, predicate: str, **kwargs) -> bool:
        """Add a fact. Returns True if new, False if already existed."""
        key = self._make_key(predicate, kwargs)
        if key in self._fact_set:
            return False
        self._fact_set.add(key)
        self.facts.append({"predicate": predicate, "args": kwargs, "key": key})
        return True

    def retract_fact(self, predicate: str, **kwargs):
        """Remove a fact."""
        key = self._make_key(predicate, kwargs)
        self._fact_set.discard(key)
        self.facts = [f for f in self.facts if f["key"] != key]

    def query(self, predicate: str, **kwargs) -> bool:
        """Check if a fact exists."""
        key = self._make_key(predicate, kwargs)
        return key in self._fact_set

    def query_all(self, predicate: str) -> List[Dict]:
        """Return all facts matching a predicate."""
        return [f for f in self.facts if f["predicate"] == predicate]

    def get_all_facts(self) -> List[Dict]:
        return copy.deepcopy(self.facts)

    def get_rules(self) -> List[dict]:
        return [r.to_dict() for r in self.rules]

    def load_patient_facts(self, patient: dict):
        """Load facts about a patient into the KB."""
        pid = patient["patient_id"]
        if "ICU" in patient.get("required_resources", []):
            self.assert_fact("patient_requires_icu", patient=pid)
        else:
            self.assert_fact("patient_no_icu_required", patient=pid)

        spec = patient.get("required_specialist", "")
        if spec:
            self.assert_fact("patient_requires_specialist", patient=pid, specialist=spec)

    def load_hospital_facts(self, hospital: dict):
        """Load facts about a hospital into the KB."""
        hid = hospital["hospital_id"]
        if hospital.get("icu_available", 0) > 0:
            self.assert_fact("hospital_icu_available", hospital=hid)
        else:
            self.assert_fact("hospital_icu_full", hospital=hid)

        if hospital.get("available_beds", 0) > 0:
            self.assert_fact("hospital_has_beds", hospital=hid)

        for spec in hospital.get("available_specialists", []):
            self.assert_fact("hospital_has_specialist", hospital=hid, specialist=spec)

    def load_doctor_facts(self, doctor: dict):
        did = doctor["doctor_id"]
        self.assert_fact("doctor_specialization", doctor=did, specialist=doctor["specialization"])
        if doctor.get("availability", True):
            self.assert_fact("doctor_available", doctor=did)

    def load_road_facts(self, road: dict):
        rid = road["road_id"]
        state = road.get("state", "NORMAL")
        if state == "CONGESTED":
            self.assert_fact("road_congested", road=rid)
        elif state == "BLOCKED":
            self.assert_fact("road_blocked", road=rid)

    def reset_derived_facts(self):
        """Remove all inferred/derived facts (those added by forward chaining)."""
        derived_predicates = {
            "hospital_satisfies_icu", "hospital_satisfies_specialist",
            "hospital_eligible_for_patient", "hospital_rejects_patient",
            "doctor_can_treat", "road_high_cost", "road_unavailable"
        }
        self.facts = [f for f in self.facts if f["predicate"] not in derived_predicates]
        self._fact_set = {f["key"] for f in self.facts}

    def _make_key(self, predicate: str, args: dict) -> str:
        sorted_args = sorted(args.items())
        return f"{predicate}({','.join(f'{k}={v}' for k,v in sorted_args)})"

    def clear(self):
        self.facts.clear()
        self._fact_set.clear()

    def snapshot(self) -> dict:
        return {
            "facts": self.get_all_facts(),
            "rules": self.get_rules(),
            "fact_count": len(self.facts)
        }


# Global KB instance shared by the system
_kb: Optional[KnowledgeBase] = None

def get_knowledge_base() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb

def reset_knowledge_base() -> KnowledgeBase:
    global _kb
    _kb = KnowledgeBase()
    return _kb
