from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    id: Optional[int]
    user_id: int
    current_level: int = 1
    placement_score: int = 0
    points: int = 0
    placement_completed_at: Optional[datetime] = None
