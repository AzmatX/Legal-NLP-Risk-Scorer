# Merge Plan to be implemented by 26 June 2026

This document outlines the proposed merge strategy for integrating feature branches into the `develop` branch, and finally `develop` into `main`. It identifies the merge order, files affected, expected conflicts, and the resolution strategy for each step.

## Merge Order

1.  `feature/dataset-cleaning` → `develop`
2.  `feature/ocr-pipeline` → `develop`
3.  `feature/ner-extraction` → `develop`
4.  `feature/fastapi-backend` → `develop`
5.  `feature/integration-testing` → `develop`
6.  `feature/clause-risk-scoring` → `develop`
7.  `develop` → `main`

## Detailed Merge Strategy

### 1. `feature/dataset-cleaning` → `develop`

**Files Affected:**
-   `docs/DATASET_VERSIONING.md`
-   `src/ingestion/cleaner.py`
-   `src/ingestion/cuad_loader.py`
-   `src/ingestion/file_processor.py`
-   `src/ingestion/schema.py`
-   `src/ingestion/validator.py`
-   `test_day1.py`
-   `test_day2.py`
-   `test_day3_cuad_parser.py`

**Expected Conflicts:**
-   Potential conflicts in `src/__init__.py` if both branches modified it.
-   Logical conflicts with the placeholder files `src/data_loader.py` and `src/preprocess_cuad.py` in `develop`.

**Resolution Strategy:**
-   Merge `docs/DATASET_VERSIONING.md` directly.
-   Integrate the logic from `src/ingestion/cuad_loader.py`, `src/ingestion/cleaner.py`, `src/ingestion/file_processor.py`, `src/ingestion/schema.py`, and `src/ingestion/validator.py` into `src/data_loader.py` and `src/preprocess_cuad.py` in `develop`. Prioritize the more complete implementations from `feature/dataset-cleaning`.
-   Move the test files (`test_day1.py`, `test_day2.py`, `test_day3_cuad_parser.py`) into the `tests/` directory and rename them to follow a consistent naming convention (e.g., `tests/test_dataset_cleaning.py`).

### 2. `feature/ocr-pipeline` → `develop`

**Files Affected:**
-   `cleaned_sample.png`
-   `import glob`
-   `sample.png`
-   `src/ocr_test.py`
-   `temp_processed.png`

**Expected Conflicts:**
-   Potential conflicts if `src/ocr_pipeline.py` in `develop` (which was moved from `src/ocr/service.py`) has been modified, and `feature/ocr-pipeline` introduces new OCR logic.

**Resolution Strategy:**
-   Integrate the OCR logic from `feature/ocr-pipeline` into the existing `src/ocr_pipeline.py` in `develop`. Prioritize the more advanced implementation.
-   Move image files (`cleaned_sample.png`, `sample.png`, `temp_processed.png`) to a dedicated `data/ocr_samples/` directory or similar, if they are examples or test data.
-   Remove `import glob` if it's a misplaced file or integrate its content if it's a script.
-   Move `src/ocr_test.py` to `tests/test_ocr_pipeline.py`.

### 3. `feature/ner-extraction` → `develop`

**Files Affected:**
-   `src/ingestion/download_cuad.py`
-   `src/ingestion/extract_text.py`
-   `src/ner/tokenize_text.py`
-   `src/utils/preprocess_text.py`
-   `src/utils/save_json.py`

**Expected Conflicts:**
-   Conflicts with `src/data_loader.py` and `src/preprocess_cuad.py` due to overlapping ingestion and preprocessing logic.
-   Conflicts with `src/ner/service.py` if both branches modified it.

**Resolution Strategy:**
-   Integrate `src/ingestion/download_cuad.py` and `src/ingestion/extract_text.py` into `src/data_loader.py` and `src/preprocess_cuad.py` in `develop`. Consolidate and remove redundancies.
-   Integrate `src/ner/tokenize_text.py` into `src/ner/service.py`.
-   Review `src/utils/preprocess_text.py` and `src/utils/save_json.py`. If their functionality is generic, move them to `src/utils/` (if not already there) or integrate their logic into existing modules like `src/preprocess_cuad.py` or `src/data_loader.py`.

### 4. `feature/fastapi-backend` → `develop`

**Files Affected:**
-   None (based on analysis).

**Expected Conflicts:**
-   None, as no unique commits were found.

**Resolution Strategy:**
-   Perform a fast-forward merge. No manual intervention expected.

### 5. `feature/integration-testing` → `develop`

**Files Affected:**
-   None (based on analysis).

**Expected Conflicts:**
-   None, as no unique commits were found.

**Resolution Strategy:**
-   Perform a fast-forward merge. No manual intervention expected.

### 6. `feature/clause-risk-scoring` → `develop`

**Files Affected:**
-   `README.md`

**Expected Conflicts:**
-   Potential conflicts in `README.md` if `develop` also modified it.

**Resolution Strategy:**
-   Manually resolve any conflicts in `README.md`, prioritizing the most up-to-date and comprehensive content.

### 7. `develop` → `main`

**Files Affected:**
-   All files modified during the previous merges into `develop`.

**Expected Conflicts:**
-   Minimal conflicts if `main` has not diverged significantly from `develop` since the last merge.

**Resolution Strategy:**
-   Perform a merge with a `--no-ff` flag to preserve merge history. Resolve any minor conflicts that may arise.
