from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class AuditLog:
    id: Optional[int]
    organization_id: int
    actor_user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
