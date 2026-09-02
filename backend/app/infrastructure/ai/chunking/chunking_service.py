from __future__ import annotations

import hashlib
from typing import Iterable

from app.infrastructure.ai.types import SourceChunk


class ChunkingService:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, source_id: str, pages: Iterable[dict[str, object]]) -> list[SourceChunk]:
        chunks: list[SourceChunk] = []
        for page in pages:
            page_number = int(page.get("page_number", 0)) if page.get("page_number") else None
            text = str(page.get("text", ""))
            chunks.extend(self.chunk_text(source_id=source_id, text=text, page_number=page_number))
        return chunks

    def chunk_text(self, source_id: str, text: str, page_number: int | None = None) -> list[SourceChunk]:
        words = text.split()
        if not words:
            return []

        chunks: list[SourceChunk] = []
        step = self.chunk_size - self.chunk_overlap
        for start in range(0, len(words), step):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words).strip()
            if not chunk_text:
                continue
            digest = hashlib.sha256(f"{source_id}:{page_number}:{start}:{chunk_text}".encode("utf-8")).hexdigest()[:16]
            chunks.append(
                SourceChunk(
                    chunk_id=f"{source_id}:{digest}",
                    text=chunk_text,
                    source_id=source_id,
                    page_number=page_number,
                    metadata={"start_word": start, "end_word": end},
                )
            )
            if end >= len(words):
                break
        return chunks