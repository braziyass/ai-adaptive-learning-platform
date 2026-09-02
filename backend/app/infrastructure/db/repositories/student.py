from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.student import Student as DomainStudent
from app.infrastructure.db.models import Student as StudentModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class StudentRepositoryImpl(BaseRepository[StudentModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(StudentModel, session)

    async def create(self, student: DomainStudent, *, commit: bool = True) -> DomainStudent:
        orm = StudentModel(user_id=student.user_id, current_level=student.current_level, placement_score=student.placement_score)
        orm = await super().create(orm, commit=commit)
        return DomainStudent(id=orm.id, user_id=orm.user_id, current_level=orm.current_level, placement_score=orm.placement_score)

    async def get_by_id(self, id: int) -> Optional[DomainStudent]:
        stmt = select(StudentModel).where(StudentModel.id == id).options(selectinload(StudentModel.user), selectinload(StudentModel.progress))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainStudent(id=orm.id, user_id=orm.user_id, current_level=orm.current_level, placement_score=orm.placement_score)

    async def get_by_user_id(self, user_id: int) -> Optional[DomainStudent]:
        stmt = select(StudentModel).where(StudentModel.user_id == user_id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainStudent(id=orm.id, user_id=orm.user_id, current_level=orm.current_level, placement_score=orm.placement_score)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[DomainStudent]:
        stmt = select(StudentModel).offset(offset).limit(limit).options(
            selectinload(StudentModel.user),
            selectinload(StudentModel.progress),
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [
            DomainStudent(
                id=o.id,
                user_id=o.user_id,
                current_level=o.current_level,
                placement_score=o.placement_score,
            )
            for o in orms
        ]

    async def list_by_level(self, level: int) -> Sequence[DomainStudent]:
        stmt = select(StudentModel).where(StudentModel.current_level == level)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainStudent(id=o.id, user_id=o.user_id, current_level=o.current_level, placement_score=o.placement_score) for o in orms]

    async def update(self, student: DomainStudent, *, commit: bool = True) -> DomainStudent:
        orm = await self.session.get(StudentModel, student.id)
        if orm is None:
            raise NotFoundError("Student not found")
        orm.current_level = student.current_level
        orm.placement_score = student.placement_score
        updated = await super().update(orm, commit=commit)
        return DomainStudent(id=updated.id, user_id=updated.user_id, current_level=updated.current_level, placement_score=updated.placement_score)

    async def delete(self, id: int, *, commit: bool = True) -> None:
        await super().delete(id, commit=commit)
