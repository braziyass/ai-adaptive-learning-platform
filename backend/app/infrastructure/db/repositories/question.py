from __future__ import annotations

from typing import Optional, Sequence, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.question import Question as DomainQuestion
from app.infrastructure.db.models import Question as QuestionModel
from app.infrastructure.db.models.enums import QuestionTypeEnum
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class QuestionRepositoryImpl(BaseRepository[QuestionModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(QuestionModel, session)

    async def create(self, question: DomainQuestion) -> DomainQuestion:
        qtype = question.type.value if hasattr(question.type, "value") else question.type
        orm = QuestionModel(quiz_id=question.quiz_id, question=question.question, type=QuestionTypeEnum(qtype), meta=question.metadata)
        orm = await self.add(orm)
        return DomainQuestion(id=orm.id, quiz_id=orm.quiz_id, question=orm.question, type=orm.type.value, metadata=orm.meta)

    async def get_by_id(self, id: int) -> Optional[DomainQuestion]:
        stmt = select(QuestionModel).where(QuestionModel.id == id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainQuestion(id=orm.id, quiz_id=orm.quiz_id, question=orm.question, type=orm.type.value, metadata=orm.meta)

    async def list_by_quiz(self, quiz_id: int) -> Sequence[DomainQuestion]:
        stmt = select(QuestionModel).where(QuestionModel.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainQuestion(id=o.id, quiz_id=o.quiz_id, question=o.question, type=o.type.value, metadata=o.meta) for o in orms]

    async def update(self, question: DomainQuestion) -> DomainQuestion:
        orm = await self.session.get(QuestionModel, question.id)
        if orm is None:
            raise NotFoundError("Question not found")
        orm.question = question.question
        orm.type = QuestionTypeEnum(question.type.value if hasattr(question.type, "value") else question.type)
        orm.meta = question.metadata
        updated = await super().update(orm)
        return DomainQuestion(id=updated.id, quiz_id=updated.quiz_id, question=updated.question, type=updated.type.value, metadata=updated.meta)

    async def delete(self, id: int) -> None:
        await super().delete(id)
