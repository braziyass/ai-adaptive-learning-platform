from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.models import User as UserModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.repositories.errors import NotFoundError, RepositoryError


class UserRepositoryImpl(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserModel, session)

    async def create(self, user: DomainUser, *, commit: bool = True) -> DomainUser:
        orm = UserModel(
            organization_id=user.organization_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            role=user.role.value if hasattr(user.role, "value") else user.role,
        )
        try:
            orm = await super().create(orm, commit=commit)
            return DomainUser(
                id=orm.id,
                first_name=orm.first_name,
                last_name=orm.last_name,
                email=orm.email,
                password=orm.password,
                role=orm.role.value,
                organization_id=orm.organization_id,
                created_at=orm.created_at,
                updated_at=orm.updated_at,
            )
        except RepositoryError:
            raise

    async def get_by_id(self, id: int) -> Optional[DomainUser]:
        stmt = select(UserModel).where(UserModel.id == id).options(
            selectinload(UserModel.student), selectinload(UserModel.teacher)
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainUser(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            password=orm.password,
            role=orm.role.value,
            organization_id=orm.organization_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def get_by_email(self, email: str) -> Optional[DomainUser]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        if orm is None:
            return None
        return DomainUser(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            password=orm.password,
            role=orm.role.value,
            organization_id=orm.organization_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def list(self, offset: int = 0, limit: int = 100, organization_id: int | None = None) -> Sequence[DomainUser]:
        stmt = select(UserModel).offset(offset).limit(limit)
        if organization_id is not None:
            stmt = stmt.where(UserModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [
            DomainUser(
                id=o.id,
                first_name=o.first_name,
                last_name=o.last_name,
                email=o.email,
                password=o.password,
                role=o.role.value,
                organization_id=o.organization_id,
                created_at=o.created_at,
                updated_at=o.updated_at,
            )
            for o in orms
        ]

    async def update(self, user: DomainUser, *, commit: bool = True) -> DomainUser:
        orm = await self.session.get(UserModel, user.id)
        if orm is None:
            raise NotFoundError("User not found")
        orm.first_name = user.first_name
        orm.last_name = user.last_name
        orm.email = user.email
        orm.password = user.password
        orm.role = user.role.value if hasattr(user.role, "value") else user.role
        try:
            updated = await super().update(orm, commit=commit)
            return DomainUser(
                id=updated.id,
                first_name=updated.first_name,
                last_name=updated.last_name,
                email=updated.email,
                password=updated.password,
                role=updated.role.value,
                organization_id=updated.organization_id,
                created_at=updated.created_at,
                updated_at=updated.updated_at,
            )
        except RepositoryError:
            raise

    async def delete(self, id: int, *, commit: bool = True) -> None:
        await super().delete(id, commit=commit)
