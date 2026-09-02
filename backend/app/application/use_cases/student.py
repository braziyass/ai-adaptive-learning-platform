from __future__ import annotations

from typing import Sequence

from app.application.dtos.student_module import (
    CompletedQuizDTO,
    StudentCurrentLevelDTO,
    StudentProfileDTO,
    StudentProgressItemDTO,
    UnlockedLessonDTO,
    ValidationTestResultDTO,
    AvailableQuizDTO,
    QuizSubmissionResultDTO,
)
from app.application.services.student import StudentModuleService
from app.domain.entities.user import User as DomainUser


class StudentModuleUseCase:
    def __init__(self, service: StudentModuleService) -> None:
        self.service = service

    async def get_profile(self, current_user: DomainUser) -> StudentProfileDTO:
        return await self.service.get_profile(current_user)

    async def get_current_level(self, current_user: DomainUser) -> StudentCurrentLevelDTO:
        return await self.service.get_current_level(current_user)

    async def get_progress(self, current_user: DomainUser) -> Sequence[StudentProgressItemDTO]:
        return await self.service.get_progress(current_user)

    async def get_unlocked_lessons(self, current_user: DomainUser) -> Sequence[UnlockedLessonDTO]:
        return await self.service.get_unlocked_lessons(current_user)

    async def get_completed_quizzes(self, current_user: DomainUser) -> Sequence[CompletedQuizDTO]:
        return await self.service.get_completed_quizzes(current_user)

    async def get_available_quizzes(self, current_user: DomainUser) -> Sequence[AvailableQuizDTO]:
        return await self.service.get_available_quizzes(current_user)

    async def get_validation_test_results(self, current_user: DomainUser) -> Sequence[ValidationTestResultDTO]:
        return await self.service.get_validation_test_results(current_user)

    async def submit_quiz(self, current_user: DomainUser, quiz_id: int, answers: list[dict]) -> QuizSubmissionResultDTO:
        return await self.service.submit_quiz(current_user, quiz_id, answers)
