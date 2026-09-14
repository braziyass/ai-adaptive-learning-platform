from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    id: Optional[int]
    title: str
    subject: str
    organization_id: Optional[int] = None
