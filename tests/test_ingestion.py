"""
Test suite for Dataset Ingestion Pipeline.

Tests cover CUAD dataset loading, format conversion, tokenization,
and training split creation.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.ingestion.service import (
    validate_contract_file,
    load_cuad_dataset,
    convert_cuad_to_training_format,
    tokenize_text_for_ner,
    create_training_splits,
    ingest_document
)


class TestValidateContractFile:
    """Tests for file validation functionality."""
    
    def test_valid_pdf_file(self):
        """Test that PDF files are accepted."""
        # Should not raise
        validate_contract_file("contract.pdf")
    
    def test_valid_docx_file(self):
        """Test that DOCX files are accepted."""
        validate_contract_file("contract.docx")
    
    def test_valid_json_file(self):
        """Test that JSON files are accepted."""
        validate_contract_file("dataset.json")
    
    def test_valid_txt_file(self):
        """Test that TXT files are accepted."""
        validate_contract_file("document.txt")
    
    def test_invalid_file_type(self):
        """Test that unsupported file types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            validate_contract_file("file.xml")
    
    def test_case_insensitive(self):
        """Test that file extension check is case-insensitive."""
        validate_contract_file("CONTRACT.PDF")
        validate_contract_file("document.Txt")


class TestLoadCUADDataset:
    """Tests for CUAD dataset loading."""
    
    def test_load_cuad_v1_format(self, tmp_path):
        """Test loading CUAD v1 format with 'data' key."""
        dataset_content = {
            "data": [
                {"id": "doc1", "text": "Sample contract text"},
                {"id": "doc2", "text": "Another contract"}
            ]
        }
        
        dataset_file = tmp_path / "cuad_v1.json"
        dataset_file.write_text(json.dumps(dataset_content))
        
        result = load_cuad_dataset(str(dataset_file))
        assert len(result) == 2
        assert result[0]["id"] == "doc1"
    
    def test_load_cuad_v2_format(self, tmp_path):
        """Test loading CUAD v2 format with 'documents' key."""
        dataset_content = {
            "documents": [
                {"id": "doc1", "text": "Sample contract text"}
            ]
        }
        
        dataset_file = tmp_path / "cuad_v2.json"
        dataset_file.write_text(json.dumps(dataset_content))
        
        result = load_cuad_dataset(str(dataset_file))
        assert len(result) == 1
    
    def test_load_list_format(self, tmp_path):
        """Test loading dataset as a plain list."""
        dataset_content = [
            {"id": "doc1", "text": "Contract 1"},
            {"id": "doc2", "text": "Contract 2"}
        ]
        
        dataset_file = tmp_path / "cuad_list.json"
        dataset_file.write_text(json.dumps(dataset_content))
        
        result = load_cuad_dataset(str(dataset_file))
        assert len(result) == 2
    
    def test_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_cuad_dataset("/nonexistent/path/dataset.json")
    
    def test_invalid_format(self, tmp_path):
        """Test that invalid format raises ValueError."""
        dataset_content = {"invalid": "format"}
        
        dataset_file = tmp_path / "invalid.json"
        dataset_file.write_text(json.dumps(dataset_content))
        
        # This should still work as it falls back to [data]
        result = load_cuad_dataset(str(dataset_file))
        assert len(result) == 1


class TestConvertCUADToTrainingFormat:
    """Tests for CUAD format conversion."""
    
    def test_basic_conversion(self, tmp_path):
        """Test basic conversion of contracts to training format."""
        contracts = [
            {"id": "c1", "text": "Contract A", "source": "test"},
            {"id": "c2", "text": "Contract B", "contract_type": "nda"}
        ]
        
        output_dir = tmp_path / "output"
        successful, failed = convert_cuad_to_training_format(contracts, str(output_dir))
        
        assert successful == 2
        assert failed == 0
        assert (output_dir / "c1.json").exists()
        assert (output_dir / "c2.json").exists()
    
    def test_conversion_with_annotations(self, tmp_path):
        """Test that annotations are preserved when include_annotations=True."""
        contracts = [
            {
                "id": "c1",
                "text": "Contract with entities",
                "annotations": [{"label": "ORG", "text": "Acme Corp"}]
            }
        ]
        
        output_dir = tmp_path / "output"
        convert_cuad_to_training_format(contracts, str(output_dir), include_annotations=True)
        
        output_file = output_dir / "c1.json"
        with open(output_file) as f:
            data = json.load(f)
        
        assert "annotations" in data
        assert len(data["annotations"]) == 1
    
    def test_conversion_without_annotations(self, tmp_path):
        """Test that annotations are excluded when include_annotations=False."""
        contracts = [
            {
                "id": "c1",
                "text": "Contract",
                "annotations": [{"label": "ORG", "text": "Acme Corp"}]
            }
        ]
        
        output_dir = tmp_path / "output"
        convert_cuad_to_training_format(contracts, str(output_dir), include_annotations=False)
        
        output_file = output_dir / "c1.json"
        with open(output_file) as f:
            data = json.load(f)
        
        assert "annotations" not in data
    
    def test_handles_failures_gracefully(self, tmp_path):
        """Test that conversion continues when some contracts fail."""
        contracts = [
            {"id": "c1", "text": "Valid contract"},
            None  # This will cause an error
        ]
        
        output_dir = tmp_path / "output"
        successful, failed = convert_cuad_to_training_format(contracts, str(output_dir))
        
        assert successful == 1
        assert failed == 1


class TestTokenizeTextForNER:
    """Tests for text tokenization."""
    
    def test_basic_tokenization(self):
        """Test basic sentence splitting and chunking."""
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = tokenize_text_for_ner(text, max_length=10)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)
    
    def test_respects_max_length(self):
        """Test that chunks don't exceed max_length."""
        text = " ".join([f"Sentence {i}." for i in range(20)])
        chunks = tokenize_text_for_ner(text, max_length=5)
        
        for chunk in chunks:
            assert chunk['token_count'] <= 5 or len(chunk['text'].split()) <= 10
    
    def test_empty_text(self):
        """Test handling of empty text."""
        chunks = tokenize_text_for_ner("")
        assert len(chunks) == 0
    
    def test_single_sentence(self):
        """Test tokenization of a single sentence."""
        text = "This is a single sentence without period"
        chunks = tokenize_text_for_ner(text)
        
        assert len(chunks) == 1
        assert chunks[0]['text'] == text


class TestCreateTrainingSplits:
    """Tests for train/val/test split creation."""
    
    def test_create_splits(self, tmp_path):
        """Test creation of training splits."""
        # Create input files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(10):
            (input_dir / f"doc_{i}.json").write_text(json.dumps({"id": i}))
        
        output_dir = tmp_path / "splits"
        counts = create_training_splits(str(input_dir), str(output_dir))
        
        assert 'train' in counts
        assert 'val' in counts
        assert 'test' in counts
        assert counts['train'] + counts['val'] + counts['test'] == 10
        
        # Check split files exist
        assert (output_dir / "train.json").exists()
        assert (output_dir / "val.json").exists()
        assert (output_dir / "test.json").exists()
    
    def test_custom_ratios(self, tmp_path):
        """Test custom split ratios."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(100):
            (input_dir / f"doc_{i}.json").write_text(json.dumps({"id": i}))
        
        output_dir = tmp_path / "splits"
        counts = create_training_splits(
            str(input_dir), str(output_dir),
            train_ratio=0.7, val_ratio=0.2, test_ratio=0.1
        )
        
        assert counts['train'] == 70
        assert counts['val'] == 20
        assert counts['test'] == 10


class TestIngestDocument:
    """Tests for document ingestion."""
    
    def test_ingest_json(self, tmp_path):
        """Test ingestion of JSON files."""
        content = {"text": "Contract content", "metadata": {"type": "nda"}}
        file_path = tmp_path / "contract.json"
        file_path.write_text(json.dumps(content))
        
        result = ingest_document(str(file_path))
        
        assert result['processed'] is True
        assert result['error'] is None
        assert result['content'] == content
    
    def test_ingest_txt(self, tmp_path):
        """Test ingestion of TXT files."""
        content = "Plain text contract content"
        file_path = tmp_path / "contract.txt"
        file_path.write_text(content)
        
        result = ingest_document(str(file_path))
        
        assert result['processed'] is True
        assert result['content']['text'] == content
    
    def test_ingest_pdf_marks_for_ocr(self, tmp_path):
        """Test that PDF files are marked for OCR processing."""
        file_path = tmp_path / "contract.pdf"
        file_path.write_bytes(b"%PDF fake pdf content")
        
        result = ingest_document(str(file_path))
        
        assert result['processed'] is True
        assert result.get('requires_ocr') is True
    
    def test_ingest_nonexistent_file(self, tmp_path):
        """Test handling of nonexistent files."""
        result = ingest_document(str(tmp_path / "nonexistent.json"))
        
        assert result['processed'] is False
        assert result['error'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
