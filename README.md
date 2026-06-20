# Contributing Guidelines

Thank you for your interest in contributing to the AI-Powered Contract Intelligence & Risk Scoring System.

This project follows a structured development workflow to ensure code quality, maintainability, and reproducibility.

## Development Workflow

### Branch Strategy

* `main` → Stable production branch
* `develop` → Active development branch
* `feature/*` → Individual feature development

Examples:

```text
feature/ocr-pipeline
feature/ner-engine
feature/risk-scoring
feature/api-backend
```

Direct commits to `main` are not permitted.

---

## Getting Started

Clone the repository:

```bash
git clone <repository-url>
cd contract-intelligence-platform
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Code Quality Standards

Before creating a pull request:

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Format code where required.

---

## Pull Request Requirements

All pull requests should:

* Address a single feature or issue
* Include meaningful commit messages
* Pass all automated tests
* Follow repository structure conventions
* Include documentation updates when necessary

---

## Commit Message Convention

Examples:

```text
feat: add OCR preprocessing pipeline
fix: resolve import path issue in CI
docs: update project architecture
test: add NER integration tests
```

---

## Reporting Issues

When reporting an issue, include:

* Description of the problem
* Expected behavior
* Actual behavior
* Steps to reproduce
* Environment information

---

## Project Philosophy

The objective of this project is to build reliable and explainable Legal NLP systems through clean engineering practices, reproducible experimentation, and maintainable software architecture.
