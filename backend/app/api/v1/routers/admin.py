from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.admin import AdminConflictError, AdminNotFoundError, AdminPersistenceError
from app.application.services.audit import AuditLogger
from app.application.services.curriculum import CurriculumBrowseService, CurriculumNotFoundError
from app.application.use_cases.admin import StudentAdminUseCase, TeacherAdminUseCase
from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.repositories.placement_test import PlacementTestRepositoryImpl
from app.presentation.dependencies import (
    get_audit_logger,
    get_curriculum_browse_service,
    get_current_admin,
    get_placement_test_repo,
    get_student_admin_use_case,
    get_teacher_admin_use_case,
)
from app.presentation.schemas.admin_students import StudentCreateRequest, StudentUpdateRequest, StudentResponse
from app.presentation.schemas.admin_teachers import TeacherCreateRequest, TeacherUpdateRequest, TeacherResponse
from app.presentation.schemas.audit import AuditLogResponse
from app.presentation.schemas.chapters import ChapterResponse
from app.presentation.schemas.courses import CourseResponse
from app.presentation.schemas.lessons import CourseLessonResponse, LessonResponse
from app.presentation.schemas.placement_test import AdminPlacementTestResponse, AdminPlacementTestUpdateRequest

router = APIRouter(prefix="/admin", dependencies=[Depends(get_current_admin)])


def _translate_error(error: Exception) -> HTTPException:
    if isinstance(error, AdminNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, AdminConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.get("/students", response_model=list[StudentResponse])
async def list_students(
    offset: int = 0,
    limit: int = 100,
    use_case: StudentAdminUseCase = Depends(get_student_admin_use_case),
):
    try:
        return await use_case.list(offset=offset, limit=limit)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, use_case: StudentAdminUseCase = Depends(get_student_admin_use_case)):
    try:
        return await use_case.get(student_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(payload: StudentCreateRequest, use_case: StudentAdminUseCase = Depends(get_student_admin_use_case)):
    try:
        return await use_case.create(payload)
    except Exception as exc:
        raise _translate_error(exc)


@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    payload: StudentUpdateRequest,
    use_case: StudentAdminUseCase = Depends(get_student_admin_use_case),
):
    try:
        return await use_case.update(student_id, payload)
    except Exception as exc:
        raise _translate_error(exc)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int, use_case: StudentAdminUseCase = Depends(get_student_admin_use_case)):
    try:
        await use_case.delete(student_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/teachers", response_model=list[TeacherResponse])
async def list_teachers(
    offset: int = 0,
    limit: int = 100,
    use_case: TeacherAdminUseCase = Depends(get_teacher_admin_use_case),
):
    try:
        return await use_case.list(offset=offset, limit=limit)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(teacher_id: int, use_case: TeacherAdminUseCase = Depends(get_teacher_admin_use_case)):
    try:
        return await use_case.get(teacher_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(payload: TeacherCreateRequest, use_case: TeacherAdminUseCase = Depends(get_teacher_admin_use_case)):
    try:
        return await use_case.create(payload)
    except Exception as exc:
        raise _translate_error(exc)


@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    payload: TeacherUpdateRequest,
    use_case: TeacherAdminUseCase = Depends(get_teacher_admin_use_case),
):
    try:
        return await use_case.update(teacher_id, payload)
    except Exception as exc:
        raise _translate_error(exc)


@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(teacher_id: int, use_case: TeacherAdminUseCase = Depends(get_teacher_admin_use_case)):
    try:
        await use_case.delete(teacher_id)
    except Exception as exc:
        raise _translate_error(exc)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    offset: int = 0,
    limit: int = 100,
    current_user: DomainUser = Depends(get_current_admin),
    audit: AuditLogger = Depends(get_audit_logger),
):
    return await audit.list_for_organization(current_user.organization_id, offset=offset, limit=limit)


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(service: CurriculumBrowseService = Depends(get_curriculum_browse_service)):
    return await service.list_courses()


@router.get("/courses/{course_id}/chapters", response_model=list[ChapterResponse])
async def list_chapters(course_id: int, service: CurriculumBrowseService = Depends(get_curriculum_browse_service)):
    try:
        return await service.list_chapters(course_id)
    except CurriculumNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/chapters/{chapter_id}/lessons", response_model=list[LessonResponse])
async def list_lessons(chapter_id: int, service: CurriculumBrowseService = Depends(get_curriculum_browse_service)):
    try:
        return await service.list_lessons(chapter_id)
    except CurriculumNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/courses/{course_id}/lessons", response_model=list[CourseLessonResponse])
async def list_course_lessons(course_id: int, service: CurriculumBrowseService = Depends(get_curriculum_browse_service)):
    try:
        return await service.list_lessons_for_course(course_id)
    except CurriculumNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/placement-test", response_model=AdminPlacementTestResponse)
async def get_placement_test(
    current_user: DomainUser = Depends(get_current_admin),
    repo: PlacementTestRepositoryImpl = Depends(get_placement_test_repo),
):
    test = await repo.get_active_for_organization(current_user.organization_id)
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No placement test has been generated yet")
    return AdminPlacementTestResponse(
        placement_test_id=test.id,
        title=test.title,
        subject=test.subject,
        questions=[
            {
                "question_id": q.id,
                "question": q.question,
                "question_type": q.type,
                "options": list(q.metadata.get("options", [])) if isinstance(q.metadata, dict) else [],
                "answer": q.metadata.get("answer") if isinstance(q.metadata, dict) else None,
                "explanation": q.metadata.get("explanation") if isinstance(q.metadata, dict) else None,
            }
            for q in test.questions
        ],
    )


@router.put("/placement-test", response_model=AdminPlacementTestResponse)
async def update_placement_test(
    payload: AdminPlacementTestUpdateRequest,
    current_user: DomainUser = Depends(get_current_admin),
    repo: PlacementTestRepositoryImpl = Depends(get_placement_test_repo),
    audit: AuditLogger = Depends(get_audit_logger),
):
    existing = await repo.get_active_for_organization(current_user.organization_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No placement test has been generated yet")

    updated = await repo.replace_questions(
        placement_test_id=existing.id,
        organization_id=current_user.organization_id,
        title=payload.title,
        subject=payload.subject,
        questions=[
            {
                "question": q.question,
                "type": q.question_type,
                "options": q.options,
                "answer": q.answer,
                "explanation": q.explanation,
            }
            for q in payload.questions
        ],
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Placement test not found")

    await audit.log(
        organization_id=current_user.organization_id,
        actor_user_id=current_user.id,
        action="placement_test.edit",
        resource_type="placement_test",
        resource_id=updated.id,
        metadata={"question_count": len(updated.questions)},
    )
    await repo.session.commit()

    return AdminPlacementTestResponse(
        placement_test_id=updated.id,
        title=updated.title,
        subject=updated.subject,
        questions=[
            {
                "question_id": q.id,
                "question": q.question,
                "question_type": q.type,
                "options": list(q.metadata.get("options", [])) if isinstance(q.metadata, dict) else [],
                "answer": q.metadata.get("answer") if isinstance(q.metadata, dict) else None,
                "explanation": q.metadata.get("explanation") if isinstance(q.metadata, dict) else None,
            }
            for q in updated.questions
        ],
    )
