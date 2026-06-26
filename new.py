# save_cuad_local.py
from datasets import load_dataset

print("🔄 Downloading CUAD dataset from Hugging Face...")
dataset = load_dataset("theatticusproject/cuad", split="train")

print(f"✅ Loaded {len(dataset)} rows!")

# Isko apne project ke 'data' folder mein save karo taaki baar baar download na karna pade
dataset.save_to_disk("data/cuad_processed")

print("💾 Dataset saved locally to 'data/cuad_processed'")
print("\n📊 Sample Entry:")
print(dataset[0])