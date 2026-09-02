from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.auth.password import verify_password, hash_password
from app.infrastructure.auth.token_service import TokenService
from app.infrastructure.db.models import User as UserModel
from app.infrastructure.db.repositories import get_refresh_token_repository
from app.domain.entities.refresh_token import RefreshToken as DomainRefresh
from app.domain.entities.user import User as DomainUser


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.token_service = TokenService()
        self.refresh_repo = get_refresh_token_repository(session)

    async def authenticate(self, email: str, password: str):
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        if not verify_password(password, orm.password):
            return None
        return DomainUser(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            password=orm.password,
            role=orm.role.value,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def hash_password(self, password: str) -> str:
        return hash_password(password)

    async def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    async def create_tokens_for_user(self, user_id: int, extra_claims: dict | None = None) -> tuple[str, str]:
        # access token
        access = self.token_service.create_access_token(subject=str(user_id), extra=extra_claims)
        # refresh token (opaque)
        refresh_token = self.token_service.generate_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expires_days)
        refresh = DomainRefresh(id=None, token=refresh_token, user_id=user_id, expires_at=expires_at, revoked=False)
        await self.refresh_repo.create(refresh)
        return access, refresh_token

    async def rotate_refresh_token(self, old_token: str) -> tuple[str, str]:
        existing = await self.refresh_repo.get_by_token(old_token)
        if existing is None or existing.revoked or existing.expires_at < datetime.utcnow():
            raise ValueError("Invalid refresh token")
        # revoke old
        await self.refresh_repo.revoke(old_token)
        # create new
        return await self.create_tokens_for_user(existing.user_id)

    async def revoke_refresh(self, token: str) -> None:
        await self.refresh_repo.revoke(token)
