from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.chapter import Chapter


class ChapterRepository(ABC):
    @abstractmethod
    async def create(self, chapter: Chapter) -> Chapter:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Chapter]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_course(self, course_id: int) -> Sequence[Chapter]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, chapter: Chapter) -> Chapter:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
