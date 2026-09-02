from typing import Optional

from pydantic import BaseModel, ConfigDict


class QuizDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    lesson_id: int
