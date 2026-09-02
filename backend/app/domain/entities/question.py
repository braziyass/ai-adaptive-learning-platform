from dataclasses import dataclass
from typing import Optional, Any

from app.domain.entities.enums import QuestionType


@dataclass
class Question:
    id: Optional[int]
    quiz_id: int
    question: str
    type: QuestionType
    metadata: Optional[Any] = None
