from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RAGChunkDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: int
    source_document: str
    chunk_index: int
    page_number: int | None = None
    text: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class GeneratedQuestionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    question_type: Literal["multiple_choice", "true_false", "short_answer"]
    options: list[str] = Field(default_factory=list)
    answer: str
    explanation: str


class GeneratedLessonDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    content: str
    learning_objectives: list[str] = Field(default_factory=list)
    source_chunk_ids: list[int] = Field(default_factory=list)


class GeneratedQuizDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    questions: list[GeneratedQuestionDTO] = Field(default_factory=list)
    source_chunk_ids: list[int] = Field(default_factory=list)


class GeneratedTestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    test_type: str
    level: int | None = None
    description: str
    questions: list[GeneratedQuestionDTO] = Field(default_factory=list)
    source_chunk_ids: list[int] = Field(default_factory=list)


class GeneratedArtifactResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_type: str
    artifact_id: int | None = None
    title: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestionResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_document: str
    chunk_count: int
    vector_ids: list[int] = Field(default_factory=list)