from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.teacher import Teacher


class TeacherRepository(ABC):
    @abstractmethod
    async def create(self, teacher: Teacher) -> Teacher:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Teacher]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Teacher]:
        raise NotImplementedError

    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Teacher]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, teacher: Teacher) -> Teacher:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
