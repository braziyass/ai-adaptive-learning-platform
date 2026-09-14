from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    text: str
    source_id: str
    page_number: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    source_id: str
    score: float
    page_number: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationRequest:
    title: str
    subject: str
    level: int
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    chapter_id: Optional[int] = None
    lesson_id: Optional[int] = None
    student_id: Optional[int] = None
    question_count: Optional[int] = None
    instruction: str = ""
    extra_context: dict[str, Any] = field(default_factory=dict)
    locale: Optional[str] = None


@dataclass(frozen=True)
class GeneratedContent:
    title: str
    payload: dict[str, Any]
    source_chunks: list[RetrievedChunk]
