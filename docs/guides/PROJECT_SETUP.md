# Project Setup

## Board Setup

Create a GitHub project board with these columns:

1. Backlog
2. Todo
3. In Progress
4. Review
5. Done

Map issue state transitions directly to these columns so each issue moves through a single, visible lifecycle.

## Milestones

Create the following repository milestones:

- Week 1: Data + OCR
- Week 2: NER + Clause Classification
- Week 3: Risk Scoring + Vector Search
- Week 4: API + Deployment + Testing

Assign each issue from `github-issues-backlog.md` to one milestone.

## Pull Request Workflow

1. Create work in the assigned feature branch.
2. Keep commits focused and scoped to one issue.
3. Open a pull request targeting `develop`.
4. Ensure CI is green (`ruff check .` and `pytest -q`).
5. Link the related issue in the PR description.
6. Merge after approvals and successful checks.

## Code Review Workflow

1. Request review from at least one teammate.
2. Reviewers validate scope, correctness, tests, and docs impact.
3. Resolve comments with follow-up commits.
4. Re-request review after substantial updates.
5. Merge only when approvals are complete and checks pass.

## Branch Ownership

- Lakshya -> Dataset & Cleaning (`feature/dataset-cleaning`)
- Ahmad -> OCR Pipeline (`feature/ocr-pipeline`)
- Sahasra -> NER Extraction (`feature/ner-extraction`)
- Sandeep -> FastAPI Backend (`feature/fastapi-backend`)
- Azmat -> Clause Classification & Risk Scoring (`feature/clause-risk-scoring`, `feature/integration-testing`)

## Daily Commit Policy

- Each owner should commit at least once per working day on active tasks.
- Each daily commit should include tests or validation updates when applicable.
- Use clear commit messages tied to the active issue.
- Push work daily to keep integration risk low and progress visible.
