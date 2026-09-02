from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RefreshToken:
    id: Optional[int]
    token: str
    user_id: int
    expires_at: Optional[datetime] = None
    revoked: bool = False
