from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PdfIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_document: str
    chunk_count: int
    vector_ids: list[int] = Field(default_factory=list)


class GenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=255)
    level: int = Field(ge=1)
    course_id: int | None = None
    chapter_id: int | None = None
    lesson_id: int | None = None
    student_id: int | None = None
    instruction: str = Field(default="")
    extra_context: dict[str, Any] = Field(default_factory=dict)
    locale: str | None = None


class GeneratedArtifactResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_type: Literal["lesson", "quiz", "placement_test", "validation_test"]
    artifact_id: int | None = None
    title: str
    payload: dict[str, Any] = Field(default_factory=dict)
