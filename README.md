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

- `main`
- `develop`
- `feature/dataset-cleaning`
- `feature/ocr-pipeline`
- `feature/ner-extraction`
- `feature/clause-risk-scoring`
- `feature/integration-testing`

> Branch creation is documented in `DEVELOPMENT_GUIDE.md` for manual execution.

## Team Ownership

- **Ahmad** — Dataset Processing & Cleaning
- **Sahasra** — OCR Pipeline
- **Sandeep** — NER Extraction
- **Azmat** — Clause Classification, Risk Scoring, Integration
