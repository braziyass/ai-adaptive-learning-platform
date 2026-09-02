from __future__ import annotations

from typing import Any

from app.infrastructure.ai.parser.json_parser import JSONParser
from app.infrastructure.ai.prompts.prompt_builder import PromptBuilder
from app.infrastructure.ai.retriever.retriever_service import RetrieverService
from app.infrastructure.ai.types import GenerationRequest, RetrievedChunk
from app.infrastructure.ai.validators.validation_service import ValidationService


class BaseGenerator:
    def __init__(self, retriever: RetrieverService, prompt_builder: PromptBuilder, parser: JSONParser, validator: ValidationService, chat_client: Any) -> None:
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.parser = parser
        self.validator = validator
        self.chat_client = chat_client

    def _generate(self, request: GenerationRequest, top_k: int, prompt: str) -> tuple[dict[str, Any], list[RetrievedChunk]]:
        chunks = self.retriever.retrieve(request.instruction or request.title or request.subject, top_k=top_k)
        self.validator.ensure_non_empty_chunks(chunks)
        response_text = self.chat_client.complete(prompt=prompt)
        payload = self.parser.parse(response_text)
        return payload, chunks
