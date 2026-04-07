"""
app/services/rag_pipeline.py
============================
Orchestrates the full RAG pipeline:
  Stage 1 — RETRIEVE  : find relevant chunks from FAISS
  Stage 2 — AUGMENT   : format chunks as LLM context
  Stage 3 — GENERATE  : call OpenAI, return answer

Usage:
    from app.services.rag_pipeline import rag_pipeline
    result = rag_pipeline.run(query="How to grow wheat?")
"""
from __future__ import annotations
from app.services.retriever import retriever_service
from app.services.llm import llm_service
# NOTE: weather_service is NOT imported here.
# Weather is handled in app/routes/query.py only.


class RAGPipeline:
    """End-to-end Retrieval-Augmented Generation pipeline."""

    def run(
        self,
        query: str,
        top_k: int | None = None,
        language_hint: str = "English",
    ) -> dict:
        """
        Run the full RAG pipeline.

        Returns dict with keys:
            query       - original question
            answer      - generated answer string
            sources     - list of source filenames used
            chunks_used - number of chunks retrieved
        """
        # Stage 1: RETRIEVE — search FAISS for relevant chunks
        print(f"[RAG] Retrieving for: '{query[:60]}'")
        chunks = retriever_service.retrieve(query, top_k=top_k)

        if not chunks:
            return {
                "query": query,
                "answer": (
                    "I couldn't find relevant information in the knowledge base. "
                    "Please consult your local agriculture extension officer."
                ),
                "sources": [],
                "chunks_used": 0,
            }

        # Stage 2: AUGMENT — collect unique source filenames
        sources = list({chunk["source"] for chunk in chunks})
        print(f"[RAG] {len(chunks)} chunks from: {sources}")

        # Stage 3: GENERATE — call OpenAI with context
        print("[RAG] Generating answer ...")
        answer = llm_service.generate(
            query=query,
            context_chunks=chunks,
            language_hint=language_hint,
        )
        print("[RAG] Done ✓")

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "chunks_used": len(chunks),
        }

    def is_ready(self) -> bool:
        """True only if the FAISS vector store exists on disk."""
        return retriever_service.is_ready()


# ── SINGLETON — this is what all other files import ───────────────────────────
rag_pipeline = RAGPipeline()