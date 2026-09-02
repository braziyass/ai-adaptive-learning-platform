from .auth import router as auth_router
from .admin import router as admin_router
from .student import router as student_router
from .teacher import router as teacher_router

__all__ = ["auth_router", "admin_router", "student_router", "teacher_router"]
