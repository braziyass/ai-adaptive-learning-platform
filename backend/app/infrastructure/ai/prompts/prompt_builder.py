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
        count = request.question_count or 5
        return self._build_prompt(
            request,
            chunks,
            f"Générez un quiz de {count} question(s) en JSON avec les clés : title, questions. "
            f"Le tableau questions doit contenir exactement {count} question(s). "
            "Chaque question doit inclure question, type, options, answer, explanation. Répondez en français.",
        )

    def build_placement_test_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        count = request.question_count or 20
        instruction = (
            f"Générez un test de positionnement UNIQUE de {count} question(s) couvrant l'ensemble des sujets/cours "
            f"fournis en contexte (pas un seul niveau ou une seule matière) en JSON avec les clés : title, questions, "
            f"scoring_rules. Le tableau questions doit contenir exactement {count} question(s), réparties le plus "
            "également possible sur les différents cours fournis. Répondez en français."
        )
        return self._build_prompt(request, chunks, instruction, include_level=False)

    def build_validation_test_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk]) -> str:
        return self._build_prompt(
            request,
            chunks,
            "Générez un test de validation en JSON avec les clés : title, questions, pass_mark, scoring_rules. Répondez en français.",
        )

    def _build_prompt(self, request: GenerationRequest, chunks: list[RetrievedChunk], instruction: str, include_level: bool = True) -> str:
        context_lines = []
        for chunk in chunks:
            context_lines.append(f"[chunk:{chunk.chunk_id}|score:{chunk.score:.3f}] {chunk.text}")
        context = "\n\n".join(context_lines)
        level_line = f"Niveau : {request.level}\n" if include_level else ""
        return (
            f"Vous êtes un générateur de contenu pédagogique.\n"
            f"Matière : {request.subject}\n"
            f"{level_line}"
            f"Titre : {request.title}\n"
            f"Instruction : {instruction}\n"
            f"Retournez uniquement du JSON valide.\n\n"
            f"Extraits source pertinents :\n{context}\n\n"
            f"Contexte supplémentaire : {request.extra_context}\n"
            f"Instruction utilisateur : {request.instruction}"
        )