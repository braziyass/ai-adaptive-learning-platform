from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

from app.domain.entities.enums import QuestionType


class QuestionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    quiz_id: int
    question: str
    type: QuestionType
    metadata: Optional[Any]
