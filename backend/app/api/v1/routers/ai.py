from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.application.dtos.ai import DocumentIngestionResultDTO, GeneratedArtifactResultDTO
from app.application.services.audit import AuditLogger
from app.core.config import settings
from app.core.database import get_db
from app.domain.entities.user import User as DomainUser
from app.infrastructure.ai.config import AISettings
from app.infrastructure.ai.types import GenerationRequest as AIWorkerGenerationRequest
from app.infrastructure.ai.workers.worker import Worker
from app.presentation.dependencies import get_current_admin
from app.presentation.schemas.ai import GenerationRequest as GenerationRequestPayload
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai", dependencies=[Depends(get_current_admin)])


def _build_worker(session: AsyncSession, organization_id: int) -> Worker:
    ai_settings = AISettings(
        pdf_dir=Path("app/storage/pdfs"),
        processed_dir=Path("app/storage/processed"),
        cache_dir=Path("app/storage/cache/ai"),
        groq_chat_model=settings.groq_chat_model,
        chunk_size=settings.ai_chunk_size,
        chunk_overlap=settings.ai_chunk_overlap,
        top_k=settings.ai_retrieval_top_k,
        allow_fallback=settings.ai_use_fallback,
    )
    return Worker(
        session=session,
        organization_id=organization_id,
        settings=ai_settings,
        api_key=settings.groq_api_key,
        allow_fallback=settings.ai_use_fallback,
    )


@router.post("/pdfs/upload", response_model=DocumentIngestionResultDTO, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: DomainUser = Depends(get_current_admin),
):
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF filename is required")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported")

    pdf_dir = Path("app/storage/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / filename

    content = await file.read()
    pdf_path.write_bytes(content)

    worker = _build_worker(db, current_user.organization_id)
    chunks = worker.ingest_pdf(pdf_path, source_id=pdf_path.stem)
    audit = AuditLogger(db)
    await audit.log(
        organization_id=current_user.organization_id,
        actor_user_id=current_user.id,
        action="pdf.upload",
        resource_type="pdf",
        resource_id=filename,
        metadata={"chunk_count": len(chunks)},
    )
    await db.commit()
    return DocumentIngestionResultDTO(
        source_document=filename,
        chunk_count=len(chunks),
        vector_ids=list(range(len(chunks))),
    )


@router.post("/generate/{artifact_type}", response_model=GeneratedArtifactResultDTO, status_code=status.HTTP_201_CREATED)
async def generate_artifact(
    artifact_type: str,
    payload: GenerationRequestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: DomainUser = Depends(get_current_admin),
):
    worker = _build_worker(db, current_user.organization_id)
    request = AIWorkerGenerationRequest(**payload.model_dump())

    try:
        if artifact_type == "lesson":
            if payload.chapter_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="chapter_id is required for lesson generation")
            artifact_id = await worker.generate_lesson(
                request=request,
                chapter_id=payload.chapter_id,
            )
        elif artifact_type == "quiz":
            if payload.lesson_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="lesson_id is required for quiz generation")
            artifact_id = await worker.generate_quiz(
                request=request,
                lesson_id=payload.lesson_id,
            )
        elif artifact_type == "placement_test":
            artifact_id = await worker.generate_placement_test(request=request)
        elif artifact_type == "validation_test":
            artifact_id = await worker.generate_validation_test(request=request)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported artifact type")
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    artifact = await worker.generated_artifact_repository.get_by_id(artifact_id, organization_id=current_user.organization_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Generated artifact was not persisted")

    audit = AuditLogger(db)
    await audit.log(
        organization_id=current_user.organization_id,
        actor_user_id=current_user.id,
        action=f"artifact.generate.{artifact_type}",
        resource_type="generated_artifact",
        resource_id=artifact.id,
    )
    await db.commit()

    return GeneratedArtifactResultDTO(
        artifact_type=artifact.artifact_type,
        artifact_id=artifact.id,
        title=artifact.title,
        payload=artifact.payload,
    )
