import spacy

nlp = spacy.load("en_core_web_sm")

def extract_legal_entities(text: str):
    if not text.strip():
        return []

    doc = nlp(text)

    entities = []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "DATE", "MONEY"]:
            entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_
                }
            )

    return entities