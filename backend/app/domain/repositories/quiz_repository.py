from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.quiz import Quiz


class QuizRepository(ABC):
    @abstractmethod
    async def create(self, quiz: Quiz) -> Quiz:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Quiz]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_lesson_id(self, lesson_id: int) -> Optional[Quiz]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, quiz: Quiz) -> Quiz:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
