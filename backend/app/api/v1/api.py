from fastapi import APIRouter
from app.api.v1.routers import auth, admin, student, teacher
from app.api.v1.routers.ai import router as ai_router


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(ai_router, tags=["ai"])
api_router.include_router(student.router, tags=["student"])
api_router.include_router(teacher.router, tags=["teacher"])
