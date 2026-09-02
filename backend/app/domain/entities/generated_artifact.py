from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class GeneratedArtifact:
    id: Optional[int]
    artifact_type: str
    title: str
    subject: str
    level: int
    payload: dict[str, Any]
    source_chunks: list[dict[str, Any]] = field(default_factory=list)
    course_id: Optional[int] = None
    chapter_id: Optional[int] = None
    lesson_id: Optional[int] = None
    student_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
