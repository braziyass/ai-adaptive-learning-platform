from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    id: Optional[int]
    user_id: int
    current_level: int = 1
    placement_score: int = 0
