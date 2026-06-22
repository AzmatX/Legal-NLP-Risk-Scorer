"""
File Processor for legal contract documents.

Orchestrates validation, cleaning, and initial structuring of raw contract text.
"""

from typing import Any, Dict, Optional

from src.ingestion.cleaner import TextCleaner
from src.ingestion.schema import ContractSchema
from src.ingestion.validator import ContractValidator


class ContractProcessor:
    """
    Processes raw contract text through the ingestion pipeline.

    Steps:
        1. Validate the text (e.g. minimum length, encoding).
        2. Clean the text (headers, footers, whitespace, etc.).
        3. Create a structured ContractSchema object for downstream use.

    Typical usage:
        processor = ContractProcessor()
        structured = processor.process_text("contract.pdf", raw_text)
    """

    def __init__(
        self,
        cleaner: Optional[TextCleaner] = None,
        validator: Optional[ContractValidator] = None
    ) -> None:
        """
        Args:
            cleaner: A TextCleaner instance. If None, uses default settings.
            validator: A ContractValidator instance. If None, uses default settings.
        """
        self.cleaner = cleaner if cleaner is not None else TextCleaner()
        self.validator = validator if validator is not None else ContractValidator()

    def process_text(self, file_name: str, text: str) -> Dict[str, Any]:
        """
        Validate, clean, and structure raw contract text.

        Args:
            file_name: Identifier for the source (e.g. filename, path, UUID).
            text: Raw text extracted from the document.

        Returns:
            A dictionary representation of ContractSchema, containing
            file_name, cleaned text, and empty entity/clause slots.

        Raises:
            ValueError: If validation fails (via ContractValidator).
            TypeError: If text is not a string.
        """
        # Guard against non‑string input
        if not isinstance(text, str):
            raise TypeError(
                f"Expected string for 'text', got {type(text).__name__}"
            )

        # Validate (raises on failure)
        self.validator.validate(file_name, text)

        # Clean the text
        cleaned_text = self.cleaner.clean(text)

        # Create structured data (entities & clauses to be populated later)
        structured = ContractSchema(
            file_name=file_name,
            text=cleaned_text,
            entities={},
            clauses={}
        )

        return structured.to_dict()