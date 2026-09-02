from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.lesson import Lesson as DomainLesson
from app.infrastructure.db.models import Lesson as LessonModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class LessonRepositoryImpl(BaseRepository[LessonModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LessonModel, session)

    async def create(self, lesson: DomainLesson) -> DomainLesson:
        orm = LessonModel(chapter_id=lesson.chapter_id, title=lesson.title, content=lesson.content)
        orm = await self.add(orm)
        return DomainLesson(id=orm.id, chapter_id=orm.chapter_id, title=orm.title, content=orm.content)

    async def get_by_id(self, id: int) -> Optional[DomainLesson]:
        stmt = select(LessonModel).where(LessonModel.id == id).options(selectinload(LessonModel.quiz))
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainLesson(id=orm.id, chapter_id=orm.chapter_id, title=orm.title, content=orm.content)

    async def list_by_chapter(self, chapter_id: int) -> Sequence[DomainLesson]:
        stmt = select(LessonModel).where(LessonModel.chapter_id == chapter_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainLesson(id=o.id, chapter_id=o.chapter_id, title=o.title, content=o.content) for o in orms]

    async def update(self, lesson: DomainLesson) -> DomainLesson:
        orm = await self.session.get(LessonModel, lesson.id)
        if orm is None:
            raise NotFoundError("Lesson not found")
        orm.title = lesson.title
        orm.content = lesson.content
        updated = await super().update(orm)
        return DomainLesson(id=updated.id, chapter_id=updated.chapter_id, title=updated.title, content=updated.content)

    async def delete(self, id: int) -> None:
        await super().delete(id)
