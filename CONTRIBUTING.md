# Contributing Guide

## Setup

1. Use Python 3.11.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -e .[dev]
```

## Local Quality Checks

```bash
ruff check .
pytest -q
```

## Pull Requests

- Keep PRs focused and small.
- Ensure CI is green.
- Use the PR template.
