from sqlalchemy.ext.asyncio import AsyncSession

from .user import UserRepositoryImpl
from .student import StudentRepositoryImpl
from .teacher import TeacherRepositoryImpl
from .course import CourseRepositoryImpl
from .chapter import ChapterRepositoryImpl
from .lesson import LessonRepositoryImpl
from .quiz import QuizRepositoryImpl
from .question import QuestionRepositoryImpl
from .student_progress import StudentProgressRepositoryImpl
from .refresh_token import RefreshTokenRepositoryImpl
from .generated_test import GeneratedTestRepositoryImpl
from .placement_test import PlacementTestRepositoryImpl

__all__ = [
    "UserRepositoryImpl",
    "StudentRepositoryImpl",
    "TeacherRepositoryImpl",
    "CourseRepositoryImpl",
    "ChapterRepositoryImpl",
    "LessonRepositoryImpl",
    "QuizRepositoryImpl",
    "QuestionRepositoryImpl",
    "StudentProgressRepositoryImpl",
    "GeneratedTestRepositoryImpl",
    "RefreshTokenRepositoryImpl",
    "PlacementTestRepositoryImpl",
]


def get_user_repository(session: AsyncSession) -> UserRepositoryImpl:
    return UserRepositoryImpl(session)


def get_student_repository(session: AsyncSession) -> StudentRepositoryImpl:
    return StudentRepositoryImpl(session)


def get_teacher_repository(session: AsyncSession) -> TeacherRepositoryImpl:
    return TeacherRepositoryImpl(session)


def get_course_repository(session: AsyncSession) -> CourseRepositoryImpl:
    return CourseRepositoryImpl(session)


def get_chapter_repository(session: AsyncSession) -> ChapterRepositoryImpl:
    return ChapterRepositoryImpl(session)


def get_lesson_repository(session: AsyncSession) -> LessonRepositoryImpl:
    return LessonRepositoryImpl(session)


def get_quiz_repository(session: AsyncSession) -> QuizRepositoryImpl:
    return QuizRepositoryImpl(session)


def get_question_repository(session: AsyncSession) -> QuestionRepositoryImpl:
    return QuestionRepositoryImpl(session)


def get_student_progress_repository(session: AsyncSession) -> StudentProgressRepositoryImpl:
    return StudentProgressRepositoryImpl(session)


def get_generated_test_repository(session: AsyncSession) -> GeneratedTestRepositoryImpl:
    return GeneratedTestRepositoryImpl(session)


def get_refresh_token_repository(session: AsyncSession) -> RefreshTokenRepositoryImpl:
    return RefreshTokenRepositoryImpl(session)


def get_placement_test_repository(session: AsyncSession) -> PlacementTestRepositoryImpl:
    return PlacementTestRepositoryImpl(session)
