from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.placement_test import PlacementTest as DomainPlacementTest
from app.domain.entities.placement_test import PlacementTestQuestion as DomainPlacementTestQuestion
from app.infrastructure.db.models import PlacementTest as PlacementTestModel
from app.infrastructure.db.models import PlacementTestQuestion as PlacementTestQuestionModel
from app.infrastructure.db.models.enums import QuestionTypeEnum


def _question_to_domain(orm: PlacementTestQuestionModel) -> DomainPlacementTestQuestion:
    return DomainPlacementTestQuestion(
        id=orm.id,
        placement_test_id=orm.placement_test_id,
        question=orm.question,
        type=orm.type.value,
        metadata=orm.meta or {},
    )


def _test_to_domain(orm: PlacementTestModel) -> DomainPlacementTest:
    return DomainPlacementTest(
        id=orm.id,
        organization_id=orm.organization_id,
        subject=orm.subject,
        title=orm.title,
        is_active=orm.is_active,
        created_at=orm.created_at,
        questions=[_question_to_domain(q) for q in sorted(orm.questions, key=lambda q: q.id or 0)],
    )


class PlacementTestRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_for_organization(self, organization_id: int) -> Optional[DomainPlacementTest]:
        stmt = (
            select(PlacementTestModel)
            .where(PlacementTestModel.organization_id == organization_id, PlacementTestModel.is_active.is_(True))
            .options(selectinload(PlacementTestModel.questions))
            .order_by(PlacementTestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        return _test_to_domain(orm) if orm is not None else None

    async def get_by_id(self, placement_test_id: int, organization_id: int) -> Optional[DomainPlacementTest]:
        stmt = (
            select(PlacementTestModel)
            .where(PlacementTestModel.id == placement_test_id, PlacementTestModel.organization_id == organization_id)
            .options(selectinload(PlacementTestModel.questions))
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        return _test_to_domain(orm) if orm is not None else None

    async def deactivate_active(self, organization_id: int) -> None:
        stmt = (
            update(PlacementTestModel)
            .where(PlacementTestModel.organization_id == organization_id, PlacementTestModel.is_active.is_(True))
            .values(is_active=False)
        )
        await self.session.execute(stmt)

    async def create_with_questions(
        self,
        organization_id: int,
        subject: str,
        title: str,
        questions: Sequence[dict],
    ) -> DomainPlacementTest:
        orm = PlacementTestModel(organization_id=organization_id, subject=subject, title=title, is_active=True)
        for item in questions:
            qtype = str(item.get("type") or "multiple_choice")
            try:
                qtype_enum = QuestionTypeEnum(qtype)
            except ValueError:
                qtype_enum = QuestionTypeEnum.multiple_choice
            orm.questions.append(
                PlacementTestQuestionModel(
                    question=str(item.get("question", "")).strip(),
                    type=qtype_enum,
                    meta={
                        "options": item.get("options", []),
                        "answer": item.get("answer"),
                        "explanation": item.get("explanation"),
                    },
                )
            )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm, attribute_names=["questions"])
        return _test_to_domain(orm)
