"""
Risk Scoring Service
Computes contract risk using clause presence, confidence weighting,
mandatory clause penalties, and generates actionable recommendations.
"""

from typing import Dict, Any, List, Set
import re

# -----------------------------------------------
# 1. Risk weights per clause type (0–30 scale)
# -----------------------------------------------
RISK_WEIGHTS: Dict[str, int] = {
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
MANDATORY_CLAUSES: Set[str] = {
    "confidentiality",
    "governing_law",
    "payment_terms",
    "termination_for_cause",
}

# -----------------------------------------------
# 3. Thresholds for recommendations
# -----------------------------------------------
HIGH_RISK_WEIGHT_THRESHOLD = 15   # clauses with weight above this will trigger a "review" recommendation

def score_contract(clause_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a comprehensive risk assessment from the output of classify_contract().

    Args:
        clause_result: dict with keys 'clauses' (list of per-clause dicts with label and confidence),
                       'summary' (type_counts), 'risk_factors', etc.

    Returns:
        dict with:
        - risk_score: int (0–100)
        - risk_level: 'low' | 'medium' | 'high'
        - risk_breakdown: list of dicts with clause, weight, confidence, contribution
        - missing_clauses: list of mandatory clauses not found
        - recommendations: list of actionable suggestions
        - unknown_clauses_count: int
    """
    clauses = clause_result.get("clauses", [])
    type_counts = clause_result.get("summary", {}).get("type_counts", {})

    # Prepare a mapping of clause label -> list of confidences (if multiple occurrences)
    detected_labels = {}
    for clause in clauses:
        label = clause.get("label", "unknown")
        conf_str = clause.get("confidence", "0.00")
        try:
            conf = float(conf_str)
        except ValueError:
            conf = 0.0
        if label not in detected_labels:
            detected_labels[label] = []
        detected_labels[label].append(conf)

    # -----------------------------------------------
    # A. Weighted score with confidence
    # -----------------------------------------------
    risk_breakdown = []
    total_weighted_score = 0.0

    for label, confs in detected_labels.items():
        weight = RISK_WEIGHTS.get(label, 0)
        if weight == 0:
            continue  # ignore unknown for scoring (but we count them later)
        # Use average confidence if multiple occurrences, or max? We'll use max to avoid diluting risk.
        avg_conf = sum(confs) / len(confs)
        contribution = weight * avg_conf
        total_weighted_score += contribution
        risk_breakdown.append({
            "clause": label,
            "weight": weight,
            "confidence": round(avg_conf, 2),
            "contribution": round(contribution, 2),
        })

    # -----------------------------------------------
    # B. Missing mandatory clause penalties
    # -----------------------------------------------
    detected_set = set(detected_labels.keys())
    missing = MANDATORY_CLAUSES - detected_set
    missing_penalty = len(missing) * 10   # +10 per missing clause
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
    recommendations = []

    # 1. Missing mandatory clauses
    for clause in missing:
        recommendations.append(f"Add {clause.replace('_', ' ').title()} clause")

    # 2. High-risk detected clauses (weight > threshold)
    for item in risk_breakdown:
        if item["weight"] >= HIGH_RISK_WEIGHT_THRESHOLD:
            recommendations.append(f"Review {item['clause'].replace('_', ' ').title()} obligations")

    # 3. If many unknown clauses, suggest model improvement
    unknown_count = type_counts.get("unknown", 0)
    if unknown_count > 0:
        recommendations.append(f"Consider fine‑tuning classifier – {unknown_count} clause(s) were not recognized")

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