"""
Uncertainty module: fuzzy-style probability values for traffic and hospital load.
These values modulate utility scores without requiring machine learning.
"""
from typing import Dict


# Traffic load probability values (0.0 = no load, 1.0 = max load)
TRAFFIC_UNCERTAINTY = {
    "NORMAL": 0.1,
    "MODERATE": 0.4,
    "CONGESTED": 0.8,
    "BLOCKED": 1.0
}

# Hospital occupancy levels (fraction of capacity used)
def hospital_load_uncertainty(available_beds: int, total_beds: int) -> float:
    """Return a load factor: 0.0 = empty, 1.0 = completely full."""
    if total_beds == 0:
        return 1.0
    used = total_beds - available_beds
    ratio = used / total_beds
    # Fuzzy thresholds
    if ratio < 0.3:
        return 0.2   # LOW load
    elif ratio < 0.6:
        return 0.5   # MEDIUM load
    elif ratio < 0.9:
        return 0.8   # HIGH load
    else:
        return 1.0   # CRITICAL

def icu_load_uncertainty(icu_available: int, icu_total: int) -> float:
    """Return ICU load factor."""
    if icu_total == 0:
        return 1.0
    if icu_available == 0:
        return 1.0
    return hospital_load_uncertainty(icu_available, icu_total)

def route_uncertainty(road_states: list) -> float:
    """
    Given a list of road states along a route, compute overall route uncertainty.
    Higher = riskier route.
    """
    if not road_states:
        return 0.0
    values = [TRAFFIC_UNCERTAINTY.get(s, 0.1) for s in road_states]
    # Weighted: worst roads have more impact (max + mean blend)
    return 0.6 * max(values) + 0.4 * (sum(values) / len(values))

def severity_weight(severity: str) -> Dict[str, float]:
    """
    Return utility weight configuration based on patient severity.
    Critical patients prioritise resource availability over distance.
    """
    weights = {
        "CRITICAL":  {"resource": 0.40, "specialist": 0.30, "distance": 0.15, "traffic": 0.15},
        "HIGH":      {"resource": 0.30, "specialist": 0.25, "distance": 0.25, "traffic": 0.20},
        "MODERATE":  {"resource": 0.25, "specialist": 0.20, "distance": 0.30, "traffic": 0.25},
        "LOW":       {"resource": 0.20, "specialist": 0.15, "distance": 0.35, "traffic": 0.30},
    }
    return weights.get(severity, weights["MODERATE"])
