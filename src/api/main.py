from fastapi import FastAPI, File, HTTPException, UploadFile

from clause_classifier.service import classify_clause
from ingestion.service import validate_contract_file
from ner.service import extract_legal_entities
from ocr.service import extract_text_from_document
from risk_scoring.service import score_contract
from utils.config import settings
from vector_store.service import semantic_search

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
    text = extract_text_from_document(payload)
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
