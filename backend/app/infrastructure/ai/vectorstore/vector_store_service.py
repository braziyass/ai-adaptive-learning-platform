from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import faiss
import numpy as np

from app.application.dtos.ai import RAGChunkDTO
from app.domain.entities.ai_chunk import AIChunk


class VectorStoreService:
    def __init__(self, index_path: str, chunk_store_path: str) -> None:
        self.index_path = Path(index_path)
        self.chunk_store_path = Path(chunk_store_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.chunk_store_path.parent.mkdir(parents=True, exist_ok=True)
        self._index: faiss.IndexIDMap2 | None = None
        self._chunks: dict[int, dict[str, Any]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.index_path.exists():
            self._index = faiss.read_index(str(self.index_path))
        if self.chunk_store_path.exists():
            payload = json.loads(self.chunk_store_path.read_text(encoding="utf-8"))
            chunks = payload.get("chunks", []) if isinstance(payload, dict) else payload
            self._chunks = {int(item["id"]): item for item in chunks}
        self._loaded = True

    def _ensure_index(self, embedding_dimension: int) -> None:
        if self._index is not None:
            return
        base_index = faiss.IndexFlatIP(embedding_dimension)
        self._index = faiss.IndexIDMap2(base_index)

    def _persist(self) -> None:
        if self._index is not None:
            faiss.write_index(self._index, str(self.index_path))
        payload = {"chunks": sorted(self._chunks.values(), key=lambda item: int(item["id"]))}
        self.chunk_store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    async def upsert_chunks(self, chunks: Sequence[AIChunk], embeddings: Sequence[Sequence[float]]) -> list[int]:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunk and embedding counts must match")
        if not chunks:
            return []

        self._ensure_loaded()

        vectors = np.asarray(list(embeddings), dtype=np.float32)
        faiss.normalize_L2(vectors)
        self._ensure_index(vectors.shape[1])

        next_id = max(self._chunks.keys(), default=0) + 1
        ids = np.asarray([next_id + offset for offset in range(len(chunks))], dtype=np.int64)

        assert self._index is not None
        self._index.add_with_ids(vectors, ids)

        for chunk, embedding, chunk_id in zip(chunks, vectors.tolist(), ids.tolist(), strict=True):
            chunk.id = int(chunk_id)
            self._chunks[int(chunk_id)] = {
                "id": int(chunk_id),
                "source_document": chunk.source_document,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }

        self._persist()
        return [int(chunk_id) for chunk_id in ids.tolist()]

    async def search(self, query_embedding: Sequence[float], top_k: int) -> list[RAGChunkDTO]:
        self._ensure_loaded()
        if self._index is None or not self._chunks:
            return []

        vector = np.asarray([list(query_embedding)], dtype=np.float32)
        faiss.normalize_L2(vector)
        distances, indices = self._index.search(vector, top_k)

        results: list[RAGChunkDTO] = []
        for score, chunk_id in zip(distances[0].tolist(), indices[0].tolist(), strict=True):
            if chunk_id == -1:
                continue
            chunk = self._chunks.get(int(chunk_id))
            if chunk is None:
                continue
            results.append(
                RAGChunkDTO(
                    chunk_id=int(chunk["id"]),
                    source_document=str(chunk["source_document"]),
                    chunk_index=int(chunk["chunk_index"]),
                    page_number=chunk.get("page_number"),
                    text=str(chunk["text"]),
                    score=float(score),
                    metadata=dict(chunk.get("metadata") or {}),
                )
            )
        return results