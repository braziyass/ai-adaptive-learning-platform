from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.student_progress import StudentProgress


class StudentProgressRepository(ABC):
    @abstractmethod
    async def create(self, progress: StudentProgress) -> StudentProgress:
        raise NotImplementedError

    @abstractmethod
    async def get(self, student_id: int, lesson_id: int) -> Optional[StudentProgress]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_student(self, student_id: int) -> Sequence[StudentProgress]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, progress: StudentProgress) -> StudentProgress:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, student_id: int, lesson_id: int) -> None:
        raise NotImplementedError
