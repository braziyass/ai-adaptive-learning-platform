from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StudentProgressCreateRequest(BaseModel):
    student_id: int
    lesson_id: int
    completed: bool = Field(default=False)
    score: Optional[int] = None
    attempts: int = Field(default=0, ge=0)

    model_config = ConfigDict()


class StudentProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    lesson_id: int
    completed: bool
    score: Optional[int]
    attempts: int
