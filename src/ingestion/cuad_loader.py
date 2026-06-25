"""
CUAD (Contract Understanding Atticus Dataset) loader.

Provides two loading strategies:
1. Standard in‑memory load (fast, suitable for files up to a few hundred MB).
2. Streaming load via ijson (constant memory, ideal for very large JSON files).
"""

import json
from collections.abc import Iterator
from typing import Any

# Optional streaming dependency – install with: pip install ijson
try:
    import ijson
    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False


class CUADLoader:
    """Loads and flattens the CUAD dataset from a JSON file."""

    # Expected top‑level key
    DATA_KEY = "data"

    # Keys inside each contract / paragraph
    TITLE_KEY = "title"
    PARAGRAPHS_KEY = "paragraphs"
    CONTEXT_KEY = "context"
    QAS_KEY = "qas"

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def load(self, file_path: str) -> list[dict[str, Any]]:
        """
        Load the CUAD JSON file fully into memory and flatten its structure.

        Args:
            file_path: Path to the CUAD JSON file (e.g. CUADv1.json).

        Returns:
            A list of dicts, each with keys 'title', 'context', 'qas'.
            Returns an empty list if the file contains no data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON structure is invalid or missing required keys.
        """
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Validate top‑level structure
        if not isinstance(data, dict) or self.DATA_KEY not in data:
            raise ValueError(
                f"Invalid JSON format: expected dict with key '{self.DATA_KEY}'"
            )

        contracts_data = data[self.DATA_KEY]
        if not isinstance(contracts_data, list):
            raise ValueError(
                f"'{self.DATA_KEY}' must be a list, got {type(contracts_data)}"
            )

        # Flatten using a list comprehension (fast and readable)
        return [
            {
                "title": contract[self.TITLE_KEY],
                "context": paragraph[self.CONTEXT_KEY],
                "qas": paragraph[self.QAS_KEY],
            }
            for contract in contracts_data
            if isinstance(contract, dict)
            for paragraph in contract.get(self.PARAGRAPHS_KEY, [])
            if isinstance(paragraph, dict)
        ]

    def load_stream(self, file_path: str) -> Iterator[dict[str, Any]]:
        """
        Stream the CUAD JSON file using ijson – constant memory footprint.

        This method yields one paragraph at a time, making it ideal for
        extremely large datasets that do not fit in memory.

        Args:
            file_path: Path to the CUAD JSON file.

        Yields:
            Dicts with keys 'title', 'context', 'qas'.

        Raises:
            ImportError: If ijson is not installed.
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON structure is invalid.
        """
        if not HAS_IJSON:
            raise ImportError(
                "The ijson library is required for streaming. "
                "Install it with: pip install ijson"
            )

        with open(file_path, 'rb') as f:
            # ijson.items parses the "data" array item by item
            for contract in ijson.items(f, 'data.item'):
                title = contract[self.TITLE_KEY]

                # Paragraphs can be missing – safely iterate
                paragraphs = contract.get(self.PARAGRAPHS_KEY, [])
                if not isinstance(paragraphs, list):
                    continue

                for paragraph in paragraphs:
                    if not isinstance(paragraph, dict):
                        continue
                    yield {
                        "title": title,
                        "context": paragraph[self.CONTEXT_KEY],
                        "qas": paragraph[self.QAS_KEY],
                    }