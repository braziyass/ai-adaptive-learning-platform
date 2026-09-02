from dataclasses import dataclass
from typing import Optional


@dataclass
class Teacher:
    id: Optional[int]
    user_id: int
