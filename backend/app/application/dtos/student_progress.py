from typing import Optional

from pydantic import BaseModel, ConfigDict


class StudentProgressDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    lesson_id: int
    completed: bool
    score: Optional[int]
    attempts: int
