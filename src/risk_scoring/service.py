"""
Risk Scoring Service

Computes contract risk using clause presence, confidence weighting,
mandatory clause penalties, and generates actionable recommendations.
"""

from typing import Any

# -----------------------------------------------
# 1. Risk weights per clause type (0–30 scale)
# -----------------------------------------------
RISK_WEIGHTS: dict[str, int] = {
    "termination_for_cause": 30,
    "indemnification": 25,
    "limitation_of_liability": 25,
    "non_compete": 20,
    "data_protection": 20,
    "force_majeure": 15,
    "arbitration": 15,
    "non_solicit": 15,
    "payment_terms": 12,
    "insurance": 10,
    "warranty": 10,
    "assignment": 8,
    "confidentiality": 5,
    "governing_law": 5,
    "choice_of_forum": 5,
}

# -----------------------------------------------
# 2. Mandatory clauses – missing ones incur penalties
# -----------------------------------------------
MANDATORY_CLAUSES: set[str] = {
    "confidentiality",
    "governing_law",
    "payment_terms",
    "termination_for_cause",
}

# -----------------------------------------------
# 3. Thresholds for recommendations
# -----------------------------------------------
HIGH_RISK_WEIGHT_THRESHOLD = 15


def score_contract(clause_result: dict[str, Any]) -> dict[str, Any]:
    """
    Compute a comprehensive contract risk assessment.

    Args:
        clause_result:
            Dictionary containing:
            - clauses (per-clause labels and confidence scores)
            - summary (type_counts)
            - risk_factors

    Returns:
        Dictionary containing:
        - risk_score (0–100)
        - risk_level
        - risk_breakdown
        - missing_clauses
        - recommendations
        - unknown_clauses_count
    """

    clauses = clause_result.get("clauses", [])
    type_counts = clause_result.get("summary", {}).get("type_counts", {})

    # Map each clause label to its confidence values
    detected_labels: dict[str, list[float]] = {}

    for clause in clauses:
        label = clause.get("label", "unknown")
        conf_str = clause.get("confidence", "0.00")

        try:
            conf = float(conf_str)
        except ValueError:
            conf = 0.0

        detected_labels.setdefault(label, []).append(conf)

    # -----------------------------------------------
    # A. Weighted score with confidence
    # -----------------------------------------------
    risk_breakdown = []
    total_weighted_score = 0.0

    for label, confs in detected_labels.items():
        weight = RISK_WEIGHTS.get(label, 0)

        if weight == 0:
            continue

        # Use the maximum confidence to avoid
        # diluting the calculated risk score.
        max_conf = max(confs)

        contribution = weight * max_conf
        total_weighted_score += contribution

        risk_breakdown.append(
            {
                "clause": label,
                "weight": weight,
                "confidence": round(max_conf, 2),
                "contribution": round(contribution, 2),
            }
        )

    # -----------------------------------------------
    # B. Missing mandatory clause penalties
    # -----------------------------------------------
    detected_set = set(detected_labels.keys())
    missing = MANDATORY_CLAUSES - detected_set

    missing_penalty = len(missing) * 10
    total_weighted_score += missing_penalty

    # -----------------------------------------------
    # C. Normalize to 0–100
    # -----------------------------------------------
    risk_score = min(100, round(total_weighted_score))

    # -----------------------------------------------
    # D. Risk level
    # -----------------------------------------------
    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    # -----------------------------------------------
    # E. Generate recommendations
    # -----------------------------------------------
    recommendations: list[str] = []

    for clause in missing:
        recommendations.append(
            f"Add {clause.replace('_', ' ').title()} clause"
        )

    for item in risk_breakdown:
        if item["weight"] >= HIGH_RISK_WEIGHT_THRESHOLD:
            recommendations.append(
                f"Review {item['clause'].replace('_', ' ').title()} obligations"
            )

    unknown_count = type_counts.get("unknown", 0)

    if unknown_count > 0:
        recommendations.append(
            "Consider fine-tuning classifier because "
            f"{unknown_count} clause(s) were not recognized."
        )

    # -----------------------------------------------
    # F. Final result
    # -----------------------------------------------
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_breakdown": risk_breakdown,
        "missing_clauses": list(missing),
        "recommendations": recommendations,
        "unknown_clauses_count": unknown_count,
    }