from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentProgress:
    student_id: int
    lesson_id: int
    completed: bool = False
    score: Optional[int] = None
    attempts: int = 0
