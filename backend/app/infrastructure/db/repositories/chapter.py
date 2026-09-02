from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.chapter import Chapter as DomainChapter
from app.infrastructure.db.models import Chapter as ChapterModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class ChapterRepositoryImpl(BaseRepository[ChapterModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ChapterModel, session)

    async def create(self, chapter: DomainChapter) -> DomainChapter:
        orm = ChapterModel(course_id=chapter.course_id, title=chapter.title, order=chapter.order)
        orm = await self.add(orm)
        return DomainChapter(id=orm.id, course_id=orm.course_id, title=orm.title, order=orm.order)

    async def get_by_id(self, id: int) -> Optional[DomainChapter]:
        stmt = select(ChapterModel).where(ChapterModel.id == id).options(selectinload(ChapterModel.lessons))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainChapter(id=orm.id, course_id=orm.course_id, title=orm.title, order=orm.order)

    async def list_by_course(self, course_id: int) -> Sequence[DomainChapter]:
        stmt = select(ChapterModel).where(ChapterModel.course_id == course_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainChapter(id=o.id, course_id=o.course_id, title=o.title, order=o.order) for o in orms]

    async def update(self, chapter: DomainChapter) -> DomainChapter:
        orm = await self.session.get(ChapterModel, chapter.id)
        if orm is None:
            raise NotFoundError("Chapter not found")
        orm.title = chapter.title
        orm.order = chapter.order
        updated = await super().update(orm)
        return DomainChapter(id=updated.id, course_id=updated.course_id, title=updated.title, order=updated.order)

    async def delete(self, id: int) -> None:
        await super().delete(id)
