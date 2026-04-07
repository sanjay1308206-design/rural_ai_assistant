from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            print(f"[EmbeddingService] Loading: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    def embed(self, text: str) -> np.ndarray:
        return self._load_model().encode(text, convert_to_numpy=True).astype(np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self._load_model().encode(texts, convert_to_numpy=True, batch_size=32).astype(np.float32)

embedding_service = EmbeddingService()