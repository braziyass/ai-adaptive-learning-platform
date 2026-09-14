from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chapter import Chapter as DomainChapter
from app.domain.entities.course import Course as DomainCourse
from app.domain.entities.lesson import Lesson as DomainLesson
from app.infrastructure.db.repositories import get_chapter_repository, get_course_repository, get_lesson_repository


class CurriculumNotFoundError(Exception):
    pass


class CurriculumBrowseService:
    """Read-only, organization-scoped browsing of courses/chapters/lessons.

    Backs the admin generation-form pickers so admins choose curriculum
    content by name instead of typing raw database IDs.
    """

    def __init__(self, session: AsyncSession, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id
        self.course_repo = get_course_repository(session)
        self.chapter_repo = get_chapter_repository(session)
        self.lesson_repo = get_lesson_repository(session)

    async def list_courses(self) -> Sequence[DomainCourse]:
        return await self.course_repo.list(limit=500, organization_id=self.organization_id)

    async def list_chapters(self, course_id: int) -> Sequence[DomainChapter]:
        course = await self.course_repo.get_by_id(course_id, organization_id=self.organization_id)
        if course is None:
            raise CurriculumNotFoundError("Course not found")
        return await self.chapter_repo.list_by_course(course_id)

    async def list_lessons(self, chapter_id: int) -> Sequence[DomainLesson]:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if chapter is None:
            raise CurriculumNotFoundError("Chapter not found")
        course = await self.course_repo.get_by_id(chapter.course_id, organization_id=self.organization_id)
        if course is None:
            raise CurriculumNotFoundError("Chapter not found")
        return await self.lesson_repo.list_by_chapter(chapter_id)
