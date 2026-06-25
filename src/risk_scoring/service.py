def score_contract(clauses: list[dict[str, str]]) -> dict[str, float | str]:
    base = 25.0
    risk = min(100.0, base + (len(clauses) * 5.0))
    level = "low" if risk < 40 else "medium" if risk < 70 else "high"
    return {"risk_score": risk, "risk_level": level}
