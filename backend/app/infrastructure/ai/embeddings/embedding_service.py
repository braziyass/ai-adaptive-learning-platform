from __future__ import annotations

import hashlib
from typing import Protocol

import numpy as np


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashEmbeddingProvider:
    def __init__(self, dimension: int = 1536) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = np.zeros(self.dimension, dtype=np.float32)
            tokens = text.lower().split()
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "little") % self.dimension
                vector[index] += 1.0
            norm = float(np.linalg.norm(vector)) or 1.0
            vectors.append((vector / norm).tolist())
        return vectors


class OpenAIEmbeddingProvider:
    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai is required for OpenAI embeddings") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self.provider = provider or HashEmbeddingProvider()

    def embed(self, text: str) -> list[float]:
        return self.provider.embed_texts([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return self.provider.embed_texts(texts)