from __future__ import annotations

from typing import Any


class ValidationService:
    def ensure_non_empty_chunks(self, chunks: list[dict[str, Any]] | list[Any]) -> None:
        if not chunks:
            raise ValueError("RAG retrieval returned no chunks")

    def validate_lesson_payload(self, payload: dict[str, Any]) -> None:
        if not payload.get("title") or not payload.get("content"):
            raise ValueError("Lesson payload is missing title or content")

    def validate_quiz_payload(self, payload: dict[str, Any]) -> None:
        questions = payload.get("questions")
        if not payload.get("title") or not isinstance(questions, list) or not questions:
            raise ValueError("Quiz payload is invalid")

    def validate_assessment_payload(self, payload: dict[str, Any]) -> None:
        questions = payload.get("questions")
        if not payload.get("title") or not isinstance(questions, list) or not questions:
            raise ValueError("Assessment payload is invalid")