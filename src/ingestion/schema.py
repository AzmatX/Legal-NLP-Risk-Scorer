"""
Contract Schema definition using dataclasses.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict


@dataclass
class ContractSchema:
    """
    Structured representation of a cleaned contract document.

    Attributes:
        file_name: Identifier (e.g., filename or UUID) of the source document.
        text: The cleaned text content.
        entities: Extracted named entities (populated by NER service).
        clauses: Classified clauses (populated by clause classifier).
    """

    file_name: str
    text: str
    # Use default_factory for mutable defaults (safety and clarity)
    entities: Dict[str, Any] = field(default_factory=dict)
    clauses: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dataclass to a plain dictionary.

        Returns:
            Dictionary with all fields.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContractSchema":
        """
        Create a ContractSchema instance from a dictionary.

        Args:
            data: Dictionary with expected keys (file_name, text, etc.).

        Returns:
            A new ContractSchema instance.
        """
        return cls(**data)