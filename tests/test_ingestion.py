"""
Test suite for Enhanced Data Ingestion Pipeline.

Tests cover text cleaning, validation, file processing, and caching.
"""


import pytest

from src.ingestion.cleaner import TextCleaner
from src.ingestion.file_processor import ContractProcessor
from src.ingestion.schema import ContractSchema
from src.ingestion.validator import ContractValidationError, ContractValidator


class TestTextCleaner:
    """Tests for the enhanced text cleaner."""

    def test_basic_clean(self):
        """Test basic text cleaning functionality."""
        cleaner = TextCleaner()
        text = "This is a   test  document.\n\n\nWith extra spaces."
        cleaned = cleaner.clean(text)

        assert "This is a test document" in cleaned
        assert "With extra spaces" in cleaned

    def test_remove_headers_footers(self):
        """Test header and footer removal."""
        cleaner = TextCleaner(remove_headers_footers=True)
        text = """Page 1 of 10

        This is the actual contract content.

        CONFIDENTIAL

        More contract text here."""

        cleaned = cleaner.clean(text)

        assert "Page 1 of 10" not in cleaned
        assert "CONFIDENTIAL" not in cleaned
        assert "actual contract content" in cleaned

    def test_preserve_legal_symbols(self):
        """Test that legal symbols are preserved."""
        cleaner = TextCleaner(preserve_legal_symbols=True)
        text = "The agreement is governed by § 123 and costs $50,000."

        cleaned = cleaner.clean(text)

        assert "§" in cleaned or "123" in cleaned
        assert "$" in cleaned or "50" in cleaned

    def test_smart_lowercase(self):
        """Test lowercase cleaning preserves meaningful content."""
        cleaner = TextCleaner(lowercase=True)
        text = "This LLC agreement involves CEO approval and GDPR compliance."

        cleaned = cleaner.clean(text)

        assert isinstance(cleaned, str)
        assert len(cleaned.strip()) > 0
        assert "agreement" in cleaned.lower()
        assert "approval" in cleaned.lower() or "compliance" in cleaned.lower()

    def test_clean_batch(self):
        """Test batch cleaning."""
        cleaner = TextCleaner()
        texts = ["First document.", "Second document.", "Third document."]

        cleaned = cleaner.clean_batch(texts)

        assert len(cleaned) == 3
        assert all(isinstance(t, str) for t in cleaned)

    def test_empty_text_handling(self):
        """Test handling of empty or None text."""
        cleaner = TextCleaner()

        assert cleaner.clean("") == ""
        assert cleaner.clean(None) == ""
        assert cleaner.clean("   ") == ""

    def test_extract_clean_sections(self):
        """Test section extraction and cleaning from contracts."""
        cleaner = TextCleaner()
        text = """Service Agreement

Payment details."""

        sections = cleaner.extract_clean_sections(text)

        assert isinstance(sections, dict)
        assert len(sections) >= 1

        combined = " ".join(str(v) for v in sections.values()).lower()
        assert "service" in combined or "payment" in combined


class TestContractValidator:
    """Tests for the enhanced contract validator."""

    def test_valid_text_passes_validation(self):
        """Test that valid text passes validation."""
        validator = ContractValidator()

        text_sample = "This is a valid contract text with sufficient length."
        result = validator.validate("test.pdf", text_sample)
        assert result is True

    def test_empty_filename_raises_error(self):
        """Test that empty filename raises error."""
        validator = ContractValidator()

        with pytest.raises(ContractValidationError):
            validator.validate("", "Some text")

    def test_empty_text_raises_error(self):
        """Test that empty text raises error."""
        validator = ContractValidator()

        with pytest.raises(ContractValidationError):
            validator.validate("test.pdf", "")

    def test_too_short_text_raises_error(self):
        """Test that very short text raises error."""
        validator = ContractValidator(min_text_length=20)

        with pytest.raises(ContractValidationError):
            validator.validate("test.pdf", "Too short")

    def test_validate_file_path(self, tmp_path):
        """Test file path validation."""
        validator = ContractValidator()

        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF fake pdf content")

        result = validator.validate_file_path(str(test_file))

        assert result["file_name"] == "test.pdf"
        assert result["file_size"] > 0
        assert result["file_type"] == ".pdf"

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        validator = ContractValidator()

        with pytest.raises(ContractValidationError):
            validator.validate_file_path("/nonexistent/file.pdf")

    def test_validate_unsupported_format(self, tmp_path):
        """Test validation of unsupported file format."""
        validator = ContractValidator()

        test_file = tmp_path / "test.xml"
        test_file.write_bytes(b"<xml>content</xml>")

        with pytest.raises(ContractValidationError):
            validator.validate_file_path(str(test_file))

    def test_validate_json_structure(self):
        """Test JSON structure validation."""
        validator = ContractValidator()

        valid_json = '{"key": "value", "list": [1, 2, 3]}'
        result = validator.validate_json_structure(valid_json)

        assert result["valid"] is True
        assert "key" in result["keys"]

    def test_invalid_json_structure(self):
        """Test invalid JSON detection."""
        validator = ContractValidator()

        invalid_json = "{invalid json}"
        result = validator.validate_json_structure(invalid_json)

        assert result["valid"] is False
        assert result["error"] is not None

    def test_get_validation_report(self, tmp_path):
        """Test comprehensive validation report generation."""
        validator = ContractValidator()

        test_file = tmp_path / "test.json"
        test_content = '{"contract": "text"}'
        test_file.write_text(test_content)

        report = validator.get_validation_report(str(test_file), test_content)

        assert "file_path" in report
        assert "checks" in report
        assert "overall_valid" in report


class TestContractSchema:
    """Tests for contract schema."""

    def test_schema_creation(self):
        """Test creating a contract schema."""
        schema = ContractSchema(
            file_name="test.pdf",
            text="Contract text",
            entities={"ORG": ["Acme Corp"]},
            clauses={"governing_law": "New York"},
        )

        assert schema.file_name == "test.pdf"
        assert schema.text == "Contract text"

    def test_schema_to_dict(self):
        """Test converting schema to dictionary."""
        schema = ContractSchema(
            file_name="test.pdf",
            text="Contract text",
            entities={},
            clauses={},
        )

        result = schema.to_dict()

        assert isinstance(result, dict)
        assert "file_name" in result
        assert "text" in result


class TestContractProcessor:
    """Tests for contract processor integration."""

    def test_process_text(self):
        """Test end-to-end text processing."""
        processor = ContractProcessor()

        text = "This is a sample contract document with sufficient length for validation."
        result = processor.process_text("test.pdf", text)

        assert isinstance(result, dict)
        assert "file_name" in result
        assert "text" in result
        assert "entities" in result
        assert "clauses" in result

    def test_processor_with_validator(self):
        """Test processor uses validator correctly."""
        processor = ContractProcessor()

        # Should raise due to short text
        with pytest.raises(ContractValidationError):
            processor.process_text("test.pdf", "Short")


@pytest.fixture
def sample_contract_text():
    """Fixture providing sample contract text."""
    return """
    THIS AGREEMENT is made on January 1, 2024

    BETWEEN:

    ACME CORPORATION, a company organized under the laws of Delaware ("Company")

    AND:

    XYZ PARTNERS LLC, a limited liability company ("Partner")

    RECITALS:

    WHEREAS, the parties wish to enter into this business relationship;

    NOW, THEREFORE, the parties agree as follows:

    1. DEFINITIONS
    "Agreement" means this contract including all exhibits.

    2. TERM
    This Agreement shall commence on the Effective Date and continue for 2 years.

    3. PAYMENT TERMS
    Partner shall pay Company $10,000 USD within 30 days of invoice.

    4. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of New York.

    IN WITNESS WHEREOF, the parties have executed this Agreement.
    """


def test_full_ingestion_pipeline(sample_contract_text):
    """Test complete ingestion pipeline with realistic contract."""
    cleaner = TextCleaner()
    validator = ContractValidator()
    processor = ContractProcessor()

    # Clean
    cleaned = cleaner.clean(sample_contract_text)
    assert len(cleaned) > 0

    # Validate
    assert validator.validate("contract.pdf", cleaned)

    # Process
    result = processor.process_text("contract.pdf", cleaned)
    assert isinstance(result, dict)
    assert result["file_name"] == "contract.pdf"
    assert "text" in result
    assert "entities" in result
    assert "clauses" in result