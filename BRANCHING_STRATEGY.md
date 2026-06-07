# Branching Strategy

## Long-Lived Branches

- `develop` is the integration branch for all completed feature work.
- Feature branches should be rebased or merged with `develop` regularly.

## Feature Branches and Ownership

- `feature/dataset-cleaning` — Lakshya
- `feature/ocr-pipeline` — Ahmad
- `feature/ner-extraction` — Sahasra
- `feature/fastapi-backend` — Sandeep
- `feature/clause-risk-scoring` — Azmat
- `feature/integration-testing` — Azmat

## Branch Creation

```bash
git checkout -b develop
git checkout -b feature/dataset-cleaning
git checkout -b feature/ocr-pipeline
git checkout -b feature/ner-extraction
git checkout -b feature/fastapi-backend
git checkout -b feature/clause-risk-scoring
git checkout -b feature/integration-testing
```

## Merge Rules

- Open pull requests from feature branches into `develop`.
- Require at least one reviewer approval before merging.
- Require passing CI checks (`ruff check .` and `pytest -q`).
- Keep pull requests focused on one branch scope.
