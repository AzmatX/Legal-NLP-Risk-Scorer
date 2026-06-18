from src.ingestion.file_processor import ContractProcessor

processor = ContractProcessor()

print("Testing valid contract...\n")

valid_text = """
This Agreement is made between ABC Corp and XYZ Ltd.
Confidentiality must be maintained throughout the contract term.
"""

print(processor.process_text("contract.pdf", valid_text))

print("\nTesting invalid contract...\n")

try:
    processor.process_text("contract.pdf", "")
except ValueError as e:
    print("Validation Error:", e)