# app/services/text_to_speech.py
# ─────────────────────────────────────────────────────────────────────────────
# Converts text to an MP3 audio file using gTTS (Google Text-to-Speech).
#
# gTTS is free, works offline once the audio is fetched, and supports
# major Indian languages including Hindi, Tamil, Telugu, Kannada, Bengali.
#
# Returns audio bytes that can be streamed back to the client or saved.
# ─────────────────────────────────────────────────────────────────────────────

import io
import logging

from app.config import settings

log = logging.getLogger(__name__)

# Map our BCP-47 codes to gTTS language tags
GTTS_LANG_MAP: dict[str, str] = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "mr": "mr",
    "bn": "bn",
}


def text_to_speech(text: str, language: str = "en") -> bytes:
    """
    Convert `text` to MP3 audio bytes.

    Args:
        text:     The text to speak.
        language: BCP-47 language code, e.g. 'en', 'hi', 'ta'.

    Returns:
        Raw MP3 bytes. Returns empty bytes on failure.
    """
    try:
        from gtts import gTTS
    except ImportError:
        log.error("gTTS not installed. Run: pip install gTTS")
        return b""

    lang = GTTS_LANG_MAP.get(language, "en")

    try:
        tts = gTTS(text=text, lang=lang, slow=False)

        # Write to an in-memory buffer instead of a file
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)

        audio_bytes = buffer.read()
        log.info(f"TTS generated {len(audio_bytes):,} bytes ({lang})")
        return audio_bytes

    except Exception as e:
        log.error(f"TTS error: {e}")
        return b""


def save_audio(text: str, output_path: str, language: str = "en") -> bool:
    """
    Convenience: generate TTS and save directly to a file.

    Returns True on success, False on failure.
    """
    audio = text_to_speech(text, language=language)
    if not audio:
        return False

    with open(output_path, "wb") as f:
        f.write(audio)
    log.info(f"Audio saved to {output_path}")
    return True