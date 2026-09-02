from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.generated_artifact import GeneratedArtifact


class GeneratedArtifactRepository(ABC):
    @abstractmethod
    async def create(self, artifact: GeneratedArtifact) -> GeneratedArtifact:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, artifact_id: int) -> GeneratedArtifact | None:
        raise NotImplementedError
