# GitHub Issues Backlog (Fallback)

Direct issue/project/milestone automation may be unavailable in this environment.
Use this backlog to create GitHub issues manually.

## Project Board Columns

1. Backlog
2. Todo
3. In Progress
4. Review
5. Done

## Milestones

- Week 1: Data + OCR
- Week 2: NER + Clause Classification
- Week 3: Risk Scoring + Vector Search
- Week 4: API + Deployment + Testing

## Issues to Create

### 1) Dataset Parsing
- **Title:** Dataset Parsing with CUAD ingestion pipeline
- **Description:** Build CUAD parser, schema validation, and cleaned dataset export.
- **Labels:** `dataset`, `backend`
- **Assignee:** Ahmad
- **Milestone:** Week 1

### 2) OCR Pipeline
- **Title:** OCR pipeline for PDF/DOCX contract extraction
- **Description:** Implement OCR abstraction and adapters for scanned contracts.
- **Labels:** `ocr`, `ml`
- **Assignee:** Sahasra
- **Milestone:** Week 1

### 3) NER Extraction
- **Title:** Legal entity recognition module
- **Description:** Implement named entity extraction for legal parties and obligations.
- **Labels:** `ner`, `ml`
- **Assignee:** Sandeep
- **Milestone:** Week 2

### 4) Clause Classification
- **Title:** Clause classification baseline with Legal-RoBERTa
- **Description:** Build clause classifier service and baseline training/eval pipeline.
- **Labels:** `classification`, `ml`
- **Assignee:** Azmat
- **Milestone:** Week 2

### 5) Risk Scoring
- **Title:** Contract risk scoring engine
- **Description:** Build risk scoring framework and weighted risk policy design.
- **Labels:** `risk`, `backend`
- **Assignee:** Azmat
- **Milestone:** Week 3

### 6) Vector Search
- **Title:** Semantic search with vector store integration
- **Description:** Integrate LangChain with Pinecone or Milvus for retrieval.
- **Labels:** `vector-search`, `backend`
- **Assignee:** Azmat
- **Milestone:** Week 3

### 7) FastAPI Backend
- **Title:** FastAPI contract intelligence endpoints
- **Description:** Add upload/analyze/search endpoints with API schemas and validation.
- **Labels:** `api`, `backend`
- **Assignee:** Azmat
- **Milestone:** Week 4

### 8) Celery Integration
- **Title:** Celery async processing integration
- **Description:** Add background task pipeline for document processing and scoring.
- **Labels:** `celery`, `backend`
- **Assignee:** Azmat
- **Milestone:** Week 4

### 9) Dockerization
- **Title:** Docker and Docker Compose deployment setup
- **Description:** Build production-oriented container definitions for API + worker.
- **Labels:** `devops`, `docker`
- **Assignee:** Azmat
- **Milestone:** Week 4

### 10) Testing & Documentation
- **Title:** Testing coverage and engineering documentation
- **Description:** Expand unit/integration tests and finalize contributor docs.
- **Labels:** `testing`, `documentation`
- **Assignee:** Azmat
- **Milestone:** Week 4

## Manual Commands (if `gh` is configured locally)

```bash
# Example issue creation
# gh issue create --title "Dataset Parsing with CUAD ingestion pipeline" --body "..." --label dataset --assignee Ahmad --milestone "Week 1"
```
