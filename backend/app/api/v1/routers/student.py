from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.student import StudentModuleError, StudentNotFoundError, StudentPersistenceError
from app.application.use_cases.student import StudentModuleUseCase
from app.domain.entities.user import User as DomainUser
from app.presentation.dependencies import get_current_student_user, get_student_module_use_case
from app.presentation.schemas.student_module import (
    AvailableQuizResponse,
    CompletedQuizResponse,
    StudentCurrentLevelResponse,
    StudentProfileResponse,
    StudentProgressResponseItem,
    UnlockedLessonResponse,
    ValidationTestResultResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
)
import logging
import traceback

router = APIRouter(prefix="/student", dependencies=[Depends(get_current_student_user)])


def _translate_error(error: Exception) -> HTTPException:
    if isinstance(error, StudentNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, StudentPersistenceError):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.get("/profile", response_model=StudentProfileResponse)
async def get_profile(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_profile(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/current-level", response_model=StudentCurrentLevelResponse)
async def get_current_level(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_current_level(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/progress", response_model=list[StudentProgressResponseItem])
async def get_progress(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_progress(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/unlocked-lessons", response_model=list[UnlockedLessonResponse])
async def get_unlocked_lessons(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_unlocked_lessons(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/completed-quizzes", response_model=list[CompletedQuizResponse])
async def get_completed_quizzes(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_completed_quizzes(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/available-quizzes", response_model=list[AvailableQuizResponse])
async def get_available_quizzes(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_available_quizzes(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/validation-results", response_model=list[ValidationTestResultResponse])
async def get_validation_results(
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.get_validation_test_results(current_user)
    except Exception as exc:
        raise _translate_error(exc)


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(
    quiz_id: int,
    payload: QuizSubmissionRequest,
    current_user: DomainUser = Depends(get_current_student_user),
    use_case: StudentModuleUseCase = Depends(get_student_module_use_case),
):
    try:
        return await use_case.submit_quiz(current_user, quiz_id, payload.answers)
    except Exception as exc:
        logging.exception("Error submitting quiz %s for user %s", quiz_id, getattr(current_user, 'id', None))
        tb = traceback.format_exc()
        # also include traceback in the error detail to aid local debugging
        raise _translate_error(Exception(f"{exc}\n\nTraceback:\n{tb}"))
