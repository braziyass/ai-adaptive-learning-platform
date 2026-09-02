from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.teacher import Teacher as DomainTeacher
from app.infrastructure.db.models import Teacher as TeacherModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class TeacherRepositoryImpl(BaseRepository[TeacherModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TeacherModel, session)

    async def create(self, teacher: DomainTeacher, *, commit: bool = True) -> DomainTeacher:
        orm = TeacherModel(user_id=teacher.user_id)
        orm = await super().create(orm, commit=commit)
        return DomainTeacher(id=orm.id, user_id=orm.user_id)

    async def get_by_id(self, id: int) -> Optional[DomainTeacher]:
        stmt = select(TeacherModel).where(TeacherModel.id == id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainTeacher(id=orm.id, user_id=orm.user_id)

    async def get_by_user_id(self, user_id: int) -> Optional[DomainTeacher]:
        stmt = select(TeacherModel).where(TeacherModel.user_id == user_id).options(selectinload(TeacherModel.user))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainTeacher(id=orm.id, user_id=orm.user_id)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[DomainTeacher]:
        stmt = select(TeacherModel).offset(offset).limit(limit).options(selectinload(TeacherModel.user))
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainTeacher(id=o.id, user_id=o.user_id) for o in orms]

    async def update(self, teacher: DomainTeacher, *, commit: bool = True) -> DomainTeacher:
        orm = await self.session.get(TeacherModel, teacher.id)
        if orm is None:
            raise NotFoundError("Teacher not found")
        orm.user_id = teacher.user_id
        updated = await super().update(orm, commit=commit)
        return DomainTeacher(id=updated.id, user_id=updated.user_id)

    async def delete(self, id: int, *, commit: bool = True) -> None:
        await super().delete(id, commit=commit)
