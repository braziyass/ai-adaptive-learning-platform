from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generated_test import AIGeneratedTest as DomainGeneratedTest
from app.infrastructure.db.models import AIGeneratedTest as AIGeneratedTestModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class GeneratedTestRepositoryImpl(BaseRepository[AIGeneratedTestModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AIGeneratedTestModel, session)

    async def create(self, generated_test: DomainGeneratedTest) -> DomainGeneratedTest:
        orm = AIGeneratedTestModel(
            course_id=generated_test.course_id,
            student_id=generated_test.student_id,
            level=generated_test.level,
            test_type=generated_test.test_type,
            title=generated_test.title,
            payload=generated_test.payload,
        )
        orm = await self.add(orm)
        return DomainGeneratedTest(
            id=orm.id,
            course_id=orm.course_id,
            student_id=orm.student_id,
            level=orm.level,
            test_type=orm.test_type,
            title=orm.title,
            payload=dict(orm.payload or {}),
        )

    async def get_by_id(self, id: int) -> Optional[DomainGeneratedTest]:
        stmt = select(AIGeneratedTestModel).where(AIGeneratedTestModel.id == id)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainGeneratedTest(
            id=orm.id,
            course_id=orm.course_id,
            student_id=orm.student_id,
            level=orm.level,
            test_type=orm.test_type,
            title=orm.title,
            payload=dict(orm.payload or {}),
        )

    async def list_by_type(self, test_type: str, offset: int = 0, limit: int = 100) -> Sequence[DomainGeneratedTest]:
        stmt = (
            select(AIGeneratedTestModel)
            .where(AIGeneratedTestModel.test_type == test_type)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [
            DomainGeneratedTest(
                id=orm.id,
                course_id=orm.course_id,
                student_id=orm.student_id,
                level=orm.level,
                test_type=orm.test_type,
                title=orm.title,
                payload=dict(orm.payload or {}),
            )
            for orm in rows
        ]

    async def update(self, generated_test: DomainGeneratedTest) -> DomainGeneratedTest:
        orm = await self.session.get(AIGeneratedTestModel, generated_test.id)
        if orm is None:
            raise NotFoundError("Generated test not found")
        orm.course_id = generated_test.course_id
        orm.student_id = generated_test.student_id
        orm.level = generated_test.level
        orm.test_type = generated_test.test_type
        orm.title = generated_test.title
        orm.payload = generated_test.payload
        updated = await super().update(orm)
        return DomainGeneratedTest(
            id=updated.id,
            course_id=updated.course_id,
            student_id=updated.student_id,
            level=updated.level,
            test_type=updated.test_type,
            title=updated.title,
            payload=dict(updated.payload or {}),
        )

    async def delete(self, id: int) -> None:
        await super().delete(id)