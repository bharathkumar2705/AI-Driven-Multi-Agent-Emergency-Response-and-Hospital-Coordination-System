"""
Rule definitions for the Emergency Response Knowledge Base.
Each rule has a list of conditions (functions over the fact set)
and a conclusion that is added when all conditions are satisfied.
"""
from typing import List, Callable, Set, Tuple


class Rule:
    def __init__(self, rule_id: str, description: str,
                 conditions: List[str], conclusion: str):
        self.rule_id = rule_id
        self.description = description
        self.conditions = conditions  # list of fact pattern strings
        self.conclusion = conclusion  # fact pattern string to assert

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "conditions": self.conditions,
            "conclusion": self.conclusion
        }


# Predefined rules for the knowledge base
EMERGENCY_RULES: List[Rule] = [
    Rule(
        "R001",
        "If patient requires ICU and hospital has available ICU, hospital satisfies ICU requirement",
        ["patient_requires_icu({patient})", "hospital_icu_available({hospital})"],
        "hospital_satisfies_icu({hospital},{patient})"
    ),
    Rule(
        "R002",
        "If patient requires specialist and hospital has that specialist available, hospital satisfies specialist requirement",
        ["patient_requires_specialist({patient},{specialist})", "hospital_has_specialist({hospital},{specialist})"],
        "hospital_satisfies_specialist({hospital},{patient})"
    ),
    Rule(
        "R003",
        "If hospital satisfies ICU and specialist requirements, hospital is eligible for critical patient",
        ["hospital_satisfies_icu({hospital},{patient})", "hospital_satisfies_specialist({hospital},{patient})"],
        "hospital_eligible_for_patient({hospital},{patient})"
    ),
    Rule(
        "R004",
        "If hospital has available beds and patient does not require ICU, hospital can accept patient",
        ["hospital_has_beds({hospital})", "patient_no_icu_required({patient})"],
        "hospital_eligible_for_patient({hospital},{patient})"
    ),
    Rule(
        "R005",
        "If doctor is available and has required specialization, doctor can treat patient",
        ["doctor_available({doctor})", "doctor_specialization({doctor},{specialist})", "patient_requires_specialist({patient},{specialist})"],
        "doctor_can_treat({doctor},{patient})"
    ),
    Rule(
        "R006",
        "If road is congested, route using that road has high cost",
        ["road_congested({road})"],
        "road_high_cost({road})"
    ),
    Rule(
        "R007",
        "If road is blocked, route using that road is unavailable",
        ["road_blocked({road})"],
        "road_unavailable({road})"
    ),
    Rule(
        "R008",
        "If hospital ICU is full, hospital cannot accept critical patient needing ICU",
        ["hospital_icu_full({hospital})", "patient_requires_icu({patient})"],
        "hospital_rejects_patient({hospital},{patient})"
    ),
]
