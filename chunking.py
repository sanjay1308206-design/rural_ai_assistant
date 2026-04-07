"""
app/utils/chunking.py
======================
Splits long documents into overlapping text chunks for embedding.
"""
from __future__ import annotations
import re


def character_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size character chunks with overlap."""
    chunks, start = [], 0
    step = chunk_size - overlap
    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def clean_text(text: str) -> str:
    """Remove non-printable chars and collapse extra blank lines."""
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u0900-\u097F\u0B80-\u0BFF]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()