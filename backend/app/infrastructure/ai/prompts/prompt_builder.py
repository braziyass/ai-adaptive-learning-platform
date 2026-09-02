from __future__ import annotations

from app.infrastructure.ai.types import GenerationRequest, RetrievedChunk


class PromptBuilder:
    def build_lesson_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        return self._build_prompt(
            request,
            chunks,
            "Générez une leçon en JSON avec les clés : title, content, objectives, summary, references. Répondez en français.",
        )

    def build_quiz_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        return self._build_prompt(
            request,
            chunks,
            "Générez un quiz en JSON avec les clés : title, questions. Chaque question doit inclure question, type, options, answer, explanation. Répondez en français.",
        )

    def build_placement_test_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        return self._build_prompt(
            request,
            chunks,
            "Générez un test de positionnement en JSON avec les clés : title, questions, scoring_rules. Répondez en français.",
        )

    def build_validation_test_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        return self._build_prompt(
            request,
            chunks,
            "Générez un test de validation en JSON avec les clés : title, questions, pass_mark, scoring_rules. Répondez en français.",
        )

    def _build_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk], instruction: str) -> str:
        context_lines = []
        for chunk in chunks:
            context_lines.append(f"[chunk:{chunk.chunk_id}|score:{chunk.score:.3f}] {chunk.text}")
        context = "\n\n".join(context_lines)
        return (
            f"Vous êtes un générateur de contenu pédagogique.\n"
            f"Matière : {request.subject}\n"
            f"Niveau : {request.level}\n"
            f"Titre : {request.title}\n"
            f"Instruction : {instruction}\n"
            f"Retournez uniquement du JSON valide.\n\n"
            f"Extraits source pertinents :\n{context}\n\n"
            f"Contexte supplémentaire : {request.extra_context}\n"
            f"Instruction utilisateur : {request.instruction}"
        )