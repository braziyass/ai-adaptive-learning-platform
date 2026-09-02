from .user import UserDTO
from .student import StudentDTO
from .teacher import TeacherDTO
from .course import CourseDTO
from .chapter import ChapterDTO
from .lesson import LessonDTO
from .quiz import QuizDTO
from .question import QuestionDTO
from .student_progress import StudentProgressDTO
from .admin_students import StudentAdminCreateDTO, StudentAdminUpdateDTO, StudentAdminReadDTO
from .admin_teachers import TeacherAdminCreateDTO, TeacherAdminUpdateDTO, TeacherAdminReadDTO
from .student_module import (
    StudentProfileDTO,
    StudentCurrentLevelDTO,
    StudentProgressItemDTO,
    UnlockedLessonDTO,
    CompletedQuizDTO,
    ValidationTestResultDTO,
)
from .teacher_module import (
    TeacherStudentSummaryDTO,
    TeacherProgressItemDTO,
    PlacementTestResultDTO,
    ValidationTestResultDTO as TeacherValidationTestResultDTO,
    TeacherStatisticsDTO,
)

__all__ = [
    "UserDTO",
    "StudentDTO",
    "TeacherDTO",
    "CourseDTO",
    "ChapterDTO",
    "LessonDTO",
    "QuizDTO",
    "QuestionDTO",
    "StudentProgressDTO",
    "StudentAdminCreateDTO",
    "StudentAdminUpdateDTO",
    "StudentAdminReadDTO",
    "TeacherAdminCreateDTO",
    "TeacherAdminUpdateDTO",
    "TeacherAdminReadDTO",
    "StudentProfileDTO",
    "StudentCurrentLevelDTO",
    "StudentProgressItemDTO",
    "UnlockedLessonDTO",
    "CompletedQuizDTO",
    "ValidationTestResultDTO",
    "TeacherStudentSummaryDTO",
    "TeacherProgressItemDTO",
    "PlacementTestResultDTO",
    "TeacherValidationTestResultDTO",
    "TeacherStatisticsDTO",
]
