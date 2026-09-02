from dataclasses import dataclass
from typing import Optional


@dataclass
class Quiz:
    id: Optional[int]
    lesson_id: int
