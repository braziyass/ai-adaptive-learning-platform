from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.student_module import (
    AvailableQuizDTO,
    AvailableQuizQuestionDTO,
    CompletedQuizDTO,
    PlacementTestDTO,
    PlacementTestQuestionDTO,
    PlacementTestSubmissionResultDTO,
    StudentCurrentLevelDTO,
    StudentProfileDTO,
    StudentProgressItemDTO,
    UnlockedLessonDTO,
    ValidationTestResultDTO,
    ValidationTestSubmissionResultDTO,
)
from app.application.services.audit import AuditLogger
from app.application.services.leveling import LevelingService
from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.models import Chapter as ChapterModel
from app.infrastructure.db.models import Course as CourseModel
from app.infrastructure.db.models import Question as QuestionModel
from app.infrastructure.db.models import Lesson as LessonModel
from app.infrastructure.db.models import Quiz as QuizModel
from app.infrastructure.db.models import StudentProgress as ProgressModel
from app.infrastructure.db.repositories import StudentRepositoryImpl, UserRepositoryImpl
from app.infrastructure.db.repositories import (
    QuestionRepositoryImpl,
    StudentProgressRepositoryImpl,
    GeneratedTestRepositoryImpl,
    QuizRepositoryImpl,
    PlacementTestRepositoryImpl,
)
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
    def __init__(self, session: AsyncSession, organization_id: int) -> None:
        self.session = session
        self.organization_id = organization_id
        self.user_repo = UserRepositoryImpl(session)
        self.student_repo = StudentRepositoryImpl(session)
        self.placement_test_repo = PlacementTestRepositoryImpl(session)
        self.audit = AuditLogger(session)

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
            points=student.points,
            placement_completed_at=student.placement_completed_at,
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
            .join(CourseModel, CourseModel.id == ChapterModel.course_id)
            .outerjoin(
                ProgressModel,
                and_(ProgressModel.lesson_id == LessonModel.id, ProgressModel.student_id == student.id),
            )
            .outerjoin(QuizModel, QuizModel.lesson_id == LessonModel.id)
            .where(ChapterModel.order <= student.current_level, CourseModel.organization_id == self.organization_id)
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

    async def _available_quizzes(self, student, *, level_filter) -> list[AvailableQuizDTO]:
        stmt = (
            select(LessonModel, ChapterModel, QuizModel, QuestionModel)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .join(CourseModel, CourseModel.id == ChapterModel.course_id)
            .join(QuizModel, QuizModel.lesson_id == LessonModel.id)
            .outerjoin(QuestionModel, QuestionModel.quiz_id == QuizModel.id)
            .where(level_filter, CourseModel.organization_id == self.organization_id)
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

    async def get_available_quizzes(self, current_user: DomainUser) -> Sequence[AvailableQuizDTO]:
        student, _ = await self._load_student_and_user(current_user)
        return await self._available_quizzes(student, level_filter=ChapterModel.order <= student.current_level)

    async def get_available_validation_tests(self, current_user: DomainUser) -> Sequence[AvailableQuizDTO]:
        student, _ = await self._load_student_and_user(current_user)
        return await self._available_quizzes(student, level_filter=ChapterModel.order == student.current_level)

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
                passed=LevelingService.is_validation_pass(progress.score),
                attempts=progress.attempts,
            )
            for quiz, lesson, chapter, progress in rows
        ]

    async def _grade_quiz_answers(self, quiz_id: int, answers: list[dict]):
        question_repo = QuestionRepositoryImpl(self.session)
        questions = await question_repo.list_by_quiz(quiz_id)
        total = len(questions)
        correct = 0
        details: list[QuizSubmissionQuestionResultDTO] = []

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
        return score, total, correct, details

    async def _quiz_in_organization(self, quiz_id: int, level_filter=None) -> bool:
        stmt = (
            select(QuizModel.id)
            .join(LessonModel, LessonModel.id == QuizModel.lesson_id)
            .join(ChapterModel, ChapterModel.id == LessonModel.chapter_id)
            .join(CourseModel, CourseModel.id == ChapterModel.course_id)
            .where(QuizModel.id == quiz_id, CourseModel.organization_id == self.organization_id)
        )
        if level_filter is not None:
            stmt = stmt.where(level_filter)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def submit_quiz(self, current_user: DomainUser, quiz_id: int, answers: list[dict]) -> QuizSubmissionResultDTO:
        student, _ = await self._load_student_and_user(current_user)

        progress_repo = StudentProgressRepositoryImpl(self.session)
        gen_repo = GeneratedTestRepositoryImpl(self.session)
        quiz_repo = QuizRepositoryImpl(self.session)

        quiz = await quiz_repo.get_by_id(quiz_id)
        if quiz is None or not await self._quiz_in_organization(quiz_id):
            raise StudentNotFoundError("Quiz not found")

        score, total, correct, details = await self._grade_quiz_answers(quiz_id, answers)

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

        points_awarded = LevelingService.points_for_quiz(correct, total)
        student.points += points_awarded
        await self.student_repo.update(student)

        payload = {"submission": answers, "result": {"score": score, "total": total, "correct": correct, "details": [d.model_dump() for d in details]}}
        gen = DomainGeneratedTest(id=None, course_id=None, student_id=student.id, level=None, test_type="quiz_submission", title=f"Quiz {quiz_id} submission", payload=payload)
        await gen_repo.create(gen)

        await self.audit.log(
            organization_id=self.organization_id,
            actor_user_id=current_user.id,
            action="quiz.submit",
            resource_type="quiz",
            resource_id=quiz_id,
            metadata={"score": score, "points_awarded": points_awarded},
        )
        await self.session.commit()

        return QuizSubmissionResultDTO(
            quiz_id=quiz_id, lesson_id=lesson_id, score=score, total=total, correct=correct, attempts=attempts,
            points_awarded=points_awarded, details=details,
        )

    async def submit_validation_test(self, current_user: DomainUser, quiz_id: int, answers: list[dict]) -> ValidationTestSubmissionResultDTO:
        student, _ = await self._load_student_and_user(current_user)

        progress_repo = StudentProgressRepositoryImpl(self.session)
        gen_repo = GeneratedTestRepositoryImpl(self.session)
        quiz_repo = QuizRepositoryImpl(self.session)

        quiz = await quiz_repo.get_by_id(quiz_id)
        if quiz is None or not await self._quiz_in_organization(quiz_id, level_filter=ChapterModel.order == student.current_level):
            raise StudentNotFoundError("Validation test not found for your current level")

        score, total, correct, details = await self._grade_quiz_answers(quiz_id, answers)

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

        passed = LevelingService.is_validation_pass(score)
        points_awarded = LevelingService.points_for_quiz(correct, total)
        leveled_up = False
        previous_level = student.current_level
        if passed:
            points_awarded += LevelingService.validation_pass_bonus_points()
            new_level = LevelingService.next_level(student.current_level)
            leveled_up = new_level != previous_level
            student.current_level = new_level
        student.points += points_awarded
        await self.student_repo.update(student)

        payload = {"submission": answers, "result": {"score": score, "total": total, "correct": correct, "details": [d.model_dump() for d in details]}}
        gen = DomainGeneratedTest(id=None, course_id=None, student_id=student.id, level=previous_level, test_type="validation_test_submission", title=f"Validation test {quiz_id} submission", payload=payload)
        await gen_repo.create(gen)

        await self.audit.log(
            organization_id=self.organization_id,
            actor_user_id=current_user.id,
            action="validation_test.submit",
            resource_type="quiz",
            resource_id=quiz_id,
            metadata={"score": score, "passed": passed, "leveled_up": leveled_up, "new_level": student.current_level},
        )
        await self.session.commit()

        return ValidationTestSubmissionResultDTO(
            quiz_id=quiz_id, lesson_id=lesson_id, score=score, total=total, correct=correct, attempts=attempts,
            points_awarded=points_awarded, passed=passed, leveled_up=leveled_up, new_level=student.current_level,
            details=details,
        )

    async def get_placement_test(self, current_user: DomainUser) -> PlacementTestDTO:
        await self._load_student_and_user(current_user)
        test = await self.placement_test_repo.get_active_for_organization(self.organization_id)
        if test is None:
            raise StudentNotFoundError("No placement test is available yet")
        return PlacementTestDTO(
            placement_test_id=test.id,
            title=test.title,
            subject=test.subject,
            questions=[
                PlacementTestQuestionDTO(
                    question_id=q.id,
                    question=q.question,
                    question_type=q.type,
                    options=list(q.metadata.get("options", [])) if isinstance(q.metadata, dict) else [],
                )
                for q in test.questions
            ],
        )

    async def submit_placement_test(self, current_user: DomainUser, answers: list[dict]) -> PlacementTestSubmissionResultDTO:
        student, _ = await self._load_student_and_user(current_user)

        test = await self.placement_test_repo.get_active_for_organization(self.organization_id)
        if test is None:
            raise StudentNotFoundError("No placement test is available yet")

        answers_map = {a.get("question_id"): a.get("answer") for a in answers}
        total = len(test.questions)
        correct = 0
        details: list[QuizSubmissionQuestionResultDTO] = []

        for q in test.questions:
            meta = q.metadata or {}
            expected = meta.get("answer") if isinstance(meta, dict) else None
            explanation = meta.get("explanation") if isinstance(meta, dict) else None
            submitted = answers_map.get(q.id)
            is_correct = False
            if expected is not None:
                try:
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

        score = int((correct / total) * 100) if total > 0 else 0
        assigned_level = LevelingService.assign_level_from_score(score)

        student.placement_score = score
        student.current_level = assigned_level
        student.placement_completed_at = datetime.now(timezone.utc)
        await self.student_repo.update(student)

        await self.audit.log(
            organization_id=self.organization_id,
            actor_user_id=current_user.id,
            action="placement_test.submit",
            resource_type="placement_test",
            resource_id=test.id,
            metadata={"score": score, "assigned_level": assigned_level},
        )
        await self.session.commit()

        return PlacementTestSubmissionResultDTO(score=score, total=total, correct=correct, assigned_level=assigned_level, details=details)
