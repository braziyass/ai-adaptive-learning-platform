from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.refresh_token import RefreshToken as DomainRefresh
from app.infrastructure.db.models import RefreshToken as RefreshModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError


class RefreshTokenRepositoryImpl(BaseRepository[RefreshModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshModel, session)

    async def create(self, token: DomainRefresh, *, commit: bool = True) -> DomainRefresh:
        orm = RefreshModel(token=token.token, user_id=token.user_id, expires_at=token.expires_at, revoked=token.revoked)
        orm = await super().create(orm, commit=commit)
        return DomainRefresh(id=orm.id, token=orm.token, user_id=orm.user_id, expires_at=orm.expires_at, revoked=orm.revoked)

    async def get_by_token(self, token_str: str) -> Optional[DomainRefresh]:
        stmt = select(RefreshModel).where(RefreshModel.token == token_str)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainRefresh(id=orm.id, token=orm.token, user_id=orm.user_id, expires_at=orm.expires_at, revoked=orm.revoked)

    async def revoke(self, token_str: str) -> None:
        stmt = select(RefreshModel).where(RefreshModel.token == token_str)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return
        orm.revoked = True
        await self.session.commit()

    async def revoke_all_for_user(self, user_id: int) -> None:
        stmt = select(RefreshModel).where(RefreshModel.user_id == user_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        for o in orms:
            o.revoked = True
        await self.session.commit()

    async def list_active_for_user(self, user_id: int) -> Sequence[DomainRefresh]:
        stmt = select(RefreshModel).where(RefreshModel.user_id == user_id, RefreshModel.revoked == False)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [DomainRefresh(id=o.id, token=o.token, user_id=o.user_id, expires_at=o.expires_at, revoked=o.revoked) for o in orms]
