# Branch Analysis Report

This report analyzes the differences between feature branches and the `develop` branch, identifying unique commits, affected files, and potential areas of conflict or duplicate work.

## Summary of Branches

- `main`: Main production branch.
- `develop`: Integration branch for new features.
- `feature/dataset-cleaning`: Focuses on dataset preparation.
- `feature/ocr-pipeline`: Focuses on OCR functionality.
- `feature/ner-extraction`: Focuses on Named Entity Recognition.
- `feature/fastapi-backend`: Focuses on the FastAPI application.
- `feature/integration-testing`: Focuses on integration tests.
- `feature/clause-risk-scoring`: Focuses on clause risk scoring.

## Branch Comparison with `develop`

### `feature/dataset-cleaning`

**Unique Commits:**
- `0ad2da5`: Day 4: add dataset versioning documentation
- `9ce2416`: fix: remove invalid mode parameter from json.load() - ruff linting fix
- `889a150`: Day 3: implement CUAD dataset parser and tests
- `93883e6`: Day 2: implemented contract cleaning and validation pipeline
- `62ed7f2`: Fix import organization issues
- `158413d`: Day 1: dataset loader, cleaning pipeline and schema definition added

**Affected Files (Added/Modified):**
- `docs/DATASET_VERSIONING.md` (Added)
- `src/ingestion/cleaner.py` (Added)
- `src/ingestion/cuad_loader.py` (Added)
- `src/ingestion/file_processor.py` (Added)
- `src/ingestion/schema.py` (Added)
- `src/ingestion/validator.py` (Added)
- `test_day1.py` (Added)
- `test_day2.py` (Added)
- `test_day3_cuad_parser.py` (Added)

**Potential Conflicts/Duplicate Work:**
- This branch introduces several new files under `src/ingestion` and new test files. Given the reorganization, there might be conflicts with the `src/data_loader.py` and `src/preprocess_cuad.py` placeholders created in `develop`. The logic from `src/ingestion/cuad_loader.py` and related files should be integrated into `src/data_loader.py` and `src/preprocess_cuad.py`.

### `feature/ocr-pipeline`

**Unique Commits:**
- `6964053`: feat: integrate opencv preprocessing and pypdf adapter into ocr pipeline
- `f3da43e`: feat: integrate basic risk scoring system with keywords dictionary
- `c0f1cec`: feat: setup core OCR pipeline with text replacement and autocorrect

**Affected Files (Added/Modified):**
- `cleaned_sample.png` (Added)
- `import glob` (Added - likely a temporary or misplaced file)
- `sample.png` (Added)
- `src/ocr_test.py` (Added)
- `temp_processed.png` (Added)

**Potential Conflicts/Duplicate Work:**
- This branch introduces new OCR-related files and images. The `src/ocr_pipeline.py` file in `develop` is a direct move from `src/ocr/service.py`. The functionality from `feature/ocr-pipeline` should be integrated into the new `src/ocr_pipeline.py`.
- `import glob` seems like a misplaced file and should be removed or integrated if it contains relevant code.

### `feature/ner-extraction`

**Unique Commits:**
- `01f4971`: Added project code into team structure

**Affected Files (Added/Modified):**
- `src/ingestion/download_cuad.py` (Added)
- `src/ingestion/extract_text.py` (Added)
- `src/ner/tokenize_text.py` (Added)
- `src/utils/preprocess_text.py` (Added)
- `src/utils/save_json.py` (Added)

**Potential Conflicts/Duplicate Work:**
- This branch adds new files to `src/ingestion` and `src/ner`. There's potential overlap with `feature/dataset-cleaning` regarding data ingestion and preprocessing. The `src/utils/preprocess_text.py` might conflict with the new `src/preprocess_cuad.py` or `src/ingestion` modules. The `src/ner/tokenize_text.py` should be integrated into `src/ner/service.py`.

### `feature/fastapi-backend`

**Unique Commits:**
- No unique commits found compared to `develop`.

**Affected Files (Added/Modified):**
- No files affected compared to `develop`.

**Potential Conflicts/Duplicate Work:**
- This branch appears to be identical to `develop` in terms of commits. It might have been merged or rebased already, or it's an empty feature branch.

### `feature/integration-testing`

**Unique Commits:**
- No unique commits found compared to `develop`.

**Affected Files (Added/Modified):**
- No files affected compared to `develop`.

**Potential Conflicts/Duplicate Work:**
- Similar to `feature/fastapi-backend`, this branch seems to be identical to `develop`.

### `feature/clause-risk-scoring`

**Unique Commits:**
- `59c0079`: Update README.md

**Affected Files (Added/Modified):**
- `README.md` (Modified)

**Potential Conflicts/Duplicate Work:**
- This branch only modifies `README.md`. This change should be easily mergeable, but care should be taken if `README.md` has also been modified on `develop` or other branches.
