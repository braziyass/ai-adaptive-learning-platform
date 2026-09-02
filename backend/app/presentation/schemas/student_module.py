from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    current_level: int
    placement_score: int


class StudentCurrentLevelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    current_level: int


class StudentProgressResponseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    chapter_order: int
    completed: bool
    score: Optional[int]
    attempts: int


class UnlockedLessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    chapter_order: int
    content: str
    completed: bool
    score: Optional[int]
    attempts: int
    quiz_id: Optional[int]


class AvailableQuizQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: Optional[int] = None
    question: str
    question_type: str
    options: list[str] = []
    explanation: Optional[str] = None


class AvailableQuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_id: int
    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    chapter_order: int
    title: str
    questions: list[AvailableQuizQuestionResponse] = []


class CompletedQuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_id: int
    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    score: Optional[int]
    attempts: int


class ValidationTestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_id: int
    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    level: int
    score: Optional[int]
    passed: bool
    attempts: int


class QuizSubmissionQuestionResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    correct: bool
    correct_answer: str | None = None
    explanation: str | None = None


class QuizSubmissionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    answers: list[dict]


class QuizSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quiz_id: int
    lesson_id: int
    score: int | None
    total: int
    correct: int
    attempts: int
    details: list[QuizSubmissionQuestionResultResponse] = []
