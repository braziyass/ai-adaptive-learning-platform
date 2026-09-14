from enum import Enum


class Role(Enum):
    PLATFORM_ADMIN = "platform_admin"
    ADMINISTRATOR = "administrator"
    TEACHER = "teacher"
    STUDENT = "student"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
