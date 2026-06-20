# Repository Audit Report

## 1. Existing Directory Structure

```
.
├── BRANCHING_STRATEGY.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DEVELOPMENT_GUIDE.md
├── Dockerfile
├── PROJECT_SETUP.md
├── README.md
├── docker-compose.yml
├── github-issues-backlog.md
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── main.py
│   ├── clause_classifier
│   │   ├── __init__.py
│   │   └── service.py
│   ├── ingestion
│   │   ├── __init__.py
│   │   └── service.py
│   ├── ner
│   │   ├── __init__.py
│   │   └── service.py
│   ├── ocr
│   │   ├── __init__.py
│   │   └── service.py
│   ├── risk_scoring
│   │   ├── __init__.py
│   │   └── service.py
│   ├── tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── worker.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── config.py
│   └── vector_store
│       ├── __init__.py
│       └── service.py
└── tests
    └── test_api.py
```

## 2. Existing Python Modules

- `src/__init__.py`
- `src/api/__init__.py`
- `src/api/main.py`
- `src/clause_classifier/__init__.py`
- `src/clause_classifier/service.py`
- `src/ingestion/__init__.py`
- `src/ingestion/service.py`
- `src/ner/__init__.py`
- `src/ner/service.py`
- `src/ocr/__init__.py`
- `src/ocr/service.py`
- `src/risk_scoring/__init__.py`
- `src/risk_scoring/service.py`
- `src/tasks/__init__.py`
- `src/tasks/celery_app.py`
- `src/tasks/worker.py`
- `src/utils/__init__.py`
- `src/utils/config.py`
- `src/vector_store/__init__.py`
- `src/vector_store/service.py`
- `tests/test_api.py`

## 3. Existing Notebooks

No notebooks found in the current directory structure.

## 4. OCR-related files

- `src/ocr/__init__.py`
- `src/ocr/service.py`

## 5. Dataset-related files

No explicit dataset files found in the current directory structure. The `feature/dataset-cleaning` branch suggests there might be dataset-related work.

## 6. FastAPI files

- `src/api/main.py`

## 7. Training files

No explicit training files found in the current directory structure. The `src/clause_classifier/service.py` and `src/ner/service.py` might contain training-related logic.

## 8. Tests

- `tests/test_api.py`

## 9. Duplicates, Obsolete Files, Misplaced Files, Missing Files

- **Duplicates:** None immediately apparent from the file listing.
- **Obsolete Files:** None immediately apparent.
- **Misplaced Files:** `src/utils/config.py` should ideally be `src/config.py` for easier access and standardization.
- **Missing Files:**
    - `src/config.py`: A centralized configuration file is missing (currently `src/utils/config.py`).
    - `src/data_loader.py`: A dedicated data loading module is missing.
    - `src/preprocess_cuad.py`: A dedicated preprocessing module for CUAD dataset is missing.
    - `src/train.py`: A dedicated training script is missing.
    - `notebooks/`: Directory for notebooks is missing. Expected `explore_cuad.ipynb` and `train_first_run.ipynb`.
