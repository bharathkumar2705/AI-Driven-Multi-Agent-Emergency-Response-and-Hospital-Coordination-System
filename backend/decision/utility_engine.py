"""
Utility-Based Hospital Selection Engine.
Scores each hospital using weighted factors and selects the best eligible one.

Utility = w_resource * resource_score
        + w_specialist * specialist_score
        - w_distance * normalized_distance
        - w_traffic * route_uncertainty

All scores are in [0, 1]. Weights depend on patient severity.
"""
from typing import List, Dict, Optional, Tuple
import math
from .uncertainty import severity_weight, icu_load_uncertainty, hospital_load_uncertainty, route_uncertainty, TRAFFIC_UNCERTAINTY


MAX_GRID_DIST = math.sqrt(2) * 9   # max Manhattan on 10x10 grid = 18


def manhattan(a: List[int], b: List[int]) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def score_hospital(
    hospital: dict,
    patient: dict,
    doctors: List[dict],
    route_road_states: List[str],
    ambulance_pos: List[int]
) -> dict:
    """
    Compute utility score for a single hospital.
    Returns score breakdown dict.
    """
    severity = patient.get("severity", "MODERATE")
    weights = severity_weight(severity)
    needs_icu = "ICU" in patient.get("required_resources", []) or patient.get("severity") == "CRITICAL"
    required_spec = patient.get("required_specialist", "")

    # 1. Resource score
    resource_score = 0.0
    resource_reasons = []
    if needs_icu:
        if hospital.get("icu_available", 0) > 0:
            # Higher ICU availability = better score
            icu_load = icu_load_uncertainty(hospital["icu_available"], hospital.get("icu_total", 1))
            resource_score = 1.0 - icu_load * 0.5  # penalise high load
            resource_reasons.append(f"ICU available ({hospital['icu_available']}) ✅")
        else:
            resource_score = 0.0
            resource_reasons.append("ICU unavailable ❌")
    else:
        bed_load = hospital_load_uncertainty(hospital.get("available_beds", 0), hospital.get("total_beds", 1))
        resource_score = 1.0 - bed_load * 0.3
        resource_reasons.append(f"Beds available: {hospital.get('available_beds', 0)} ✅")

    # 2. Specialist score
    specialist_score = 0.0
    specialist_reasons = []
    hosp_id = hospital["hospital_id"]
    hosp_doctors = [d for d in doctors if d["hospital_id"] == hosp_id]
    if required_spec:
        available_spec = [d for d in hosp_doctors if d["specialization"] == required_spec and d.get("availability", True)]
        if available_spec:
            specialist_score = 1.0
            specialist_reasons.append(f"{required_spec} available ✅")
        else:
            specialist_score = 0.0
            specialist_reasons.append(f"{required_spec} unavailable ❌")
    else:
        specialist_score = 0.8  # no special requirement
        specialist_reasons.append("No specialist required")

    # 3. Distance score (higher = closer)
    hosp_loc = hospital.get("location", {"row": 0, "col": 0})
    if isinstance(hosp_loc, dict):
        hosp_pos = [hosp_loc["row"], hosp_loc["col"]]
    else:
        hosp_pos = list(hosp_loc)
    dist = manhattan(ambulance_pos, hosp_pos)
    distance_score = dist / MAX_GRID_DIST  # normalised: 0=close, 1=far

    # 4. Traffic score
    traffic_val = route_uncertainty(route_road_states)

    # 5. Composite utility
    utility = (
        weights["resource"] * resource_score
        + weights["specialist"] * specialist_score
        - weights["distance"] * distance_score
        - weights["traffic"] * traffic_val
    )
    utility = max(0.0, min(1.0, utility))

    # Reject if critical resource unavailable
    eligible = True
    rejection_reason = None
    if needs_icu and hospital.get("icu_available", 0) == 0:
        eligible = False
        rejection_reason = "ICU unavailable"
    if required_spec and specialist_score == 0.0:
        eligible = False
        rejection_reason = f"Required specialist ({required_spec}) unavailable"
    if hospital.get("available_beds", 0) == 0:
        eligible = False
        rejection_reason = "No beds available"

    return {
        "hospital_id": hosp_id,
        "hospital_name": hospital.get("name", hosp_id),
        "utility_score": round(utility, 4),
        "resource_score": round(resource_score, 4),
        "specialist_score": round(specialist_score, 4),
        "distance_score": round(distance_score, 4),
        "traffic_score": round(traffic_val, 4),
        "distance_km": round(dist * 0.8, 2),
        "eligible": eligible,
        "rejection_reason": rejection_reason,
        "resource_reasons": resource_reasons,
        "specialist_reasons": specialist_reasons,
        "weights": weights
    }


def select_best_hospital(
    hospitals: List[dict],
    patient: dict,
    doctors: List[dict],
    city_graph,
    ambulance_pos: List[int]
) -> Tuple[Optional[dict], List[dict]]:
    """
    Score all hospitals and return (best_hospital_score, all_scores).
    Returns None if no eligible hospital found.
    """
    all_scores = []
    for hospital in hospitals:
        hosp_loc = hospital.get("location", {"row": 0, "col": 0})
        if isinstance(hosp_loc, dict):
            hosp_pos = [hosp_loc["row"], hosp_loc["col"]]
        else:
            hosp_pos = list(hosp_loc)

        # Sample road states between ambulance and hospital (simplified)
        road_states = _sample_route_states(city_graph, ambulance_pos, hosp_pos)
        score = score_hospital(hospital, patient, doctors, road_states, ambulance_pos)
        all_scores.append(score)

    eligible = [s for s in all_scores if s["eligible"]]
    if not eligible:
        return None, all_scores

    best = max(eligible, key=lambda s: s["utility_score"])
    return best, all_scores


def _sample_route_states(city_graph, start: List[int], end: List[int]) -> List[str]:
    """Quickly estimate road states on a direct route (for scoring only)."""
    states = []
    r, c = start[0], start[1]
    er, ec = end[0], end[1]
    # Walk a Manhattan path and sample road states
    steps = 0
    while (r != er or c != ec) and steps < 20:
        if r < er:
            node = (r, c)
            next_node = (r+1, c)
        elif r > er:
            node = (r, c)
            next_node = (r-1, c)
        elif c < ec:
            node = (r, c)
            next_node = (r, c+1)
        else:
            node = (r, c)
            next_node = (r, c-1)
        road_id = city_graph.get_road_by_nodes(node, next_node)
        if road_id:
            states.append(city_graph.edges[road_id]["state"])
        if r < er:
            r += 1
        elif r > er:
            r -= 1
        elif c < ec:
            c += 1
        else:
            c -= 1
        steps += 1
    return states if states else ["NORMAL"]
