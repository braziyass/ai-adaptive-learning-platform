from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.course import Course as DomainCourse
from app.infrastructure.db.models import Course as CourseModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class CourseRepositoryImpl(BaseRepository[CourseModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CourseModel, session)

    async def create(self, course: DomainCourse) -> DomainCourse:
        orm = CourseModel(title=course.title, subject=course.subject)
        orm = await self.add(orm)
        return DomainCourse(id=orm.id, title=orm.title, subject=orm.subject)

    async def get_by_id(self, id: int) -> Optional[DomainCourse]:
        stmt = select(CourseModel).where(CourseModel.id == id).options(selectinload(CourseModel.chapters))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainCourse(id=orm.id, title=orm.title, subject=orm.subject)

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[DomainCourse]:
        stmt = select(CourseModel).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainCourse(id=o.id, title=o.title, subject=o.subject) for o in orms]

    async def update(self, course: DomainCourse) -> DomainCourse:
        orm = await self.session.get(CourseModel, course.id)
        if orm is None:
            raise NotFoundError("Course not found")
        orm.title = course.title
        orm.subject = course.subject
        updated = await super().update(orm)
        return DomainCourse(id=updated.id, title=updated.title, subject=updated.subject)

    async def delete(self, id: int) -> None:
        await super().delete(id)
