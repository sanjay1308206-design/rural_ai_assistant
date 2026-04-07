# app/services/speech_to_text.py
# ─────────────────────────────────────────────────────────────────────────────
# Converts an audio file (WAV, MP3, M4A, …) to text using OpenAI Whisper.
#
# Whisper runs fully locally – no API call, no API key needed here.
# The model is downloaded on first use and cached in ~/.cache/whisper/.
# ─────────────────────────────────────────────────────────────────────────────

import logging
import tempfile
from pathlib import Path
from app.config import settings

log = logging.getLogger(__name__)

# ── Lazy-load Whisper ─────────────────────────────────────────────────────────
# Whisper is heavy (~150 MB for "base") so we load it on first use.
_whisper_model = None


def _get_model():
    """Load and cache the Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        import whisper
        log.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        log.info("Whisper model ready.")
    return _whisper_model


def transcribe_audio(audio_bytes: bytes, file_extension: str = "wav") -> str:
    """
    Transcribe raw audio bytes to text using Whisper.

    Args:
        audio_bytes:    Raw bytes of the audio file.
        file_extension: File format hint, e.g. "wav", "mp3", "m4a".

    Returns:
        Transcribed text string (may be empty if audio is silent/unclear).
    """
    model = _get_model()

    # Whisper requires a file path, so we write bytes to a temp file
    with tempfile.NamedTemporaryFile(
        suffix=f".{file_extension}", delete=False
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # `fp16=False` avoids warnings on CPU; set True on GPU for speed
        result = model.transcribe(tmp_path, fp16=False)
        text = result.get("text", "").strip()
        log.info(f"Transcription ({len(text)} chars): {text[:80]}…")
        return text
    except Exception as e:
        log.error(f"Whisper transcription error: {e}")
        return ""
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


def transcribe_file(audio_path: str | Path) -> str:
    """
    Transcribe an audio file given its path on disk.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Transcribed text string.
    """
    path = Path(audio_path)
    audio_bytes = path.read_bytes()
    return transcribe_audio(audio_bytes, file_extension=path.suffix.lstrip("."))
