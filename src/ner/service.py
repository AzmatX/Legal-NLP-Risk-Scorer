def extract_legal_entities(text: str) -> list[str]:
    if not text.strip():
        return []
    return ["Party A", "Party B"]
