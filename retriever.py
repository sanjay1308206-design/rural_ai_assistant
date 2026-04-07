"""
app/services/retriever.py
=========================
Loads the FAISS index from disk and retrieves the top-k most similar
text chunks for a given query string.

Usage:
    from app.services.retriever import retriever_service
    chunks = retriever_service.retrieve("How to grow wheat?")
"""
from __future__ import annotations
import json
import os
import faiss
import numpy as np
from app.config import settings
from app.services.embedding import embedding_service


class RetrieverService:

    def __init__(self):
        self._index    = None   # faiss.Index — loaded on first use
        self._metadata = None   # list[dict]  — loaded on first use

    def _load(self):
        """Load FAISS index + metadata from disk (runs only once)."""
        if self._index is not None:
            return  # already loaded

        index_path = os.path.join(settings.VECTORSTORE_PATH, settings.FAISS_INDEX_FILE)
        meta_path  = os.path.join(settings.VECTORSTORE_PATH, settings.METADATA_FILE)

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found: '{index_path}'\n"
                "Run:  python scripts/ingest_data.py"
            )
        if not os.path.exists(meta_path):
            raise FileNotFoundError(
                f"Metadata file not found: '{meta_path}'\n"
                "Run:  python scripts/ingest_data.py"
            )

        print("[Retriever] Loading FAISS index ...")
        self._index = faiss.read_index(index_path)

        print("[Retriever] Loading metadata ...")
        with open(meta_path, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)

        print(f"[Retriever] Ready — {self._index.ntotal} vectors ✓")

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        """
        Find top-k most relevant chunks for the query.
        Returns list of dicts: {source, chunk_index, text, score}
        """
        self._load()

        if top_k is None:
            top_k = settings.TOP_K_RESULTS

        # Embed query → shape (1, 384) for FAISS batch format
        qvec = embedding_service.embed(query).reshape(1, -1)

        # Search FAISS — lower L2 distance = more similar
        distances, indices = self._index.search(qvec, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue   # FAISS returns -1 when fewer results than top_k
            chunk = self._metadata[idx].copy()
            chunk["score"] = float(dist)
            results.append(chunk)

        return results

    def is_ready(self) -> bool:
        """True if FAISS index file exists on disk."""
        path = os.path.join(settings.VECTORSTORE_PATH, settings.FAISS_INDEX_FILE)
        return os.path.exists(path)


# ── SINGLETON — this is what all other files import ───────────────────────────
retriever_service = RetrieverService()