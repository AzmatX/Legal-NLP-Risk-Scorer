import logging
from typing import Any

from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


# ---------- Health check (lightweight) ----------
@celery_app.task(name="tasks.healthcheck")
def healthcheck() -> str:
    return "ok"


# ---------- Heavy background task ----------
@celery_app.task(name="tasks.process_contract", bind=True)
def process_contract_background(self, file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Background task to process contract asynchronously.
    This is called by the API for long-running documents.
    """
    logger.info(f"Starting background processing for: {filename}")
    self.update_state(state="PROGRESS", meta={"status": "Extracting text..."})

    # Import heavy modules ONLY inside the task (so worker starts fast)
    from src.clause_classifier.service import classify_contract
    from src.ner.service import extract_legal_entities
    from src.ocr.service import extract_text_from_document
    from src.risk_scoring.service import score_contract

    try:
        # 1. OCR
        self.update_state(state="PROGRESS", meta={"status": "OCR in progress..."})
        text_result = extract_text_from_document(file_content, is_file_path=False)
        text = text_result.get("full_text", "") if isinstance(text_result, dict) else text_result

        if not text:
            raise ValueError("Empty text extracted.")

        # 2. NER
        self.update_state(state="PROGRESS", meta={"status": "Extracting entities..."})
        entities = extract_legal_entities(text)

        # 3. Clause Classification
        self.update_state(state="PROGRESS", meta={"status": "Classifying clauses..."})
        clause_result = classify_contract(text)

        # 4. Risk Scoring
        self.update_state(state="PROGRESS", meta={"status": "Scoring risk..."})
        risk_assessment = score_contract(clause_result)

        return {
            "status": "SUCCESS",
            "filename": filename,
            "entities": entities,
            "clauses": clause_result["clauses"],
            "summary": clause_result["summary"],
            "risk": risk_assessment,
        }

    except Exception as e:
        logger.error(f"Task failed for {filename}: {e}")
        return {"status": "FAILURE", "filename": filename, "error": str(e)}
