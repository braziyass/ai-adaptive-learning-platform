from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.audit_log import AuditLog as DomainAuditLog
from app.infrastructure.db.models import AuditLog as AuditLogModel


class AuditLogger:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(
        self,
        *,
        organization_id: int,
        actor_user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        model = AuditLogModel(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            log_metadata=metadata or {},
        )
        self.session.add(model)
        await self.session.flush()

    async def list_for_organization(
        self, organization_id: int, offset: int = 0, limit: int = 100
    ) -> list[DomainAuditLog]:
        from sqlalchemy import select

        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.organization_id == organization_id)
            .order_by(AuditLogModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [
            DomainAuditLog(
                id=row.id,
                organization_id=row.organization_id,
                actor_user_id=row.actor_user_id,
                action=row.action,
                resource_type=row.resource_type,
                resource_id=row.resource_id,
                metadata=row.log_metadata or {},
                created_at=row.created_at,
            )
            for row in rows
        ]
