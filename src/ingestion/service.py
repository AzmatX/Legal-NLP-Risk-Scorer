from pathlib import Path

ALLOWED_SUFFIXES = {".pdf", ".docx"}


def validate_contract_file(file_name: str) -> None:
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("Only PDF and DOCX files are supported")
