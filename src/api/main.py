from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.clause_classifier.service import classify_contract
from src.ingestion.service import validate_contract_file
from src.ner.service import extract_legal_entities
from src.ocr.service import extract_text_from_document
from src.risk_scoring.service import score_contract
from src.utils.config import settings

# ---------- Lifespan: Load heavy models once ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Pre-load NER/Classifier models (avoid lazy loading per request)
    print("🚀 Loading NER and Classifier models on startup...")
    from src.ner.service import _get_default_processor
    from src.clause_classifier.service import ClauseClassifier
    _get_default_processor()  # Load spaCy
    ClauseClassifier()        # Load transformer (or dummy)
    print("✅ Models loaded!")
    yield
    # Shutdown: Cleanup if needed
    print("🛑 Shutting down...")

# ---------- FastAPI App ----------
app = FastAPI(
    title=settings.APP_NAME,           # ✅ FIX: Uppercase APP_NAME
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ---------- CORS (Essential for Frontend Demo) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health Check ----------
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME}

# ---------- Analyze Contract ----------
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

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from document.")

    # 2. Extract entities
    entities = extract_legal_entities(text)

    # 3. Clause segmentation + classification
    clause_result = classify_contract(text)

    # 4. Risk assessment
    risk_assessment = score_contract(clause_result)

    # 5. Build final response
    return {
        "filename": file.filename,
        "entities": entities,
        "clauses": clause_result["clauses"],
        "summary": clause_result["summary"],
        "risk_factors": clause_result["risk_factors"],
        "risk": risk_assessment,
    }