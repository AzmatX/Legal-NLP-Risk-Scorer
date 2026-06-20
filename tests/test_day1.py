from src.ingestion.file_processor import ContractProcessor

processor = ContractProcessor()

sample_text = """
This Agreement is made between ABC Corp and XYZ Ltd on 5th June 2024.
Confidentiality must be maintained.
"""

result = processor.process_text("sample.pdf", sample_text)

print(result)