from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.teacher import TeacherModuleError, TeacherNotFoundError, TeacherPersistenceError
from app.application.use_cases.teacher import TeacherModuleUseCase
from app.domain.entities.user import User as DomainUser
from app.presentation.dependencies import get_current_teacher_user, get_teacher_module_use_case
from app.presentation.schemas.teacher_module import (
    PlacementTestResultResponse,
    TeacherProgressResponseItem,
    TeacherStatisticsResponse,
    TeacherStudentSummaryResponse,
    ValidationTestResultResponse,
)

router = APIRouter(prefix="/teacher", dependencies=[Depends(get_current_teacher_user)])


def _translate_error(error: Exception) -> HTTPException:
    if isinstance(error, TeacherNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, TeacherPersistenceError):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.get("/students", response_model=list[TeacherStudentSummaryResponse])
async def list_students(
    offset: int = 0,
    limit: int = 100,
    current_user: DomainUser = Depends(get_current_teacher_user),
    use_case: TeacherModuleUseCase = Depends(get_teacher_module_use_case),
):
    try:
        return await use_case.list_students(current_user, offset=offset, limit=limit)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/students/{student_id}/progress", response_model=list[TeacherProgressResponseItem])
async def get_student_progress(
    student_id: int,
    current_user: DomainUser = Depends(get_current_teacher_user),
    use_case: TeacherModuleUseCase = Depends(get_teacher_module_use_case),
):
    try:
        return await use_case.get_student_progress(current_user, student_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/students/{student_id}/placement-result", response_model=PlacementTestResultResponse)
async def get_placement_result(
    student_id: int,
    current_user: DomainUser = Depends(get_current_teacher_user),
    use_case: TeacherModuleUseCase = Depends(get_teacher_module_use_case),
):
    try:
        return await use_case.get_placement_test_result(current_user, student_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/students/{student_id}/validation-results", response_model=list[ValidationTestResultResponse])
async def get_validation_results(
    student_id: int,
    current_user: DomainUser = Depends(get_current_teacher_user),
    use_case: TeacherModuleUseCase = Depends(get_teacher_module_use_case),
):
    try:
        return await use_case.get_validation_test_results(current_user, student_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/statistics", response_model=TeacherStatisticsResponse)
async def get_statistics(
    current_user: DomainUser = Depends(get_current_teacher_user),
    use_case: TeacherModuleUseCase = Depends(get_teacher_module_use_case),
):
    try:
        return await use_case.get_statistics(current_user)
    except Exception as exc:
        raise _translate_error(exc)
