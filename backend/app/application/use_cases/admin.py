from __future__ import annotations

from typing import Sequence

from app.application.dtos.admin_students import StudentAdminCreateDTO, StudentAdminReadDTO, StudentAdminUpdateDTO
from app.application.dtos.admin_teachers import TeacherAdminCreateDTO, TeacherAdminReadDTO, TeacherAdminUpdateDTO
from app.application.services.admin import StudentAdminService, TeacherAdminService


class StudentAdminUseCase:
    def __init__(self, service: StudentAdminService) -> None:
        self.service = service

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[StudentAdminReadDTO]:
        return await self.service.list_students(offset=offset, limit=limit)

    async def get(self, student_id: int) -> StudentAdminReadDTO:
        return await self.service.get_student(student_id)

    async def create(self, payload: StudentAdminCreateDTO) -> StudentAdminReadDTO:
        return await self.service.create_student(payload)

    async def update(self, student_id: int, payload: StudentAdminUpdateDTO) -> StudentAdminReadDTO:
        return await self.service.update_student(student_id, payload)

    async def delete(self, student_id: int) -> None:
        await self.service.delete_student(student_id)


class TeacherAdminUseCase:
    def __init__(self, service: TeacherAdminService) -> None:
        self.service = service

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[TeacherAdminReadDTO]:
        return await self.service.list_teachers(offset=offset, limit=limit)

    async def get(self, teacher_id: int) -> TeacherAdminReadDTO:
        return await self.service.get_teacher(teacher_id)

    async def create(self, payload: TeacherAdminCreateDTO) -> TeacherAdminReadDTO:
        return await self.service.create_teacher(payload)

    async def update(self, teacher_id: int, payload: TeacherAdminUpdateDTO) -> TeacherAdminReadDTO:
        return await self.service.update_teacher(teacher_id, payload)

    async def delete(self, teacher_id: int) -> None:
        await self.service.delete_teacher(teacher_id)
