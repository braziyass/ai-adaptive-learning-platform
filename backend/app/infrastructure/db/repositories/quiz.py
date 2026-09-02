from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.quiz import Quiz as DomainQuiz
from app.infrastructure.db.models import Quiz as QuizModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class QuizRepositoryImpl(BaseRepository[QuizModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(QuizModel, session)

    async def create(self, quiz: DomainQuiz) -> DomainQuiz:
        orm = QuizModel(lesson_id=quiz.lesson_id)
        orm = await self.add(orm)
        return DomainQuiz(id=orm.id, lesson_id=orm.lesson_id)

    async def get_by_id(self, id: int) -> Optional[DomainQuiz]:
        stmt = select(QuizModel).where(QuizModel.id == id).options(selectinload(QuizModel.questions))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainQuiz(id=orm.id, lesson_id=orm.lesson_id)

    async def get_by_lesson_id(self, lesson_id: int) -> Optional[DomainQuiz]:
        stmt = select(QuizModel).where(QuizModel.lesson_id == lesson_id).options(selectinload(QuizModel.questions))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainQuiz(id=orm.id, lesson_id=orm.lesson_id)

    async def update(self, quiz: DomainQuiz) -> DomainQuiz:
        orm = await self.session.get(QuizModel, quiz.id)
        if orm is None:
            raise NotFoundError("Quiz not found")
        orm.lesson_id = quiz.lesson_id
        updated = await super().update(orm)
        return DomainQuiz(id=updated.id, lesson_id=updated.lesson_id)

    async def delete(self, id: int) -> None:
        await super().delete(id)
