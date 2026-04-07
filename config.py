"""
app/config.py
=============
Central configuration. Reads from .env file.
NO API KEY NEEDED — Ollama runs locally.

.env file:
    OLLAMA_MODEL=llama3
    OLLAMA_BASE_URL=http://localhost:11434
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Settings:

    # ── Ollama Local LLM (FREE, no API key) ──────────────────────────────────
    OLLAMA_BASE_URL: str   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str      = os.getenv("OLLAMA_MODEL", "llama3")

    # Generation
    LLM_MAX_TOKENS: int    = int(os.getenv("LLM_MAX_TOKENS", "512"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str   = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM: int     = int(os.getenv("EMBEDDING_DIM", "384"))

    # ── FAISS ─────────────────────────────────────────────────────────────────
    BASE_DIR = Path(__file__).resolve().parent.parent

    VECTORSTORE_PATH = BASE_DIR / "vectorstore"
    FAISS_INDEX_FILE = "index.faiss"
    METADATA_FILE = "meta.pkl"

    # ── RAG ───────────────────────────────────────────────────────────────────
    TOP_K_RESULTS: int     = int(os.getenv("TOP_K_RESULTS", "4"))
    CHUNK_SIZE: int        = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int     = int(os.getenv("CHUNK_OVERLAP", "50"))

    # ── OpenWeather (optional) ────────────────────────────────────────────────
    OPENWEATHER_API_KEY: str  = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # ── Whisper STT ───────────────────────────────────────────────────────────
    WHISPER_MODEL: str     = os.getenv("WHISPER_MODEL", "base")

    # ── Server ────────────────────────────────────────────────────────────────
    API_HOST: str          = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int          = int(os.getenv("API_PORT", "8000"))

    # ── Paths ─────────────────────────────────────────────────────────────────
    RAW_DATA_DIR: str      = os.getenv("RAW_DATA_DIR", "data/raw")
    PROCESSED_DATA_DIR: str = os.getenv("PROCESSED_DATA_DIR", "data/processed")


settings = Settings()