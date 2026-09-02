from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from app.infrastructure.ai.embeddings.embedding_service import EmbeddingService
from app.infrastructure.ai.types import RetrievedChunk, SourceChunk


class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService, index_path: Path, metadata_path: Path) -> None:
        self.embedding_service = embedding_service
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self._faiss = None
        self._index = None
        self._vectors: np.ndarray | None = None
        self._chunks: list[dict[str, object]] = []
        self._load()

    def _load(self) -> None:
        if self.metadata_path.exists():
            self._chunks = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        fallback_path = self.index_path.with_suffix(".npy")
        if self.index_path.exists():
            try:
                import faiss
            except ImportError:
                if fallback_path.exists():
                    self._vectors = np.load(fallback_path)
                return

            self._faiss = faiss
            self._index = faiss.read_index(str(self.index_path))
        elif fallback_path.exists():
            self._vectors = np.load(fallback_path)

    def _persist(self) -> None:
        self.metadata_path.write_text(json.dumps(self._chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        if self._index is not None and self._faiss is not None:
            self._faiss.write_index(self._index, str(self.index_path))
        elif self._vectors is not None:
            np.save(self.index_path, self._vectors)

    def add_chunks(self, chunks: list[SourceChunk]) -> None:
        if not chunks:
            return

        vectors = np.asarray(self.embedding_service.embed_many([chunk.text for chunk in chunks]), dtype=np.float32)
        if vectors.ndim != 2:
            raise ValueError("Embedding provider returned invalid vectors")

        normalized = vectors / np.clip(np.linalg.norm(vectors, axis=1, keepdims=True), a_min=1e-12, a_max=None)
        try:
            import faiss
        except ImportError:
            self._vectors = normalized if self._vectors is None else np.vstack([self._vectors, normalized])
        else:
            if self._faiss is None:
                self._faiss = faiss
                self._index = faiss.IndexFlatIP(normalized.shape[1])
            self._index.add(normalized)

        for chunk in chunks:
            self._chunks.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "source_id": chunk.source_id,
                    "page_number": chunk.page_number,
                    "metadata": chunk.metadata,
                }
            )
        self._persist()

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if not self._chunks:
            return []

        query_vector = np.asarray(self.embedding_service.embed(query), dtype=np.float32).reshape(1, -1)
        query_vector = query_vector / np.clip(np.linalg.norm(query_vector, axis=1, keepdims=True), a_min=1e-12, a_max=None)

        if self._index is not None and self._faiss is not None:
            scores, indices = self._index.search(query_vector, min(top_k, len(self._chunks)))
            result: list[RetrievedChunk] = []
            for score, index in zip(scores[0], indices[0], strict=True):
                if index < 0:
                    continue
                item = self._chunks[index]
                result.append(
                    RetrievedChunk(
                        chunk_id=str(item["chunk_id"]),
                        text=str(item["text"]),
                        source_id=str(item["source_id"]),
                        score=float(score),
                        page_number=item.get("page_number"),
                        metadata=dict(item.get("metadata") or {}),
                    )
                )
            return result

        if self._vectors is None:
            raise RuntimeError("Vector store is not initialized")

        scores = self._vectors @ query_vector[0]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievedChunk(
                chunk_id=str(self._chunks[index]["chunk_id"]),
                text=str(self._chunks[index]["text"]),
                source_id=str(self._chunks[index]["source_id"]),
                score=float(scores[index]),
                page_number=self._chunks[index].get("page_number"),
                metadata=dict(self._chunks[index].get("metadata") or {}),
            )
            for index in top_indices
        ]
