import json
import re
from pathlib import Path
from collections import Counter

print("🚀 Directly creating lightweight dataset from CUAD_v1.json...")

json_path = Path("data/CUAD_v1.json")
if not json_path.exists():
    print(f"❌ Error: {json_path} nahi mila!")
    exit(1)

with open(json_path, encoding="utf-8") as f:
    raw = json.load(f)

samples = []
total_docs = len(raw["data"])

for doc in raw["data"]:
    for para in doc.get("paragraphs", []):
        for qa in para.get("qas", []):
            if qa.get("is_impossible", False):
                continue
            
            question = qa.get("question", "")
            # Label extract karo (e.g., "governing_law")
            match = re.search(r'"([^"]+)"', question)
            label = match.group(1) if match else "unknown"
            
            # Sirf answer text (clause text) lo. Context nahi lena.
            for ans in qa.get("answers", []):
                samples.append({
                    "text": ans["text"].strip(),
                    "label": label
                })

print(f"🔥 Total Labeled Clauses Extracted: {len(samples)}")

# Save as JSONL (Lightweight)
output_path = Path("data/cuad_classification.jsonl")
with open(output_path, "w", encoding="utf-8") as f:
    for s in samples:
        json.dump(s, f, ensure_ascii=False)
        f.write("\n")

size_mb = output_path.stat().st_size / (1024 * 1024)
print(f"✅ Saved to: {output_path}")
print(f"📦 File Size: {size_mb:.2f} MB (Bahut chhota! 🚀)")

# Stats
labels = [s["label"] for s in samples]
counter = Counter(labels)
print(f"\n🏷️ Total Unique Labels: {len(counter)}")
print("🔥 Top 10 Clauses:")
for label, count in counter.most_common(10):
    print(f"  {label}: {count}")