from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class AIGeneratedTest:
    id: Optional[int]
    course_id: Optional[int]
    student_id: Optional[int]
    level: Optional[int]
    test_type: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)