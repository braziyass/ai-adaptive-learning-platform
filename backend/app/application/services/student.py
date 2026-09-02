from __future__ import annotations

from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.student_module import (
    AvailableQuizDTO,
    AvailableQuizQuestionDTO,
    CompletedQuizDTO,
    StudentCurrentLevelDTO,
    StudentProfileDTO,
    StudentProgressItemDTO,
    UnlockedLessonDTO,
    ValidationTestResultDTO,
)
from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.models import Chapter as ChapterModel
from app.infrastructure.db.models import Question as QuestionModel
from app.infrastructure.db.models import Lesson as LessonModel
from app.infrastructure.db.models import Quiz as QuizModel
from app.infrastructure.db.models import StudentProgress as ProgressModel
from app.infrastructure.db.repositories import StudentRepositoryImpl, UserRepositoryImpl
from app.infrastructure.db.repositories import QuestionRepositoryImpl, StudentProgressRepositoryImpl, GeneratedTestRepositoryImpl, QuizRepositoryImpl
from app.domain.entities.student_progress import StudentProgress as DomainStudentProgress
from app.domain.entities.generated_test import AIGeneratedTest as DomainGeneratedTest
from app.application.dtos.student_module import QuizSubmissionResultDTO, QuizSubmissionQuestionResultDTO


class StudentModuleError(Exception):
    pass


class StudentNotFoundError(StudentModuleError):
    pass


class StudentPersistenceError(StudentModuleError):
    pass


class StudentModuleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepositoryImpl(session)
        self.student_repo = StudentRepositoryImpl(session)

    async def _load_student_and_user(self, current_user: DomainUser):
        student = await self.student_repo.get_by_user_id(current_user.id)
        if student is None:
            raise StudentNotFoundError("Student profile not found")
        user = await self.user_repo.get_by_id(current_user.id)
        if user is None:
            raise StudentPersistenceError("Student user record is missing")
        return student, user

    async def get_profile(self, current_user: DomainUser) -> StudentProfileDTO:
        student, user = await self._load_student_and_user(current_user)
        return StudentProfileDTO(
            id=student.id,
            user_id=student.user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=str(user.email),
            current_level=student.current_level,
            placement_score=student.placement_score,
        )

    async def get_current_level(self, current_user: DomainUser) -> StudentCurrentLevelDTO:
        student, _ = await self._load_student_and_user(current_user)
        return StudentCurrentLevelDTO(student_id=student.id, current_level=student.current_level)

    async def get_progress(self, current_user: DomainUser) -> Sequence[StudentProgressItemDTO]:
        student, _ = await self._load_student_and_user(current_user)
        stmt = (
            select(ProgressModel, LessonModel, ChapterModel)
            .join(LessonModel, LessonModel.id == ProgressModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .where(ProgressModel.student_id == student.id)
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            StudentProgressItemDTO(
                student_id=progress.student_id,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                chapter_order=chapter.order,
                completed=progress.completed,
                score=progress.score,
                attempts=progress.attempts,
            )
            for progress, lesson, chapter in rows
        ]

    async def get_unlocked_lessons(self, current_user: DomainUser) -> Sequence[UnlockedLessonDTO]:
        student, _ = await self._load_student_and_user(current_user)
        stmt = (
            select(LessonModel, ChapterModel, ProgressModel, QuizModel)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .outerjoin(
                ProgressModel,
                and_(ProgressModel.lesson_id == LessonModel.id, ProgressModel.student_id == student.id),
            )
            .outerjoin(QuizModel, QuizModel.lesson_id == LessonModel.id)
            .where(ChapterModel.order <= student.current_level)
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            UnlockedLessonDTO(
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                chapter_order=chapter.order,
                content=lesson.content,
                completed=bool(progress.completed) if progress is not None else False,
                score=progress.score if progress is not None else None,
                attempts=progress.attempts if progress is not None else 0,
                quiz_id=quiz.id if quiz is not None else None,
            )
            for lesson, chapter, progress, quiz in rows
        ]

    async def get_available_quizzes(self, current_user: DomainUser) -> Sequence[AvailableQuizDTO]:
        student, _ = await self._load_student_and_user(current_user)
        stmt = (
            select(LessonModel, ChapterModel, QuizModel, QuestionModel)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .join(QuizModel, QuizModel.lesson_id == LessonModel.id)
            .outerjoin(QuestionModel, QuestionModel.quiz_id == QuizModel.id)
            .where(ChapterModel.order <= student.current_level)
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc(), QuestionModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        quizzes: dict[int, AvailableQuizDTO] = {}
        for lesson, chapter, quiz, question in rows:
            # Defensive guards: skip rows that lack a quiz (shouldn't normally happen)
            if quiz is None:
                continue
            quiz_item = quizzes.get(quiz.id)
            if quiz_item is None:
                quiz_item = AvailableQuizDTO(
                    quiz_id=quiz.id,
                    lesson_id=lesson.id,
                    lesson_title=lesson.title,
                    chapter_id=chapter.id,
                    chapter_title=chapter.title,
                    chapter_order=chapter.order,
                    title=f"{lesson.title} - Quiz",
                    questions=[],
                )
                quizzes[quiz.id] = quiz_item

            if question is not None:
                try:
                    metadata = question.meta or {}
                    options = metadata.get("options") if isinstance(metadata, dict) else []
                    explanation = metadata.get("explanation") if isinstance(metadata, dict) else None
                    q_type = question.type.value if getattr(question, "type", None) is not None else "multiple_choice"
                    quiz_item.questions.append(
                        AvailableQuizQuestionDTO(
                            question_id=question.id,
                            question=question.question,
                            question_type=q_type,
                            options=list(options) if isinstance(options, list) else [],
                            explanation=explanation if isinstance(explanation, str) else None,
                        )
                    )
                except Exception:
                    # Skip malformed question rows rather than failing the whole endpoint
                    continue

        return list(quizzes.values())

    async def get_completed_quizzes(self, current_user: DomainUser) -> Sequence[CompletedQuizDTO]:
        student, _ = await self._load_student_and_user(current_user)
        stmt = (
            select(QuizModel, LessonModel, ChapterModel, ProgressModel)
            .join(LessonModel, LessonModel.id == QuizModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .join(
                ProgressModel,
                and_(ProgressModel.lesson_id == LessonModel.id, ProgressModel.student_id == student.id),
            )
            .where(ProgressModel.completed.is_(True))
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            CompletedQuizDTO(
                quiz_id=quiz.id,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                score=progress.score,
                attempts=progress.attempts,
            )
            for quiz, lesson, chapter, progress in rows
        ]

    async def get_validation_test_results(self, current_user: DomainUser) -> Sequence[ValidationTestResultDTO]:
        student, _ = await self._load_student_and_user(current_user)
        stmt = (
            select(QuizModel, LessonModel, ChapterModel, ProgressModel)
            .join(LessonModel, LessonModel.id == QuizModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .join(
                ProgressModel,
                and_(ProgressModel.lesson_id == LessonModel.id, ProgressModel.student_id == student.id),
            )
            .where(
                ProgressModel.completed.is_(True),
                ProgressModel.score.is_not(None),
                ChapterModel.order == student.current_level,
            )
            .order_by(ChapterModel.order.asc(), LessonModel.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            ValidationTestResultDTO(
                quiz_id=quiz.id,
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                level=chapter.order,
                score=progress.score,
                passed=bool(progress.score is not None and progress.score >= 80),
                attempts=progress.attempts,
            )
            for quiz, lesson, chapter, progress in rows
        ]

    async def submit_quiz(self, current_user: DomainUser, quiz_id: int, answers: list[dict]) -> QuizSubmissionResultDTO:
        student, _ = await self._load_student_and_user(current_user)

        # initialize repositories
        question_repo = QuestionRepositoryImpl(self.session)
        progress_repo = StudentProgressRepositoryImpl(self.session)
        gen_repo = GeneratedTestRepositoryImpl(self.session)
        quiz_repo = QuizRepositoryImpl(self.session)

        # fetch quiz and related lesson
        quiz = await quiz_repo.get_by_id(quiz_id)
        if quiz is None:
            raise StudentNotFoundError("Quiz not found")

        questions = await question_repo.list_by_quiz(quiz_id)
        total = len(questions)
        correct = 0
        details: list[QuizSubmissionQuestionResultDTO] = []

        # map answers by question_id
        answers_map = {a.get("question_id"): a.get("answer") for a in answers}

        for q in questions:
            meta = q.metadata or {}
            expected = None
            explanation = None
            if isinstance(meta, dict):
                expected = meta.get("answer")
                explanation = meta.get("explanation")

            submitted = answers_map.get(q.id)
            is_correct = False
            if expected is not None:
                try:
                    # compare as string lowercased
                    is_correct = str(submitted).strip().lower() == str(expected).strip().lower()
                except Exception:
                    is_correct = False

            if is_correct:
                correct += 1

            details.append(
                QuizSubmissionQuestionResultDTO(
                    question_id=q.id,
                    correct=is_correct,
                    correct_answer=str(expected) if expected is not None else None,
                    explanation=explanation if isinstance(explanation, str) else None,
                )
            )

        score = int((correct / total) * 100) if total > 0 else None

        # persist student progress
        lesson_id = quiz.lesson_id
        existing = await progress_repo.get(student.id, lesson_id)
        if existing is None:
            progress = DomainStudentProgress(student_id=student.id, lesson_id=lesson_id, completed=True, score=score, attempts=1)
            await progress_repo.create(progress)
            attempts = 1
        else:
            existing.attempts = (existing.attempts or 0) + 1
            existing.score = score
            existing.completed = True
            updated = await progress_repo.update(existing)
            attempts = updated.attempts

        # store generated test record containing submission and details
        payload = {"submission": answers, "result": {"score": score, "total": total, "correct": correct, "details": [d.model_dump() for d in details]}}
        gen = DomainGeneratedTest(id=None, course_id=None, student_id=student.id, level=None, test_type="quiz_submission", title=f"Quiz {quiz_id} submission", payload=payload)
        await gen_repo.create(gen)

        return QuizSubmissionResultDTO(quiz_id=quiz_id, lesson_id=lesson_id, score=score, total=total, correct=correct, attempts=attempts, details=details)
