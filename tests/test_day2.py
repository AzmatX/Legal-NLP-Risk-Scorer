import pytest

from src.ingestion.file_processor import ContractProcessor
from src.ingestion.validator import ContractValidationError


class TestDay2ContractProcessor:
    def test_valid_contract_processing(self):
        processor = ContractProcessor()

        valid_text = """
        This Agreement is made between ABC Corp and XYZ Ltd.
        Confidentiality must be maintained throughout the contract term.
        """

        result = processor.process_text("contract.pdf", valid_text)

        assert isinstance(result, dict)
        assert result["file_name"] == "contract.pdf"
        assert "text" in result
        assert "entities" in result
        assert "clauses" in result

    def test_empty_contract_raises_validation_error(self):
        processor = ContractProcessor()

        with pytest.raises(ContractValidationError, match="Contract text is empty"):
            processor.process_text("contract.pdf", "")
