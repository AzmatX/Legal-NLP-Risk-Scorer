import json
from collections import Counter

with open("data/CUADv1.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

documents = dataset["data"]
label_counter = Counter()

for doc in documents:
    for para in doc["paragraphs"]:
        for qa in para["qas"]:
            if not qa["is_impossible"]:   # only actual clause present
                label = qa["id"].split("__")[-1]
                label_counter[label] += 1

print("TOTAL POSITIVE LABELS:", sum(label_counter.values()))
print("TOTAL UNIQUE LABELS:", len(label_counter))

print("\nTOP 20 LABELS:")
for label, count in label_counter.most_common(20):
    print(f"{label}: {count}")

print("\nRARE LABELS (<50):")
for label, count in sorted(label_counter.items(), key=lambda x: x[1]):
    if count < 50:
        print(f"{label}: {count}")