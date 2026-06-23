import json

rare_labels = [
    "Source Code Escrow",
    "Price Restrictions",
    "Unlimited/All-You-Can-Eat-License",
    "Affiliate License-Licensor",
    "Most Favored Nation",
    "Third Party Beneficiary",
    "No-Solicit Of Customers",
    "Non-Disparagement",
    "Joint Ip Ownership"
]

with open("data/CUADv1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

found = {label: [] for label in rare_labels}

for doc in data["data"]:
    for paragraph in doc["paragraphs"]:
        context = paragraph["context"]

        for qa in paragraph["qas"]:
            label = qa["question"].split('"')[1]

            if label in rare_labels and not qa["is_impossible"]:
                for ans in qa["answers"]:
                    found[label].append(ans["text"])

for label, clauses in found.items():
    print(f"\n{label}: {len(clauses)}")
    if clauses:
        print("Sample:", clauses[0][:300])