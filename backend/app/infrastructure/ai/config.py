from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AISettings:
    pdf_dir: Path = Path("app/storage/pdfs")
    processed_dir: Path = Path("app/storage/processed")
    cache_dir: Path = Path("app/storage/cache/ai")
    groq_chat_model: str = "qwen/qwen3.8-27b"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    top_k: int = 5
    min_score: float = 0.2
    allow_fallback: bool = False
