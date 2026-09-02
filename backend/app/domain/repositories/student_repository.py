from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.student import Student


class StudentRepository(ABC):
    @abstractmethod
    async def create(self, student: Student) -> Student:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Student]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Student]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_level(self, level: int) -> Sequence[Student]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, student: Student) -> Student:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
