from fastapi import FastAPI, File, HTTPException, UploadFile

from src.clause_classifier.service import classify_clause
from src.ingestion.service import validate_contract_file
from src.ner.service import extract_legal_entities
from src.ocr.service import extract_text_from_document
from src.risk_scoring.service import score_contract
from src.utils.config import settings
from src.vector_store.service import semantic_search

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/contracts/analyze")
async def analyze_contract(file: UploadFile = File(...)) -> dict[str, object]:
    try:
        validate_contract_file(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload = await file.read()
    text_result = extract_text_from_document(payload, is_file_path=False)
    text = text_result.get("full_text", "") if isinstance(text_result, dict) else text_result
    entities = extract_legal_entities(text)
    clause = classify_clause(text)
    risk = score_contract([clause])
    return {
        "filename": file.filename,
        "entities": entities,
        "clauses": [clause],
        "risk": risk,
    }


@app.get("/contracts/search")
def search_contracts(query: str) -> dict[str, object]:
    return {"query": query, "results": semantic_search(query)}
