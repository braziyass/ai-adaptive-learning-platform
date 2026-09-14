from __future__ import annotations

from pathlib import Path
import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generated_artifact import GeneratedArtifact
from app.domain.entities.chapter import Chapter as DomainChapter
from app.domain.entities.course import Course as DomainCourse
from app.domain.entities.lesson import Lesson as DomainLesson
from app.domain.entities.quiz import Quiz as DomainQuiz
from app.domain.entities.question import Question as DomainQuestion
from app.infrastructure.ai.chunking.chunking_service import ChunkingService
from app.infrastructure.ai.cleaning.text_cleaner import TextCleaner
from app.infrastructure.ai.config import AISettings
from app.infrastructure.ai.embeddings.embedding_service import EmbeddingService
from app.infrastructure.ai.extraction.pdf_extractor import PDFExtractor
from app.infrastructure.ai.generators.lessons.lesson_generator import LessonGenerator
from app.infrastructure.ai.generators.placement.placement_test_generator import PlacementTestGenerator
from app.infrastructure.ai.generators.quizzes.quiz_generator import QuizGenerator
from app.infrastructure.ai.generators.validation.validation_test_generator import ValidationTestGenerator
from app.infrastructure.ai.parser.json_parser import JSONParser
from app.infrastructure.ai.prompts.prompt_builder import PromptBuilder
from app.infrastructure.ai.retriever.retriever_service import RetrieverService
from app.infrastructure.ai.types import GenerationRequest, SourceChunk
from app.infrastructure.ai.validators.validation_service import ValidationService
from app.infrastructure.ai.vectorstore.vectorstore_service import VectorStoreService
from app.infrastructure.db.repositories.generated_artifact_repository import SQLAlchemyGeneratedArtifactRepository
from app.infrastructure.db.repositories import (
    get_chapter_repository,
    get_course_repository,
    get_lesson_repository,
    get_placement_test_repository,
    get_question_repository,
    get_quiz_repository,
)


class GroqChatClient:
    def __init__(self, model: str, api_key: str | None = None, allow_fallback: bool = False) -> None:
        self.model = model
        self.api_key = (api_key or "").strip()
        self.allow_fallback = allow_fallback

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            if self.allow_fallback:
                return self._fallback_response(prompt)
            raise RuntimeError("Groq API key is not configured. Set GROQ_API_KEY in backend/.env and keep AI_USE_FALLBACK=false for a real AI setup.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            if self.allow_fallback:
                return self._fallback_response(prompt)
            raise RuntimeError("The OpenAI Python SDK is not installed.") from exc

        try:
            client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or "{}"
        except Exception as exc:
            if self.allow_fallback:
                return self._fallback_response(prompt)
            raise RuntimeError(f"Groq request failed: {exc}") from exc

    def _fallback_response(self, prompt: str) -> str:
        title_match = re.search(r"^(?:Title|Titre):\s*(.+)$", prompt, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Contenu généré"
        if "placement test" in prompt.lower():
            payload = {
                "title": title,
                "content": "Un test de positionnement local généré à partir du PDF ingéré.",
                "questions": [
                    {
                        "question": "Quelle est l'idée principale abordée dans le PDF ?",
                        "type": "multiple_choice",
                        "options": ["Concepts", "Histoire", "Mathématiques", "Aucune des réponses"],
                        "answer": "Concepts",
                        "explanation": "Question de secours générée sans accès à Groq.",
                    }
                ],
                "scoring_rules": {"correct": 1, "incorrect": 0},
                "pass_mark": 50,
            }
        elif "validation test" in prompt.lower():
            payload = {
                "title": title,
                "content": "Un test de validation local généré à partir du PDF ingéré.",
                "questions": [
                    {
                        "question": "Citez un point clé du PDF.",
                        "type": "short_answer",
                        "options": [],
                        "answer": "Un point clé du PDF",
                        "explanation": "Question de validation de secours.",
                    }
                ],
                "scoring_rules": {"correct": 1, "incorrect": 0},
                "pass_mark": 50,
            }
        elif "quiz" in prompt.lower():
            count_match = re.search(r"quiz de (\d+) question", prompt.lower())
            count = int(count_match.group(1)) if count_match else 1
            payload = {
                "title": title,
                "content": "Un quiz local généré à partir du PDF ingéré.",
                "questions": [
                    {
                        "question": f"Question de secours {index + 1} : quel sujet a été introduit dans le PDF ?",
                        "type": "multiple_choice",
                        "options": ["Sujet A", "Sujet B", "Sujet C", "Sujet D"],
                        "answer": "Sujet A",
                        "explanation": "Question de quiz de secours.",
                    }
                    for index in range(count)
                ],
            }
        else:
            payload = {
                "title": title,
                "content": "Une leçon locale générée à partir du PDF ingéré.",
                "objectives": ["Revoir les idées principales du PDF"],
                "summary": "Sortie de leçon de secours créée sans accès à Groq.",
                "references": ["pdf1.pdf"],
                "questions": [
                    {
                        "question": "Quelle idée retenez-vous de la leçon ?",
                        "type": "short_answer",
                        "options": [],
                        "answer": "Une idée principale de la leçon",
                        "explanation": "Question de leçon de secours.",
                    }
                ],
                "scoring_rules": {"correct": 1, "incorrect": 0},
                "pass_mark": 50,
            }
        return json.dumps(payload)


class Worker:
    def __init__(
        self,
        session: AsyncSession,
        organization_id: int,
        settings: AISettings | None = None,
        api_key: str | None = None,
        allow_fallback: bool | None = None,
    ) -> None:
        self.session = session
        self.organization_id = organization_id
        self.settings = settings or AISettings()
        self.allow_fallback = self.settings.allow_fallback if allow_fallback is None else allow_fallback
        self.pdf_extractor = PDFExtractor()
        self.text_cleaner = TextCleaner()
        self.chunking_service = ChunkingService(self.settings.chunk_size, self.settings.chunk_overlap)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService(self.embedding_service, self.settings.cache_dir / "faiss.index", self.settings.cache_dir / "chunks.json")
        self.retriever = RetrieverService(self.vector_store)
        self.prompt_builder = PromptBuilder()
        self.parser = JSONParser()
        self.validator = ValidationService()
        self.chat_client = GroqChatClient(self.settings.groq_chat_model, api_key=api_key, allow_fallback=self.allow_fallback)
        self.lesson_generator = LessonGenerator(self.retriever, self.prompt_builder, self.parser, self.validator, self.chat_client)
        self.quiz_generator = QuizGenerator(self.retriever, self.prompt_builder, self.parser, self.validator, self.chat_client)
        self.placement_generator = PlacementTestGenerator(self.retriever, self.prompt_builder, self.parser, self.validator, self.chat_client)
        self.validation_generator = ValidationTestGenerator(self.retriever, self.prompt_builder, self.parser, self.validator, self.chat_client)
        self.generated_artifact_repository = SQLAlchemyGeneratedArtifactRepository(self.session)
        self.course_repository = get_course_repository(self.session)
        self.chapter_repository = get_chapter_repository(self.session)
        self.lesson_repository = get_lesson_repository(self.session)
        self.quiz_repository = get_quiz_repository(self.session)
        self.question_repository = get_question_repository(self.session)
        self.placement_test_repository = get_placement_test_repository(self.session)

    def _format_lesson_content(self, payload: dict) -> str:
        sections: list[str] = []
        summary = payload.get("summary")
        objectives = payload.get("objectives")
        content = payload.get("content")
        references = payload.get("references")

        if isinstance(summary, str) and summary.strip():
            sections.append(f"Résumé\n{summary.strip()}")
        if isinstance(objectives, list) and objectives:
            objective_lines = "\n".join(f"- {str(item)}" for item in objectives if str(item).strip())
            if objective_lines:
                sections.append(f"Objectifs d'apprentissage\n{objective_lines}")
        if isinstance(content, str) and content.strip():
            sections.append(f"Leçon\n{content.strip()}")
        if isinstance(references, list) and references:
            reference_lines = "\n".join(f"- {str(item)}" for item in references if str(item).strip())
            if reference_lines:
                sections.append(f"Références\n{reference_lines}")

        if sections:
            return "\n\n".join(sections)
        return str(content or payload.get("title", ""))

    async def _resolve_chapter_for_course(
        self, course_id: int | None, course_title: str | None, level: int, request: GenerationRequest
    ) -> int:
        """Find-or-create the (course, level) pairing a lesson belongs to.

        The admin-facing model only has "Matière" (subject) and "Cours"
        (course); chapters exist purely as the internal bookkeeping unit
        tying a course's "Niveau" to the leveling engine's chapter.order,
        so they're never surfaced or chosen directly.
        """
        if course_id is not None:
            course = await self.course_repository.get_by_id(course_id, organization_id=self.organization_id)
            if course is None:
                raise RuntimeError("Course does not belong to this organization")
        else:
            course = await self.course_repository.create(
                DomainCourse(
                    id=None,
                    title=course_title or f"{request.subject} - Cours",
                    subject=request.subject,
                    organization_id=self.organization_id,
                ),
            )

        existing_chapter = await self.chapter_repository.get_by_course_and_order(course.id, level)
        if existing_chapter is not None:
            return existing_chapter.id

        created_chapter = await self.chapter_repository.create(
            DomainChapter(
                id=None,
                course_id=course.id,
                title=f"Niveau {level}",
                order=level,
            ),
        )
        return created_chapter.id

    async def _store_artifact(self, artifact: GeneratedArtifact) -> GeneratedArtifact:
        try:
            stored_artifact = await self.generated_artifact_repository.create(artifact)
            await self.session.commit()
            return stored_artifact
        except Exception:
            await self.session.rollback()
            raise

    def ingest_pdf(self, pdf_path: str | Path, source_id: str) -> list[SourceChunk]:
        pages = self.pdf_extractor.extract(pdf_path)
        cleaned_pages = [{"page_number": page["page_number"], "text": self.text_cleaner.clean(str(page["text"]))} for page in pages]
        chunks = self.chunking_service.chunk_pages(source_id=source_id, pages=cleaned_pages)
        self.vector_store.add_chunks(chunks)
        return chunks

    async def generate_lesson(self, request: GenerationRequest, course_id: int | None, course_title: str | None) -> int:
        content = self.lesson_generator.generate(request)
        resolved_chapter_id = await self._resolve_chapter_for_course(course_id, course_title, request.level, request)
        lesson_content = self._format_lesson_content(content.payload)
        lesson = await self.lesson_repository.create(
            DomainLesson(
                id=None,
                chapter_id=resolved_chapter_id,
                title=content.title,
                content=lesson_content,
            ),
        )
        artifact = await self._store_artifact(
            GeneratedArtifact(
                id=None,
                artifact_type="lesson",
                organization_id=self.organization_id,
                title=content.title,
                subject=request.subject,
                level=request.level,
                payload=content.payload,
                source_chunks=[chunk.__dict__ for chunk in content.source_chunks],
                course_id=request.course_id,
                chapter_id=resolved_chapter_id,
                lesson_id=lesson.id,
                student_id=request.student_id,
            )
        )
        return artifact.id

    async def generate_quiz(self, request: GenerationRequest, lesson_id: int) -> int:
        content = self.quiz_generator.generate(request)
        quiz = await self.quiz_repository.get_by_lesson_id(lesson_id)
        if quiz is not None:
            await self.quiz_repository.delete(quiz.id)
        created_quiz = await self.quiz_repository.create(DomainQuiz(id=None, lesson_id=lesson_id))
        for item in content.payload.get("questions", []):
            if not isinstance(item, dict):
                continue
            question_text = str(item.get("question", "")).strip()
            if not question_text:
                continue
            question_type = str(item.get("type", "multiple_choice"))
            metadata = {
                "options": item.get("options", []),
                "answer": item.get("answer"),
                "explanation": item.get("explanation"),
            }
            await self.question_repository.create(
                DomainQuestion(
                    id=None,
                    quiz_id=created_quiz.id,
                    question=question_text,
                    type=question_type,
                    metadata=metadata,
                )
            )
        artifact = await self._store_artifact(
            GeneratedArtifact(
                id=None,
                artifact_type="quiz",
                organization_id=self.organization_id,
                title=content.title,
                subject=request.subject,
                level=request.level,
                payload=content.payload,
                source_chunks=[chunk.__dict__ for chunk in content.source_chunks],
                course_id=request.course_id,
                chapter_id=request.chapter_id,
                lesson_id=lesson_id,
                student_id=request.student_id,
            )
        )
        return artifact.id

    async def generate_placement_test(self, request: GenerationRequest) -> int:
        content = self.placement_generator.generate(request)
        questions = content.payload.get("questions", [])
        if isinstance(questions, list) and questions:
            await self.placement_test_repository.deactivate_active(self.organization_id)
            await self.placement_test_repository.create_with_questions(
                organization_id=self.organization_id,
                subject=request.subject,
                title=content.title,
                questions=[q for q in questions if isinstance(q, dict)],
            )
        artifact = await self._store_artifact(
            GeneratedArtifact(
                id=None,
                artifact_type="placement_test",
                organization_id=self.organization_id,
                title=content.title,
                subject=request.subject,
                level=request.level,
                payload=content.payload,
                source_chunks=[chunk.__dict__ for chunk in content.source_chunks],
                course_id=request.course_id,
                chapter_id=request.chapter_id,
                lesson_id=request.lesson_id,
                student_id=request.student_id,
            )
        )
        return artifact.id

    async def generate_validation_test(self, request: GenerationRequest) -> int:
        content = self.validation_generator.generate(request)
        artifact = await self._store_artifact(
            GeneratedArtifact(
                id=None,
                artifact_type="validation_test",
                organization_id=self.organization_id,
                title=content.title,
                subject=request.subject,
                level=request.level,
                payload=content.payload,
                source_chunks=[chunk.__dict__ for chunk in content.source_chunks],
                course_id=request.course_id,
                chapter_id=request.chapter_id,
                lesson_id=request.lesson_id,
                student_id=request.student_id,
            )
        )
        return artifact.id
