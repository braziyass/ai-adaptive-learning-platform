from __future__ import annotations

from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.teacher_module import (
    PlacementTestResultDTO,
    TeacherProgressItemDTO,
    TeacherStatisticsDTO,
    TeacherStudentSummaryDTO,
    ValidationTestResultDTO,
)
from app.application.services.leveling import LevelingService
from app.domain.entities.enums import Role
from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.models import Chapter as ChapterModel
from app.infrastructure.db.models import Lesson as LessonModel
from app.infrastructure.db.models import Student as StudentModel
from app.infrastructure.db.models import StudentProgress as ProgressModel
from app.infrastructure.db.models import User as UserModel
from app.infrastructure.db.repositories import StudentRepositoryImpl, UserRepositoryImpl


class TeacherModuleError(Exception):
    pass


class TeacherNotFoundError(TeacherModuleError):
    pass


class TeacherPersistenceError(TeacherModuleError):
    pass


def _assigned_level(placement_score: int) -> int:
    return LevelingService.assign_level_from_score(placement_score)


class TeacherModuleService:
    def __init__(self, session: AsyncSession, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id
        self.user_repo = UserRepositoryImpl(session)
        self.student_repo = StudentRepositoryImpl(session)

    async def _ensure_teacher(self, current_user: DomainUser) -> DomainUser:
        role_value = getattr(current_user.role, "value", current_user.role)
        if role_value != Role.TEACHER.value:
            raise TeacherNotFoundError("Teacher access required")
        user = await self.user_repo.get_by_id(current_user.id)
        if user is None:
            raise TeacherPersistenceError("Teacher user record is missing")
        return user

    async def _require_student_in_org(self, student_id: int):
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise TeacherNotFoundError("Student not found")
        user = await self.user_repo.get_by_id(student.user_id)
        if user is None or user.organization_id != self.organization_id:
            raise TeacherNotFoundError("Student not found")
        return student

    async def list_students(self, current_user: DomainUser, offset: int = 0, limit: int = 100) -> Sequence[TeacherStudentSummaryDTO]:
        await self._ensure_teacher(current_user)
        students = await self.student_repo.list_by_organization(self.organization_id, offset=offset, limit=limit)
        result: list[TeacherStudentSummaryDTO] = []
        for student in students:
            user = await self.user_repo.get_by_id(student.user_id)
            if user is None:
                raise TeacherPersistenceError("Student user record is missing")
            result.append(
                TeacherStudentSummaryDTO(
                    student_id=student.id,
                    user_id=student.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=str(user.email),
                    current_level=student.current_level,
                    placement_score=student.placement_score,
                )
            )
        return result

    async def get_student_progress(self, current_user: DomainUser, student_id: int) -> Sequence[TeacherProgressItemDTO]:
        await self._ensure_teacher(current_user)
        student = await self._require_student_in_org(student_id)

        stmt = (
            select(ProgressModel, LessonModel, ChapterModel)
            .join(LessonModel, LessonModel.id == ProgressModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .where(ProgressModel.student_id == student.id)
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            TeacherProgressItemDTO(
                student_id=progress.student_id,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                chapter_order=chapter.order,
                completed=progress.completed,
                score=progress.score,
                attempts=progress.attempts,
            )
            for progress, lesson, chapter in rows
        ]

    async def get_placement_test_result(self, current_user: DomainUser, student_id: int) -> PlacementTestResultDTO:
        await self._ensure_teacher(current_user)
        student = await self._require_student_in_org(student_id)
        user = await self.user_repo.get_by_id(student.user_id)
        if user is None:
            raise TeacherPersistenceError("Student user record is missing")
        return PlacementTestResultDTO(
            student_id=student.id,
            user_id=student.user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=str(user.email),
            placement_score=student.placement_score,
            current_level=student.current_level,
            assigned_level=_assigned_level(student.placement_score),
        )

    async def get_validation_test_results(self, current_user: DomainUser, student_id: int) -> Sequence[ValidationTestResultDTO]:
        await self._ensure_teacher(current_user)
        student = await self._require_student_in_org(student_id)

        stmt = (
            select(ProgressModel, LessonModel, ChapterModel)
            .join(LessonModel, LessonModel.id == ProgressModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .where(
                ProgressModel.student_id == student.id,
                ProgressModel.completed.is_(True),
                ProgressModel.score.is_not(None),
            )
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            ValidationTestResultDTO(
                student_id=progress.student_id,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                level=chapter.order,
                score=progress.score,
                passed=bool(progress.score is not None and progress.score >= 80),
                attempts=progress.attempts,
            )
            for progress, lesson, chapter in rows
        ]

    async def get_statistics(self, current_user: DomainUser) -> TeacherStatisticsDTO:
        await self._ensure_teacher(current_user)

        org_students = (
            select(StudentModel.id)
            .join(UserModel, UserModel.id == StudentModel.user_id)
            .where(UserModel.organization_id == self.organization_id)
        )
        student_count_stmt = select(func.count()).select_from(org_students.subquery())
        placement_avg_stmt = select(func.coalesce(func.avg(StudentModel.placement_score), 0.0)).where(
            StudentModel.id.in_(org_students)
        )
        current_level_avg_stmt = select(func.coalesce(func.avg(StudentModel.current_level), 0.0)).where(
            StudentModel.id.in_(org_students)
        )
        completed_lessons_stmt = select(func.count(ProgressModel.lesson_id)).where(
            ProgressModel.completed.is_(True), ProgressModel.student_id.in_(org_students)
        )
        total_progress_stmt = select(func.count(ProgressModel.lesson_id)).where(
            ProgressModel.student_id.in_(org_students)
        )
        passed_validations_stmt = select(func.count(ProgressModel.lesson_id)).where(
            ProgressModel.completed.is_(True),
            ProgressModel.score.is_not(None),
            ProgressModel.score >= 80,
            ProgressModel.student_id.in_(org_students),
        )

        student_count = (await self.session.execute(student_count_stmt)).scalar_one()
        placement_avg = float((await self.session.execute(placement_avg_stmt)).scalar_one() or 0.0)
        current_level_avg = float((await self.session.execute(current_level_avg_stmt)).scalar_one() or 0.0)
        total_completed_lessons = (await self.session.execute(completed_lessons_stmt)).scalar_one()
        total_progress = (await self.session.execute(total_progress_stmt)).scalar_one()
        passed_validations = (await self.session.execute(passed_validations_stmt)).scalar_one()

        completion_rate = float(total_completed_lessons / total_progress) if total_progress else 0.0
        validation_pass_rate = float(passed_validations / total_completed_lessons) if total_completed_lessons else 0.0

        return TeacherStatisticsDTO(
            total_students=student_count,
            average_placement_score=placement_avg,
            average_current_level=current_level_avg,
            total_completed_lessons=total_completed_lessons,
            completion_rate=completion_rate,
            validation_pass_rate=validation_pass_rate,
        )
