# Static Validation Report

## Import Resolution Check

Attempting to import all modules to check for resolution issues and circular imports.


## Final Static Validation Results

Despite attempts to resolve import issues, the following modules failed to import:

- `src.train`: `ModuleNotFoundError: No module named 'src.train'`

This indicates that while `src` is added to `sys.path`, Python is still unable to locate `train.py` as a module within `src` when attempting to import it as `src.train`. This might be due to `train.py` not being a package (missing `__init__.py` in a parent directory if it were intended to be part of a subpackage) or an incorrect import mechanism being used in the validation script.

**Succeeded Imports:**

- `src.config`
- `src.data_loader`
- `src.preprocess_cuad`
- `src.ocr_pipeline`
- `src.app.main`
- `src.clause_classifier.service`
- `src.ingestion.service`
- `src.ner.service`
- `src.risk_scoring.service`
- `src.tasks.celery_app`
- `src.tasks.worker`
- `src.vector_store.service`

**Note:** The `app.main` module also reported a dependency warning for `python-multipart` which was subsequently installed, resolving that specific runtime issue. The `celery` related modules also required `celery` to be installed.
