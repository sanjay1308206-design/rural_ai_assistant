"""
app/services/llm.py
====================
LLM service using Ollama (100% FREE, fully local).
No API key needed. Runs llama3 on your own machine.

SETUP:
1. Download: https://ollama.com/download
2. Run:  ollama run llama3
3. Done!
"""
from __future__ import annotations
import requests
from app.config import settings


SYSTEM_PROMPT = """You are a helpful rural agriculture assistant for Indian farmers.
Answer questions about farming, crops, soil, weather, government schemes, and rural livelihoods.
Use the context provided below to answer. If not in context, use general knowledge but mention it.
Keep answers clear, practical, and easy to understand.
Use bullet points when listing multiple steps or options."""


class LLMService:

    def __init__(self):
        self._base_url = settings.OLLAMA_BASE_URL

    # ── Private helpers ───────────────────────────────────────────────────────

    def _is_ollama_running(self) -> bool:
        try:
            r = requests.get(f"{self._base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def _is_model_available(self, model: str) -> bool:
        try:
            r = requests.get(f"{self._base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                return any(m.startswith(model.split(":")[0]) for m in models)
        except Exception:
            pass
        return False

    @staticmethod
    def _build_context(chunks: list[dict]) -> str:
        if not chunks:
            return "No specific context found. Use your general knowledge."
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(
                f"[{i}] Source: {c.get('source','?')}\n{c.get('text','').strip()}"
            )
        return "\n\n".join(parts)

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(
        self,
        query: str,
        context_chunks: list[dict],
        language_hint: str = "English",
    ) -> str:
        """Generate answer using local Ollama llama3."""

        if not self._is_ollama_running():
            return (
                "❌ Ollama is not running!\n\n"
                "Fix:\n"
                "1. Download: https://ollama.com/download\n"
                "2. Install it\n"
                "3. Open terminal and run:  ollama run llama3\n"
                "4. Wait for download (~4.7GB first time)\n"
                "5. Restart backend and try again."
            )

        model = settings.OLLAMA_MODEL

        if not self._is_model_available(model):
            return (
                f"❌ Model '{model}' not found in Ollama.\n\n"
                f"Fix: Open terminal and run:\n"
                f"    ollama pull {model}\n\n"
                f"Check installed models with:  ollama list"
            )

        try:
            context = self._build_context(context_chunks)
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Context:\n{'─'*40}\n{context}\n{'─'*40}\n\n"
                f"Farmer's Question: {query}"
            )
            if language_hint.lower() != "english":
                prompt += f"\n\nPlease respond in {language_hint}."

            print(f"[LLM] Calling Ollama ({model}) ...")
            r = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    "model":  model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": settings.LLM_TEMPERATURE,
                        "num_predict": settings.LLM_MAX_TOKENS,
                    },
                },
                timeout=120,
            )
            r.raise_for_status()
            answer = r.json().get("response", "").strip()
            if not answer:
                return "⚠️ Ollama returned empty response. Try again."
            print(f"[LLM] Done ✓ ({len(answer)} chars)")
            return answer

        except requests.exceptions.Timeout:
            return (
                "⏱️ Ollama timed out (model loading into RAM).\n"
                "Wait 30 seconds and try again."
            )
        except requests.exceptions.ConnectionError:
            return (
                "❌ Lost connection to Ollama.\n"
                "Run:  ollama serve\n"
                "Or:   ollama run llama3"
            )
        except Exception as e:
            print(f"[LLM] Error: {type(e).__name__}: {e}")
            return f"❌ Error: {type(e).__name__}: {e}"

    def health_check(self) -> bool:
        return (
            self._is_ollama_running()
            and self._is_model_available(settings.OLLAMA_MODEL)
        )

    def validate_key(self) -> dict:
        """Test Ollama — no API key needed for Ollama."""
        if not self._is_ollama_running():
            return {
                "valid": False,
                "message": (
                    "❌ Ollama is not running.\n"
                    "Run:  ollama run llama3\n"
                    "Get:  https://ollama.com/download"
                ),
            }
        model = settings.OLLAMA_MODEL
        if not self._is_model_available(model):
            return {
                "valid": False,
                "message": f"❌ Model '{model}' not found.\nRun:  ollama pull {model}",
            }
        try:
            r = requests.post(
                f"{self._base_url}/api/generate",
                json={"model": model, "prompt": "Say hello.", "stream": False},
                timeout=30,
            )
            r.raise_for_status()
            return {
                "valid": True,
                "message": f"✅ Ollama running! Model: {model} is ready.",
            }
        except Exception as e:
            return {"valid": False, "message": f"❌ Test failed: {e}"}

    def list_models(self) -> list[str]:
        try:
            r = requests.get(f"{self._base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass
        return []


# ── SINGLETON ─────────────────────────────────────────────────────────────────
llm_service = LLMService()