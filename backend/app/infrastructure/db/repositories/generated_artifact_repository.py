from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generated_artifact import GeneratedArtifact
from app.domain.repositories.generated_artifact_repository import GeneratedArtifactRepository
from app.infrastructure.db.models.generated_artifact import GeneratedArtifactModel


class SQLAlchemyGeneratedArtifactRepository(GeneratedArtifactRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, artifact: GeneratedArtifact) -> GeneratedArtifact:
        model = GeneratedArtifactModel(
            artifact_type=artifact.artifact_type,
            title=artifact.title,
            subject=artifact.subject,
            level=artifact.level,
            course_id=artifact.course_id,
            chapter_id=artifact.chapter_id,
            lesson_id=artifact.lesson_id,
            student_id=artifact.student_id,
            payload=artifact.payload,
            source_chunks=artifact.source_chunks,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return GeneratedArtifact(
            id=model.id,
            artifact_type=model.artifact_type,
            title=model.title,
            subject=model.subject,
            level=model.level,
            payload=model.payload,
            source_chunks=model.source_chunks,
            course_id=model.course_id,
            chapter_id=model.chapter_id,
            lesson_id=model.lesson_id,
            student_id=model.student_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, artifact_id: int) -> GeneratedArtifact | None:
        model = await self.session.get(GeneratedArtifactModel, artifact_id)
        if model is None:
            return None
        return GeneratedArtifact(
            id=model.id,
            artifact_type=model.artifact_type,
            title=model.title,
            subject=model.subject,
            level=model.level,
            payload=model.payload,
            source_chunks=model.source_chunks,
            course_id=model.course_id,
            chapter_id=model.chapter_id,
            lesson_id=model.lesson_id,
            student_id=model.student_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
