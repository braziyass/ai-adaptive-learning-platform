from dataclasses import dataclass
from typing import Optional


@dataclass
class Lesson:
    id: Optional[int]
    chapter_id: int
    title: str
    content: str
