from datasets import load_dataset

dataset = load_dataset("theatticusproject/cuad", split="train")

termination_count = 0
confidentiality_count = 0

for sample in dataset:
    categories = sample.get("qas", [])

    found_termination = False
    found_confidentiality = False

    for qa in categories:
        question = qa.get("question", "").lower()

        if "termination" in question:
            found_termination = True

        if "confidentiality" in question:
            found_confidentiality = True

    if found_termination:
        termination_count += 1

    if found_confidentiality:
        confidentiality_count += 1

print(f"Contracts with Termination clauses: {termination_count}")
print(f"Contracts with Confidentiality clauses: {confidentiality_count}")