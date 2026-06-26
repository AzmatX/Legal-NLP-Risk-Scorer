"""
Dataset Ingestion Pipeline for Legal Contract Analysis.

Handles loading, parsing, and preprocessing of legal contract datasets
including CUAD format conversion, tokenization, and train/val/test splitting.
"""

import json
import logging
import random
import re
from pathlib import Path
from typing import Any

# Optional dependency for better sentence splitting
try:
    import spacy

    NLP = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    HAS_SPACY = True
except ImportError:
    NLP = None
    HAS_SPACY = False

logger = logging.getLogger(__name__)

# Module‑level constants
ALLOWED_SUFFIXES: set[str] = {".pdf", ".docx", ".json", ".txt"}
DEFAULT_MAX_TOKEN_LENGTH: int = 512
DEFAULT_SPLIT_RATIOS: tuple[float, float, float] = (0.8, 0.1, 0.1)
DEFAULT_RANDOM_SEED: int = 42

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def validate_contract_file(file_name: str) -> None:
    """
    Validate that the file type is supported for ingestion.

    Args:
        file_name: Full path or name of the file.

    Raises:
        ValueError: If the file suffix is not in ALLOWED_SUFFIXES.
    """
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            f"Only {', '.join(sorted(ALLOWED_SUFFIXES))} files are supported"
        )


def load_cuad_dataset(dataset_path: str) -> list[dict[str, Any]]:
    """
    Load CUAD dataset from JSON format (v1 or v2).

    Args:
        dataset_path: Path to the CUAD dataset JSON file.

    Returns:
        List of contract documents with annotations.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON format is unrecognised.
    """
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"CUAD dataset not found at {dataset_path}")

    logger.info("Loading CUAD dataset from %s", dataset_path)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Handle both CUAD v1 (has 'data') and v2 ('documents') or a bare list
    if isinstance(data, dict):
        contracts = data.get("data") or data.get("documents")
        if contracts is None:
            # Possibly a single document wrapped in a dict
            if any(k in data for k in ("title", "text", "paragraphs")):
                contracts = [data]
            else:
                raise ValueError(
                    "Unrecognised CUAD JSON structure – missing 'data' or 'documents' key"
                )
    elif isinstance(data, list):
        contracts = data
    else:
        raise ValueError("Invalid CUAD dataset format – expected dict or list")

    logger.info("Loaded %d contracts from CUAD dataset", len(contracts))
    return contracts


def convert_cuad_to_training_format(
    contracts: list[dict[str, Any]],
    output_dir: str,
    include_annotations: bool = True,
) -> tuple[int, int]:
    """
    Convert CUAD contracts to individual training‑ready JSON files.

    Args:
        contracts: List of CUAD contract documents (as returned by load_cuad_dataset).
        output_dir: Directory where per‑document JSON files are saved.
        include_annotations: If True, include annotation labels.

    Returns:
        Tuple of (successful_conversions, failed_conversions).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    for idx, contract in enumerate(contracts):
        try:
            # Build a clean training document with defaults
            doc_id = contract.get("id") or f"doc_{idx}"
            training_doc = {
                "id": doc_id,
                "text": contract.get("text", ""),
                "metadata": {
                    "source": contract.get("source", "unknown"),
                    "contract_type": contract.get("contract_type", "general"),
                },
            }

            # Optionally include annotations and entities
            if include_annotations and "annotations" in contract:
                training_doc["annotations"] = contract["annotations"]
            if "entities" in contract:
                training_doc["entities"] = contract["entities"]

            # Write as pretty‑printed JSON
            out_file = output_path / f"{doc_id}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(training_doc, f, indent=2, ensure_ascii=False, default=str)

            successful += 1

        except Exception as e:
            logger.warning("Failed to process contract index %d: %s", idx, e)
            failed += 1

    logger.info("Converted %d contracts, %d failed", successful, failed)
    return successful, failed


def tokenize_text_for_ner(
    text: str,
    max_length: int = DEFAULT_MAX_TOKEN_LENGTH,
    use_spacy: bool = True,
) -> list[dict[str, Any]]:
    """
    Split text into chunks suitable for NER model input.
    """
    if use_spacy and HAS_SPACY:
        doc = NLP(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', text)
        sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk_words: list[str] = []
    current_length = 0
    current_sentence_count = 0  # ✅ FIX: Track sentences properly

    for sentence in sentences:
        words = sentence.split()
        sentence_len = len(words)

        if current_length + sentence_len > max_length and current_chunk_words:
            chunks.append(
                {
                    "text": " ".join(current_chunk_words),
                    "token_count": current_length,
                    "sentence_count": current_sentence_count,  # ✅ FIX: Correct count
                }
            )
            current_chunk_words = []
            current_length = 0
            current_sentence_count = 0

        current_chunk_words.extend(words)
        current_length += sentence_len
        current_sentence_count += 1  # ✅ FIX: Increment per sentence

    if current_chunk_words:
        chunks.append(
            {
                "text": " ".join(current_chunk_words),
                "token_count": current_length,
                "sentence_count": current_sentence_count,  # ✅ FIX
            }
        )

    return chunks

def create_training_splits(
    input_dir: str,
    output_dir: str,
    train_ratio: float = DEFAULT_SPLIT_RATIOS[0],
    val_ratio: float = DEFAULT_SPLIT_RATIOS[1],
    test_ratio: float = DEFAULT_SPLIT_RATIOS[2],
    seed: int = DEFAULT_RANDOM_SEED,
) -> dict[str, int]:
    """
    Create randomised train/val/test splits from a directory of JSON files.

    Args:
        input_dir: Directory containing processed JSON files.
        output_dir: Directory to save split manifest files.
        train_ratio: Proportion of files for training.
        val_ratio: Proportion for validation.
        test_ratio: Proportion for testing.
        seed: Random seed for reproducibility.

    Returns:
        Dict with keys 'train', 'val', 'test' and their counts.

    Raises:
        ValueError: If the ratios do not sum to ~1.0.
    """
    # Validate ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(
            f"Split ratios must sum to 1.0, got {total_ratio:.2f} "
            f"({train_ratio=}, {val_ratio=}, {test_ratio=})"
        )

    random.seed(seed)

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = list(input_path.glob("*.json"))
    if not files:
        logger.warning("No JSON files found in %s", input_dir)
        return {"train": 0, "val": 0, "test": 0}

    random.shuffle(files)

    total = len(files)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    splits = {
        "train": files[:train_end],
        "val": files[train_end:val_end],
        "test": files[val_end:],
    }

    # Write manifests
    for split_name, file_list in splits.items():
        manifest = {
            "files": [f.name for f in file_list],
            "count": len(file_list),
        }
        with open(output_path / f"{split_name}.json", "w") as f:
            json.dump(manifest, f, indent=2)

    counts = {k: len(v) for k, v in splits.items()}
    logger.info(
        "Created splits: Train=%d, Val=%d, Test=%d",
        counts["train"],
        counts["val"],
        counts["test"],
    )
    return counts


def ingest_document(file_path: str) -> dict[str, Any]:
    """
    Ingest a single document (JSON, TXT, PDF, DOCX) and return metadata.

    Args:
        file_path: Path to the document.

    Returns:
        Dictionary with keys:
            - file_path, file_name, processed (bool), error (Optional[str])
            - file_size (Optional[int])
            - content (for JSON/TXT) or requires_ocr (bool)
    """
    path = Path(file_path)
    result: dict[str, Any] = {
        "file_path": str(path),
        "file_name": path.name,
        "processed": False,
        "error": None,
    }

    if not path.exists():
        result["error"] = f"File not found: {file_path}"
        return result

    try:
        validate_contract_file(file_path)
        result["file_size"] = path.stat().st_size

        suffix = path.suffix.lower()
        if suffix == ".json":
            with open(path, encoding="utf-8") as f:
                result["content"] = json.load(f)
        elif suffix == ".txt":
            with open(path, encoding="utf-8") as f:
                result["content"] = {"text": f.read()}
        else:  # PDF, DOCX – to be handled by OCR pipeline
            result["requires_ocr"] = True

        result["processed"] = True
        logger.info("Successfully ingested %s", file_path)

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result["error"] = f"Parsing error: {e}"
        logger.error("Failed to parse %s: %s", file_path, e)
    except ValueError as e:  # e.g., unsupported file type
        result["error"] = str(e)
        logger.error("Validation error for %s: %s", file_path, e)
    except OSError as e:
        result["error"] = f"OS error: {e}"
        logger.error("OS error while reading %s: %s", file_path, e)

    return result
