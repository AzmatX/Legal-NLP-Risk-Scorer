import json
import re
from pathlib import Path

print("🚀 Loading CUAD_v1.json...")
json_path = Path("data/CUAD_v1.json")

if not json_path.exists():
    print(f"❌ Error: {json_path} nahi mila! Pehle file data folder mein daalo.")
    exit(1)

with open(json_path, encoding="utf-8") as f:
    raw = json.load(f)

samples = []
total_docs = len(raw["data"])
print(f"📄 Total Contracts in JSON: {total_docs}")

for doc_idx, doc in enumerate(raw["data"]):
    for para in doc.get("paragraphs", []):
        context = para.get("context", "")
        for qa in para.get("qas", []):
            # Sirf Positive samples lo (jinme clause exist karta hai)
            if qa.get("is_impossible", False):
                continue
            
            question = qa.get("question", "")
            # Label nikaalo (e.g., "governing_law")
            match = re.search(r'"([^"]+)"', question)
            label = match.group(1) if match else "unknown"
            
            # Answers (clause text) lo
            for ans in qa.get("answers", []):
                samples.append({
                    "context": context,
                    "question": question,
                    "label": label,
                    "answer_text": ans["text"]
                })

print(f"🔥 Total Labeled Clause Samples Extracted: {len(samples)}")

# Save as JSONL
output_path = Path("data/cuad_final.jsonl")
with open(output_path, "w", encoding="utf-8") as f:
    for s in samples:
        json.dump(s, f, ensure_ascii=False)
        f.write("\n")

print(f"✅ Saved to: {output_path.absolute()}")
print(f"📦 File Size: {output_path.stat().st_size // (1024*1024)} MB")

# Sample Check
print("\n📊 Sample Check (Pehle 2):")
for i in range(min(2, len(samples))):
    print(f"\n--- Sample {i+1} ---")
    print(f"Label: {samples[i]['label']}")
    print(f"Answer: {samples[i]['answer_text'][:150]}...")