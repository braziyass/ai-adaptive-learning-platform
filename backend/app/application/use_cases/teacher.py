from __future__ import annotations

from typing import Sequence

from app.application.dtos.teacher_module import (
    PlacementTestResultDTO,
    TeacherProgressItemDTO,
    TeacherStatisticsDTO,
    TeacherStudentSummaryDTO,
    ValidationTestResultDTO,
)
from app.application.services.teacher import TeacherModuleService
from app.domain.entities.user import User as DomainUser


class TeacherModuleUseCase:
    def __init__(self, service: TeacherModuleService) -> None:
        self.service = service

    async def list_students(self, current_user: DomainUser, offset: int = 0, limit: int = 100) -> Sequence[TeacherStudentSummaryDTO]:
        return await self.service.list_students(current_user, offset=offset, limit=limit)

    async def get_student_progress(self, current_user: DomainUser, student_id: int) -> Sequence[TeacherProgressItemDTO]:
        return await self.service.get_student_progress(current_user, student_id)

    async def get_placement_test_result(self, current_user: DomainUser, student_id: int) -> PlacementTestResultDTO:
        return await self.service.get_placement_test_result(current_user, student_id)

    async def get_validation_test_results(self, current_user: DomainUser, student_id: int) -> Sequence[ValidationTestResultDTO]:
        return await self.service.get_validation_test_results(current_user, student_id)

    async def get_statistics(self, current_user: DomainUser) -> TeacherStatisticsDTO:
        return await self.service.get_statistics(current_user)
