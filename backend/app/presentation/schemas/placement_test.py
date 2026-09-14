from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AdminPlacementTestQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    question: str
    question_type: str
    options: list[str] = []
    answer: str | None = None
    explanation: str | None = None


class AdminPlacementTestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    placement_test_id: int
    title: str
    subject: str
    questions: list[AdminPlacementTestQuestionResponse] = []


class PlacementTestQuestionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    question_type: str = "multiple_choice"
    options: list[str] = Field(default_factory=list)
    answer: str | None = None
    explanation: str | None = None


class AdminPlacementTestUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=255)
    questions: list[PlacementTestQuestionInput] = Field(min_length=1)
