"""
app/utils/translator.py
========================
Translation helpers using deep-translator (free, no API key needed).

Functions exported:
    translate(text, source_lang, target_lang)
    translate_to_english(text, source_lang)     <-- used by query.py
    translate_from_english(text, target_lang)   <-- used by query.py
"""
from __future__ import annotations

from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException


# Human-readable name → Google Translate language code
LANG_MAP = {
    "english":   "en",
    "hindi":     "hi",
    "tamil":     "ta",
    "telugu":    "te",
    "kannada":   "kn",
    "malayalam": "ml",
    "bengali":   "bn",
    "marathi":   "mr",
    "gujarati":  "gu",
    "punjabi":   "pa",
    "urdu":      "ur",
    "odia":      "or",
}


def _code(lang: str) -> str:
    """Convert language name to 2-letter code. Pass-through if already a code."""
    if len(lang.strip()) == 2:
        return lang.strip().lower()
    return LANG_MAP.get(lang.strip().lower(), "en")


def translate(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """
    Translate text from source_lang to target_lang.
    Uses 'auto' for automatic source language detection.
    Returns original text on any failure (never crashes).
    """
    if not text.strip():
        return text

    src = "auto" if source_lang in ("auto", "") else _code(source_lang)
    tgt = _code(target_lang)

    # Skip if same language
    if src == tgt and src != "auto":
        return text

    try:
        result = GoogleTranslator(source=src, target=tgt).translate(text)
        return result if result else text
    except LanguageNotSupportedException:
        print(f"[Translator] Unsupported language pair: {source_lang} → {target_lang}")
        return text
    except Exception as e:
        # Translation failure must NEVER crash the main pipeline
        print(f"[Translator] Warning — translation failed: {e}")
        return text


def translate_to_english(text: str, source_lang: str = "auto") -> str:
    """Translate any text to English."""
    return translate(text, source_lang=source_lang, target_lang="en")


def translate_from_english(text: str, target_lang: str = "en") -> str:
    """Translate English text to another language."""
    if target_lang in ("en", "english"):
        return text
    return translate(text, source_lang="en", target_lang=target_lang)