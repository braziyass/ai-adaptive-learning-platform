from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class PlacementTestQuestion:
    id: Optional[int]
    placement_test_id: int
    question: str
    type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlacementTest:
    id: Optional[int]
    organization_id: int
    subject: str
    title: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    questions: list[PlacementTestQuestion] = field(default_factory=list)
