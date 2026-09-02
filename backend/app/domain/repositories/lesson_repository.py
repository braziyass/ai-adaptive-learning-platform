from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.lesson import Lesson


class LessonRepository(ABC):
    @abstractmethod
    async def create(self, lesson: Lesson) -> Lesson:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Lesson]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_chapter(self, chapter_id: int) -> Sequence[Lesson]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, lesson: Lesson) -> Lesson:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
