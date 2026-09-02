from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.student_progress import StudentProgress as DomainProgress
from app.infrastructure.db.models import StudentProgress as ProgressModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class StudentProgressRepositoryImpl(BaseRepository[ProgressModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ProgressModel, session)

    async def create(self, progress: DomainProgress) -> DomainProgress:
        orm = ProgressModel(student_id=progress.student_id, lesson_id=progress.lesson_id, completed=progress.completed, score=progress.score, attempts=progress.attempts)
        orm = await self.add(orm)
        return DomainProgress(student_id=orm.student_id, lesson_id=orm.lesson_id, completed=orm.completed, score=orm.score, attempts=orm.attempts)

    async def get(self, student_id: int, lesson_id: int) -> Optional[DomainProgress]:
        stmt = select(ProgressModel).where(ProgressModel.student_id == student_id, ProgressModel.lesson_id == lesson_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainProgress(student_id=orm.student_id, lesson_id=orm.lesson_id, completed=orm.completed, score=orm.score, attempts=orm.attempts)

    async def list_by_student(self, student_id: int) -> Sequence[DomainProgress]:
        stmt = select(ProgressModel).where(ProgressModel.student_id == student_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainProgress(student_id=o.student_id, lesson_id=o.lesson_id, completed=o.completed, score=o.score, attempts=o.attempts) for o in orms]

    async def update(self, progress: DomainProgress) -> DomainProgress:
        orm = await self.session.get(ProgressModel, (progress.student_id, progress.lesson_id))
        if orm is None:
            raise NotFoundError("StudentProgress not found")
        orm.completed = progress.completed
        orm.score = progress.score
        orm.attempts = progress.attempts
        updated = await super().update(orm)
        return DomainProgress(student_id=updated.student_id, lesson_id=updated.lesson_id, completed=updated.completed, score=updated.score, attempts=updated.attempts)

    async def delete(self, student_id: int, lesson_id: int) -> None:
        stmt = select(ProgressModel).where(ProgressModel.student_id == student_id, ProgressModel.lesson_id == lesson_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return
        await super().delete(orm.student_id)
