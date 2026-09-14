from __future__ import annotations

from dataclasses import asdict
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.admin_students import (
    StudentAdminCreateDTO,
    StudentAdminReadDTO,
    StudentAdminUpdateDTO,
)
from app.application.dtos.admin_teachers import (
    TeacherAdminCreateDTO,
    TeacherAdminReadDTO,
    TeacherAdminUpdateDTO,
)
from app.application.services.audit import AuditLogger
from app.domain.entities.enums import Role
from app.domain.entities.student import Student as DomainStudent
from app.domain.entities.teacher import Teacher as DomainTeacher
from app.domain.entities.user import User as DomainUser
from app.infrastructure.auth.password import hash_password
from app.infrastructure.db.repositories import (
    StudentRepositoryImpl,
    TeacherRepositoryImpl,
    UserRepositoryImpl,
)
from app.infrastructure.db.repositories.errors import IntegrityViolationError, RepositoryError


class AdminModuleError(Exception):
    pass


class AdminNotFoundError(AdminModuleError):
    pass


class AdminConflictError(AdminModuleError):
    pass


class AdminPersistenceError(AdminModuleError):
    pass


def _role_value(role: object) -> str:
    return getattr(role, "value", role)


def _student_read(student: DomainStudent, user: DomainUser) -> StudentAdminReadDTO:
    return StudentAdminReadDTO(
        id=student.id,
        user_id=student.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        current_level=student.current_level,
        placement_score=student.placement_score,
    )


def _teacher_read(teacher: DomainTeacher, user: DomainUser) -> TeacherAdminReadDTO:
    return TeacherAdminReadDTO(
        id=teacher.id,
        user_id=teacher.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )


class StudentAdminService:
    def __init__(self, session: AsyncSession, organization_id: int, actor_user_id: int | None = None) -> None:
        self.session = session
        self.organization_id = organization_id
        self.actor_user_id = actor_user_id
        self.user_repo = UserRepositoryImpl(session)
        self.student_repo = StudentRepositoryImpl(session)
        self.audit = AuditLogger(session)

    async def _require_student_in_org(self, student_id: int) -> tuple:
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise AdminNotFoundError("Student not found")
        user = await self.user_repo.get_by_id(student.user_id)
        if user is None:
            raise AdminPersistenceError("Student user record is missing")
        if user.organization_id != self.organization_id:
            raise AdminNotFoundError("Student not found")
        return student, user

    async def list_students(self, offset: int = 0, limit: int = 100) -> Sequence[StudentAdminReadDTO]:
        students = await self.student_repo.list_by_organization(self.organization_id, offset=offset, limit=limit)
        result: list[StudentAdminReadDTO] = []
        for student in students:
            user = await self.user_repo.get_by_id(student.user_id)
            if user is None:
                raise AdminPersistenceError("Student user record is missing")
            result.append(_student_read(student, user))
        return result

    async def get_student(self, student_id: int) -> StudentAdminReadDTO:
        student, user = await self._require_student_in_org(student_id)
        return _student_read(student, user)

    async def create_student(self, payload: StudentAdminCreateDTO) -> StudentAdminReadDTO:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing is not None:
            raise AdminConflictError("Email already exists")

        try:
            user = DomainUser(
                id=None,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=str(payload.email),
                password=hash_password(payload.password),
                role=Role.STUDENT,
                organization_id=self.organization_id,
            )
            created_user = await self.user_repo.create(user, commit=False)
            student = DomainStudent(
                id=None,
                user_id=created_user.id,
                current_level=payload.current_level,
                placement_score=payload.placement_score,
            )
            created_student = await self.student_repo.create(student, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="student.create",
                resource_type="student",
                resource_id=created_student.id,
            )
            await self.session.commit()
            return _student_read(created_student, created_user)
        except IntegrityViolationError as exc:
            await self.session.rollback()
            raise AdminConflictError(str(exc)) from exc
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc

    async def update_student(self, student_id: int, payload: StudentAdminUpdateDTO) -> StudentAdminReadDTO:
        student, user = await self._require_student_in_org(student_id)

        duplicate = await self.user_repo.get_by_email(payload.email)
        if duplicate is not None and duplicate.id != user.id:
            raise AdminConflictError("Email already exists")

        try:
            updated_user = DomainUser(
                id=user.id,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=str(payload.email),
                password=hash_password(payload.password),
                role=Role.STUDENT,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            updated_student = DomainStudent(
                id=student.id,
                user_id=student.user_id,
                current_level=payload.current_level,
                placement_score=payload.placement_score,
                points=student.points,
                placement_completed_at=student.placement_completed_at,
            )
            updated_user = await self.user_repo.update(updated_user, commit=False)
            updated_student = await self.student_repo.update(updated_student, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="student.update",
                resource_type="student",
                resource_id=updated_student.id,
            )
            await self.session.commit()
            return _student_read(updated_student, updated_user)
        except IntegrityViolationError as exc:
            await self.session.rollback()
            raise AdminConflictError(str(exc)) from exc
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc

    async def delete_student(self, student_id: int) -> None:
        student, _ = await self._require_student_in_org(student_id)
        try:
            await self.user_repo.delete(student.user_id, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="student.delete",
                resource_type="student",
                resource_id=student.id,
            )
            await self.session.commit()
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc


class TeacherAdminService:
    def __init__(self, session: AsyncSession, organization_id: int, actor_user_id: int | None = None) -> None:
        self.session = session
        self.organization_id = organization_id
        self.actor_user_id = actor_user_id
        self.user_repo = UserRepositoryImpl(session)
        self.teacher_repo = TeacherRepositoryImpl(session)
        self.audit = AuditLogger(session)

    async def _require_teacher_in_org(self, teacher_id: int) -> tuple:
        teacher = await self.teacher_repo.get_by_id(teacher_id)
        if teacher is None:
            raise AdminNotFoundError("Teacher not found")
        user = await self.user_repo.get_by_id(teacher.user_id)
        if user is None:
            raise AdminPersistenceError("Teacher user record is missing")
        if user.organization_id != self.organization_id:
            raise AdminNotFoundError("Teacher not found")
        return teacher, user

    async def list_teachers(self, offset: int = 0, limit: int = 100) -> Sequence[TeacherAdminReadDTO]:
        teachers = await self.teacher_repo.list_by_organization(self.organization_id, offset=offset, limit=limit)
        result: list[TeacherAdminReadDTO] = []
        for teacher in teachers:
            user = await self.user_repo.get_by_id(teacher.user_id)
            if user is None:
                raise AdminPersistenceError("Teacher user record is missing")
            result.append(_teacher_read(teacher, user))
        return result

    async def get_teacher(self, teacher_id: int) -> TeacherAdminReadDTO:
        teacher, user = await self._require_teacher_in_org(teacher_id)
        return _teacher_read(teacher, user)

    async def create_teacher(self, payload: TeacherAdminCreateDTO) -> TeacherAdminReadDTO:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing is not None:
            raise AdminConflictError("Email already exists")

        try:
            user = DomainUser(
                id=None,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=str(payload.email),
                password=hash_password(payload.password),
                role=Role.TEACHER,
                organization_id=self.organization_id,
            )
            created_user = await self.user_repo.create(user, commit=False)
            teacher = DomainTeacher(id=None, user_id=created_user.id)
            created_teacher = await self.teacher_repo.create(teacher, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="teacher.create",
                resource_type="teacher",
                resource_id=created_teacher.id,
            )
            await self.session.commit()
            return _teacher_read(created_teacher, created_user)
        except IntegrityViolationError as exc:
            await self.session.rollback()
            raise AdminConflictError(str(exc)) from exc
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc

    async def update_teacher(self, teacher_id: int, payload: TeacherAdminUpdateDTO) -> TeacherAdminReadDTO:
        teacher, user = await self._require_teacher_in_org(teacher_id)

        duplicate = await self.user_repo.get_by_email(payload.email)
        if duplicate is not None and duplicate.id != user.id:
            raise AdminConflictError("Email already exists")

        try:
            updated_user = DomainUser(
                id=user.id,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=str(payload.email),
                password=hash_password(payload.password),
                role=Role.TEACHER,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            updated_teacher = DomainTeacher(id=teacher.id, user_id=teacher.user_id)
            updated_user = await self.user_repo.update(updated_user, commit=False)
            updated_teacher = await self.teacher_repo.update(updated_teacher, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="teacher.update",
                resource_type="teacher",
                resource_id=updated_teacher.id,
            )
            await self.session.commit()
            return _teacher_read(updated_teacher, updated_user)
        except IntegrityViolationError as exc:
            await self.session.rollback()
            raise AdminConflictError(str(exc)) from exc
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc

    async def delete_teacher(self, teacher_id: int) -> None:
        teacher, _ = await self._require_teacher_in_org(teacher_id)
        try:
            await self.user_repo.delete(teacher.user_id, commit=False)
            await self.audit.log(
                organization_id=self.organization_id,
                actor_user_id=self.actor_user_id,
                action="teacher.delete",
                resource_type="teacher",
                resource_id=teacher.id,
            )
            await self.session.commit()
        except RepositoryError as exc:
            await self.session.rollback()
            raise AdminPersistenceError(str(exc)) from exc
