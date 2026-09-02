from __future__ import annotations

from app.infrastructure.ai.types import RetrievedChunk
from app.infrastructure.ai.vectorstore.vectorstore_service import VectorStoreService


class RetrieverService:
    def __init__(self, vector_store: VectorStoreService) -> None:
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        chunks = self.vector_store.search(query, top_k=top_k)
        if not chunks:
            raise RuntimeError("No relevant chunks found for generation")
        return chunks