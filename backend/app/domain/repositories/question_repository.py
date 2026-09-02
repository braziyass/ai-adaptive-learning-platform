from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities.question import Question


class QuestionRepository(ABC):
    @abstractmethod
    async def create(self, question: Question) -> Question:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Question]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_quiz(self, quiz_id: int) -> Sequence[Question]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, question: Question) -> Question:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError
