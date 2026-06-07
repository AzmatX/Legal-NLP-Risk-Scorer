def classify_clause(text: str) -> dict[str, str]:
    return {"label": "governing_law", "confidence": "0.50" if text else "0.00"}
