"""
app/routes/query.py
====================
Endpoints:
  POST /api/ask          — main Q&A
  GET  /api/health       — system status (Ollama + vector store)
  GET  /api/validate-key — test if Ollama is running
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag_pipeline import rag_pipeline
from app.services.weather_service import weather_service
from app.utils.intent import detect_intent, get_intent_label, INTENT_WEATHER
from app.utils.translator import translate_to_english, translate_from_english

router = APIRouter()


class AskRequest(BaseModel):
    query:    str        = Field(..., min_length=1)
    language: str        = Field(default="english")
    city:     str | None = Field(default=None)
    top_k:    int        = Field(default=4, ge=1, le=20)


class AskResponse(BaseModel):
    query:        str
    answer:       str
    intent:       str
    intent_label: str
    sources:      list[str]
    chunks_used:  int
    weather:      dict | None = None


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    # 1. Detect intent
    intent       = detect_intent(req.query)
    intent_label = get_intent_label(intent)

    # 2. Weather if needed
    weather_data = None
    if intent == INTENT_WEATHER and req.city:
        weather_data = weather_service.get_weather(req.city)

    # 3. Translate query to English for better embedding
    lang = req.language.lower()
    english_query = (
        translate_to_english(req.query, source_lang=lang)
        if lang not in ("english", "en") else req.query
    )

    # 4. RAG pipeline
    if not rag_pipeline.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Vector store not ready. Run: python scripts/ingest_data.py",
        )
    result = rag_pipeline.run(query=english_query, top_k=req.top_k)

    # 5. Translate answer back
    answer = result["answer"]
    if lang not in ("english", "en"):
        answer = translate_from_english(answer, target_lang=lang)

    return AskResponse(
        query        = req.query,
        answer       = answer,
        intent       = intent,
        intent_label = intent_label,
        sources      = result["sources"],
        chunks_used  = result["chunks_used"],
        weather      = weather_data,
    )


@router.get("/health")
async def health():
    from app.services.llm import llm_service
    from app.config import settings

    vs_ready     = rag_pipeline.is_ready()
    ollama_ready = llm_service.health_check()
    models       = llm_service.list_models()
    issues       = []

    if not vs_ready:
        issues.append("Vector store missing — run: python scripts/ingest_data.py")
    if not ollama_ready:
        issues.append(f"Ollama not ready — run: ollama run {settings.OLLAMA_MODEL}")

    return {
        "status":             "ok" if not issues else "not_ready",
        "vector_store_ready": vs_ready,
        "api_key_configured": ollama_ready,
        "llm_type":           "ollama",
        "ollama_model":       settings.OLLAMA_MODEL,
        "available_models":   models,
        "issues":             issues,
        "message":            "✅ All systems ready!" if not issues else " | ".join(issues),
    }


@router.get("/validate-key")
async def validate_key():
    from app.services.llm import llm_service
    return llm_service.validate_key()