from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.course import Course


class CourseRepository(ABC):
    @abstractmethod
    async def create(self, course: Course) -> Course:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Course]:
        raise NotImplementedError

    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Course]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, course: Course) -> Course:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
