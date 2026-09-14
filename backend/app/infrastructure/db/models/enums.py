import enum


class RoleEnum(enum.Enum):
    platform_admin = "platform_admin"
    administrator = "administrator"
    teacher = "teacher"
    student = "student"


class QuestionTypeEnum(enum.Enum):
    multiple_choice = "multiple_choice"
    short_answer = "short_answer"
    true_false = "true_false"
