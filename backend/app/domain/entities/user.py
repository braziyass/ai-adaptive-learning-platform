from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.enums import Role


@dataclass
class User:
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    password: str
    role: Role = Role.STUDENT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
