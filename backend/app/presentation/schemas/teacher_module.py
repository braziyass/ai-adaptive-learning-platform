from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class TeacherStudentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    current_level: int
    placement_score: int


class TeacherProgressResponseItem(BaseModel):
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


class PlacementTestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    placement_score: int
    current_level: int
    assigned_level: int


class ValidationTestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    lesson_id: int
    lesson_title: str
    chapter_id: int
    chapter_title: str
    level: int
    score: Optional[int]
    passed: bool
    attempts: int


class TeacherStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_students: int
    average_placement_score: float
    average_current_level: float
    total_completed_lessons: int
    completion_rate: float
    validation_pass_rate: float
