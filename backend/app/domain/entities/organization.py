from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Organization:
    id: Optional[int]
    name: str
    slug: str
    plan: str = "standard"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
