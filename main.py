"""
app/main.py
============
FastAPI application entry point.

IMPORTANT: This file registers BOTH routers:
  /api/*         → query.py  (ask, health, validate-key)
  /api/voice/*   → voice.py  (transcribe, speak, ask)

Start:  uvicorn app.main:app --reload --port 8000
Docs:   http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Import BOTH route modules ─────────────────────────────────────────────────
from app.routes import query
from app.routes import voice          # <-- THIS MUST BE HERE
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title       = "Rural AI Assistant API",
        description = "AI assistant for Indian farmers — Ollama llama3 powered.",
        version     = "3.0.0",
        docs_url    = "/docs",
        redoc_url   = "/redoc",
    )

    # Allow Streamlit (port 8501) to call this API (port 8000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins     = ["*"],
        allow_credentials = True,
        allow_methods     = ["*"],
        allow_headers     = ["*"],
    )

    # ── Register routers ──────────────────────────────────────────────────────
    # Query routes  →  /api/ask, /api/health, /api/validate-key
    app.include_router(query.router, prefix="/api", tags=["Query"])

    # Voice routes  →  /api/voice/transcribe, /api/voice/speak, /api/voice/ask
    app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "🌾 Rural AI Assistant is running!",
            "docs":    "http://localhost:8000/docs",
            "health":  "http://localhost:8000/api/health",
            "voice":   "http://localhost:8000/api/voice/transcribe",
        }

    return app


# The 'app' object is what uvicorn imports
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host   = settings.API_HOST,
        port   = settings.API_PORT,
        reload = True,
    )