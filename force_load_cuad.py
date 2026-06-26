# force_load_cuad.py
from datasets import load_dataset
import json
from pathlib import Path

# data folder banayein
Path("data").mkdir(exist_ok=True)

print("🔄 Force downloading/loading CUAD dataset with no checks...")
print("(Cache delete kiya tha toh naya download hoga, thoda wait karo)")

# verification_mode='no_checks' bypass karega mismatch error
ds = load_dataset(
    "theatticusproject/cuad", 
    split="train", 
    verification_mode="no_checks"
)

print(f"✅ FORCE LOADED {len(ds)} ROWS!")

# JSONL mein save karte hain
with open("data/cuad_data.jsonl", "w", encoding="utf-8") as f:
    for row in ds:
        json.dump(row, f, ensure_ascii=False)
        f.write("\n")

print("💾 FORCE SAVED to data/cuad_data.jsonl")