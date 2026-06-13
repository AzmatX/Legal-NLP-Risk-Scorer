# AI-Powered Contract Intelligence & Risk Scoring System

Production-ready starter repository for an enterprise NLP platform that ingests legal contracts, extracts intelligence, and serves risk analysis through APIs.

## Core Capabilities

- Upload PDF/DOCX contracts
- OCR extraction pipeline scaffold
- Legal entity extraction scaffold
- Clause classification scaffold
- Risk scoring scaffold
- Semantic search scaffold
- FastAPI APIs
- Celery task worker setup

## Tech Stack

- Python 3.11
- FastAPI + Uvicorn
- Celery
- PyTorch / Transformers / spaCy (optional ML extras)
- LangChain (optional vector extras)
- Docker + Docker Compose

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
ruff check .
uvicorn api.main:app --app-dir src --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Branch Strategy

### Main Branches
- `main` → Production-ready stable code
- `develop` → Integration branch for all completed features

### Feature Branches
- `feature/dataset-cleaning` → Lakshay
- `feature/ocr-pipeline` → Ahmad
- `feature/ner-extraction` → Sahasra
- `feature/fastapi-backend` → Sandeep
- `feature/clause-risk-scoring` → Azmat
- `feature/integration-testing` → System integration and final testing

### Merge Flow

feature/* → develop → main

### Workflow Rules

1. No direct commits to `main`.
2. All development must occur on feature branches.
3. Feature branches are merged into `develop` via Pull Requests.
4. Integration testing is performed on `develop`.
5. Only tested and approved code is merged from `develop` to `main`.
6. Every team member must push commits daily with meaningful commit messages.

> Branch creation is documented in `DEVELOPMENT_GUIDE.md` for manual execution.

## Team Ownership

| Member | Module |
|--------|--------|
| Lakshay Kundaeiya | Dataset and also Cleaning |
| Ahmad | OCR Pipeline + Risk Scoring|
| Sahasra | NER Extraction |
| Sandeep | FastAPI Backend |
| Azmat | Clause Classification + Integration |
