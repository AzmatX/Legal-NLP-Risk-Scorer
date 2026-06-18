"""
Dataset Ingestion Pipeline for Legal Contract Analysis.

This module handles loading, parsing, and preprocessing of legal contract datasets
including CUAD format conversion and tokenization preparation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWED_SUFFIXES = {".pdf", ".docx", ".json", ".txt"}


def validate_contract_file(file_name: str) -> None:
    """Validate that the file type is supported for ingestion."""
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {suffix}. Only PDF, DOCX, JSON, and TXT files are supported")


def load_cuad_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Load CUAD dataset from JSON format.
    
    Args:
        dataset_path: Path to the CUAD dataset JSON file
        
    Returns:
        List of contract documents with annotations
    """
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"CUAD dataset not found at {dataset_path}")
    
    logger.info(f"Loading CUAD dataset from {dataset_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both CUAD v1 and v2 formats
    if isinstance(data, dict):
        if 'data' in data:
            contracts = data['data']
        elif 'documents' in data:
            contracts = data['documents']
        else:
            contracts = [data]
    elif isinstance(data, list):
        contracts = data
    else:
        raise ValueError("Invalid CUAD dataset format")
    
    logger.info(f"Loaded {len(contracts)} contracts from CUAD dataset")
    return contracts


def convert_cuad_to_training_format(
    contracts: List[Dict[str, Any]], 
    output_dir: str,
    include_annotations: bool = True
) -> Tuple[int, int]:
    """
    Convert CUAD dataset to training-ready JSON format.
    
    Args:
        contracts: List of CUAD contract documents
        output_dir: Directory to save processed files
        include_annotations: Whether to include annotation labels
        
    Returns:
        Tuple of (successful_conversions, failed_conversions)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    for idx, contract in enumerate(contracts):
        try:
            training_doc = {
                'id': contract.get('id', f'doc_{idx}'),
                'text': contract.get('text', ''),
                'metadata': {
                    'source': contract.get('source', 'unknown'),
                    'contract_type': contract.get('contract_type', 'general'),
                }
            }
            
            if include_annotations and 'annotations' in contract:
                training_doc['annotations'] = contract['annotations']
            
            if 'entities' in contract:
                training_doc['entities'] = contract['entities']
            
            output_file = output_path / f"{training_doc['id']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_doc, f, indent=2, ensure_ascii=False)
            
            successful += 1
            
        except Exception as e:
            logger.warning(f"Failed to process contract {idx}: {e}")
            failed += 1
    
    logger.info(f"Converted {successful} contracts, {failed} failed")
    return successful, failed


def tokenize_text_for_ner(text: str, max_length: int = 512) -> List[Dict[str, Any]]:
    """
    Tokenize text into sentences/chunks suitable for NER model input.
    
    Args:
        text: Raw contract text
        max_length: Maximum tokens per chunk
        
    Returns:
        List of tokenized chunks with metadata
    """
    import re
    
    # Simple sentence splitting (can be enhanced with legal-specific rules)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_tokens = sentence.split()
        sentence_length = len(sentence_tokens)
        
        if current_length + sentence_length > max_length:
            if current_chunk:
                chunks.append({
                    'text': ' '.join(current_chunk),
                    'token_count': current_length,
                    'sentence_count': len(current_chunk)
                })
            current_chunk = sentence_tokens
            current_length = sentence_length
        else:
            current_chunk.extend(sentence_tokens)
            current_length += sentence_length
    
    # Add remaining chunk
    if current_chunk:
        chunks.append({
            'text': ' '.join(current_chunk),
            'token_count': current_length,
            'sentence_count': len(current_chunk)
        })
    
    return chunks


def create_training_splits(
    input_dir: str,
    output_dir: str,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42
) -> Dict[str, int]:
    """
    Create train/val/test splits from processed dataset.
    
    Args:
        input_dir: Directory containing processed JSON files
        output_dir: Directory to save split files
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with counts for each split
    """
    import random
    
    random.seed(seed)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load all processed files
    files = list(input_path.glob('*.json'))
    random.shuffle(files)
    
    total = len(files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    train_files = files[:train_end]
    val_files = files[train_end:val_end]
    test_files = files[val_end:]
    
    # Write split manifests
    for split_name, split_files in [
        ('train.json', train_files),
        ('val.json', val_files),
        ('test.json', test_files)
    ]:
        split_data = {
            'files': [str(f.name) for f in split_files],
            'count': len(split_files)
        }
        with open(output_path / split_name, 'w') as f:
            json.dump(split_data, f, indent=2)
    
    counts = {
        'train': len(train_files),
        'val': len(val_files),
        'test': len(test_files)
    }
    
    logger.info(f"Created splits: Train={counts['train']}, Val={counts['val']}, Test={counts['test']}")
    return counts


def ingest_document(file_path: str) -> Dict[str, Any]:
    """
    Main entry point for ingesting a single document.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Processed document with metadata
    """
    path = Path(file_path)
    validate_contract_file(file_path)
    
    result = {
        'file_path': str(path),
        'file_name': path.name,
        'file_size': path.stat().st_size,
        'processed': False,
        'error': None
    }
    
    try:
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                result['content'] = json.load(f)
        elif path.suffix.lower() == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                result['content'] = {'text': f.read()}
        # PDF and DOCX handled by OCR pipeline
        else:
            result['requires_ocr'] = True
        
        result['processed'] = True
        logger.info(f"Successfully ingested {file_path}")
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Failed to ingest {file_path}: {e}")
    
    return result
