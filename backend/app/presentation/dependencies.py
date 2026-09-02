from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.student import StudentModuleService
from app.application.services.teacher import TeacherModuleService
from app.application.use_cases.student import StudentModuleUseCase
from app.application.use_cases.teacher import TeacherModuleUseCase
from app.core.database import get_db
from app.application.services.admin import StudentAdminService, TeacherAdminService
from app.application.use_cases.admin import StudentAdminUseCase, TeacherAdminUseCase
from app.domain.entities.enums import Role
from app.infrastructure.auth.token_service import TokenService
from app.infrastructure.db.repositories import get_user_repository
from app.domain.entities.user import User as DomainUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
token_service = TokenService()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> DomainUser:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = token_service.decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = get_user_repository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_admin(current_user: DomainUser = Depends(get_current_user)) -> DomainUser:
    if getattr(current_user.role, "value", current_user.role) != Role.ADMINISTRATOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user


async def get_current_student_user(current_user: DomainUser = Depends(get_current_user)) -> DomainUser:
    if getattr(current_user.role, "value", current_user.role) != Role.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")
    return current_user


async def get_current_teacher_user(current_user: DomainUser = Depends(get_current_user)) -> DomainUser:
    if getattr(current_user.role, "value", current_user.role) != Role.TEACHER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    return current_user


def get_student_admin_service(db: AsyncSession = Depends(get_db)) -> StudentAdminService:
    return StudentAdminService(db)


def get_teacher_admin_service(db: AsyncSession = Depends(get_db)) -> TeacherAdminService:
    return TeacherAdminService(db)


def get_student_admin_use_case(service: StudentAdminService = Depends(get_student_admin_service)) -> StudentAdminUseCase:
    return StudentAdminUseCase(service)


def get_teacher_admin_use_case(service: TeacherAdminService = Depends(get_teacher_admin_service)) -> TeacherAdminUseCase:
    return TeacherAdminUseCase(service)


def get_student_module_service(db: AsyncSession = Depends(get_db)) -> StudentModuleService:
    return StudentModuleService(db)


def get_student_module_use_case(service: StudentModuleService = Depends(get_student_module_service)) -> StudentModuleUseCase:
    return StudentModuleUseCase(service)


def get_teacher_module_service(db: AsyncSession = Depends(get_db)) -> TeacherModuleService:
    return TeacherModuleService(db)


def get_teacher_module_use_case(service: TeacherModuleService = Depends(get_teacher_module_service)) -> TeacherModuleUseCase:
    return TeacherModuleUseCase(service)
