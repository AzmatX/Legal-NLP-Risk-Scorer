# Development Guide

## Repository Structure

- `src/ingestion` — upload + file validation
- `src/ocr` — OCR pipeline
- `src/ner` — legal entity extraction
- `src/clause_classifier` — clause classification
- `src/risk_scoring` — risk engine
- `src/vector_store` — semantic search abstraction
- `src/api` — FastAPI app
- `src/tasks` — Celery app and workers
- `src/utils` — shared config/utilities

## Branch Strategy Setup

```bash
git checkout -b develop
git checkout -b feature/dataset-cleaning
git checkout -b feature/ocr-pipeline
git checkout -b feature/ner-extraction
git checkout -b feature/clause-risk-scoring
git checkout -b feature/integration-testing
```

## Milestones

1. **Week 1** — Data + OCR
2. **Week 2** — NER + Clause Classification
3. **Week 3** — Risk Scoring + Vector Search
4. **Week 4** — API + Deployment + Testing

## First Commit Plan

1. Bootstrap repo structure and standards.
2. Add FastAPI + Celery scaffolds.
3. Add CI workflows and Docker.
4. Add templates, backlog, and documentation.

## Daily Commit Roadmap

### Ahmad (Dataset)
- Day 1: Dataset loader + schema
- Day 2: Cleaning and validation
- Day 3: CUAD parsing tests
- Day 4: Dataset versioning docs

### Sahasra (OCR)
- Day 1: OCR service abstraction
- Day 2: PDF OCR adapter
- Day 3: DOCX extraction path
- Day 4: OCR benchmark report

### Sandeep (NER)
- Day 1: NER baseline pipeline
- Day 2: Entity label mapping
- Day 3: Evaluation script
- Day 4: Model-card notes

### Azmat (Classification/Risk/Integration)
- Day 1: Clause classifier baseline
- Day 2: Risk scoring logic
- Day 3: API contract analysis endpoint integration
- Day 4: End-to-end integration tests
