from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.enums import QuestionType


class QuestionCreateRequest(BaseModel):
    quiz_id: int
    question: str = Field(..., min_length=1)
    type: QuestionType
    metadata: Optional[Any] = None

    model_config = ConfigDict()


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    question: str
    type: QuestionType
    metadata: Optional[Any]
