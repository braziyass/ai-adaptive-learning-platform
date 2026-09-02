from __future__ import annotations

from app.infrastructure.ai.generators.base import BaseGenerator
from app.infrastructure.ai.types import GenerationRequest, GeneratedContent


class ValidationTestGenerator(BaseGenerator):
    def generate(self, request: GenerationRequest) -> GeneratedContent:
        chunks = self.retriever.retrieve(request.instruction or request.title or request.subject, top_k=5)
        prompt = self.prompt_builder.build_validation_test_prompt(request, chunks)
        payload = self.parser.parse(self.chat_client.complete(prompt=prompt))
        self.validator.validate_assessment_payload(payload)
        return GeneratedContent(title=payload["title"], payload=payload, source_chunks=chunks)
