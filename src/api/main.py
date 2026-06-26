from fastapi import FastAPI, File, HTTPException, UploadFile

from src.clause_classifier.service import classify_contract
from src.ingestion.service import validate_contract_file
from src.ner.service import extract_legal_entities
from src.ocr.service import extract_text_from_document
from src.risk_scoring.service import score_contract
from src.utils.config import settings

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

    # 1. Read and extract text
    payload = await file.read()
    text_result = extract_text_from_document(payload, is_file_path=False)
    text = text_result.get("full_text", "") if isinstance(text_result, dict) else text_result

    # 2. Extract entities
    entities = extract_legal_entities(text)

    # 3. Clause segmentation + classification
    clause_result = classify_contract(text)

    # 4. Risk assessment (new enhanced version)
    risk_assessment = score_contract(clause_result)

    # 5. Build final response
    return {
        "filename": file.filename,
        "entities": entities,
        "clauses": clause_result["clauses"],
        "summary": clause_result["summary"],
        "risk_factors": clause_result["risk_factors"],
        "risk": risk_assessment,  # includes score, level, breakdown, missing, recommendations
    }
