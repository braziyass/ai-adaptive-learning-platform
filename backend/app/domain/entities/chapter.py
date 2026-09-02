from dataclasses import dataclass
from typing import Optional


@dataclass
class Chapter:
    id: Optional[int]
    course_id: int
    title: str
    order: int
