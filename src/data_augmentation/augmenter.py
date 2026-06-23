import random

party_names = ["Company A", "Company B", "Vendor", "Client"]
durations = ["6 months", "12 months", "24 months"]

synonyms = {
    "shall": ["must", "agrees to"],
    "customers": ["clients", "buyers"],
    "increase": ["raise", "adjust"],
    "prices": ["pricing", "fees"]
}


def augment_text(text):
    if "Company A" in text:
        text = text.replace("Company A", random.choice(party_names))

    text = text.replace("12 months", random.choice(durations))

    for word, replacements in synonyms.items():
        if word in text:
            text = text.replace(word, random.choice(replacements))

    return text