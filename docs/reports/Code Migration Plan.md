# Code Migration Plan

This document outlines the migration plan for existing files to their target locations, ensuring a standardized and organized project structure.

## Target Structure Overview

- `src/config.py`: Centralized configuration.
- `src/data_loader.py`: Handles data loading.
- `src/preprocess_cuad.py`: Preprocessing logic for the CUAD dataset.
- `src/ocr_pipeline.py`: OCR pipeline implementation.
- `src/train.py`: Model training script.
- `src/app/main.py`: Main FastAPI application entry point.
- `notebooks/`: Directory for Jupyter notebooks.

## Migration Mapping

| Existing File/Module | Target Location/Action | Notes |
|---|---|---|
| `src/utils/config.py` | `src/config.py` | Rename and move for centralized configuration. |
| (New File) | `src/data_loader.py` | Create a placeholder file. Data loading logic might be extracted from existing services or notebooks. |
| (New File) | `src/preprocess_cuad.py` | Create a placeholder file. Preprocessing logic might be extracted from existing services or notebooks, especially from `feature/dataset-cleaning` branch. |
| `src/ocr/service.py` | `src/ocr_pipeline.py` | Rename and move. Consolidate OCR-related logic here. |
| (New File) | `src/train.py` | Create a placeholder file. Training logic will be consolidated here, potentially from `src/clause_classifier/service.py` or `src/ner/service.py`. |
| `src/api/main.py` | `src/app/main.py` | Move to `src/app/` directory to encapsulate the FastAPI application. |
| (New Directory) | `notebooks/` | Create this directory. |
| (New File) | `notebooks/explore_cuad.ipynb` | Create a placeholder notebook. |
| (New File) | `notebooks/train_first_run.ipynb` | Create a placeholder notebook. |
