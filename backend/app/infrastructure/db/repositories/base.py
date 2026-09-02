from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.base import Base as OrmBase
from app.infrastructure.db.repositories.errors import IntegrityViolationError, RepositoryError


ModelType = TypeVar("ModelType", bound=OrmBase)


class BaseRepository(Generic[ModelType]):
    """Generic async repository with common CRUD operations.

    This class works directly with ORM models. Concrete repositories may
    accept domain entities and map them to ORM types; mapping lives in
    the concrete implementations to keep this base generic.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, instance: ModelType, *, commit: bool = True) -> ModelType:
        try:
            self.session.add(instance)
            if commit:
                await self.session.commit()
            else:
                await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except IntegrityError as exc:
            await self.session.rollback()
            raise IntegrityViolationError(str(exc)) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(str(exc)) from exc

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        try:
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as exc:
            raise RepositoryError(str(exc)) from exc

    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        try:
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as exc:
            raise RepositoryError(str(exc)) from exc

    async def exists(self, id: Any) -> bool:
        stmt = select(exists().where(self.model.id == id))
        try:
            result = await self.session.execute(stmt)
            return bool(result.scalar_one())
        except SQLAlchemyError as exc:
            raise RepositoryError(str(exc)) from exc

    async def update(self, instance: ModelType, *, commit: bool = True) -> ModelType:
        try:
            merged = await self.session.merge(instance)
            if commit:
                await self.session.commit()
            else:
                await self.session.flush()
            await self.session.refresh(merged)
            return merged
        except IntegrityError as exc:
            await self.session.rollback()
            raise IntegrityViolationError(str(exc)) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(str(exc)) from exc

    async def delete(self, id: Any, *, commit: bool = True) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        try:
            await self.session.execute(stmt)
            if commit:
                await self.session.commit()
            else:
                await self.session.flush()
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(str(exc)) from exc

    async def add(self, instance: ModelType, *, commit: bool = True) -> ModelType:
        try:
            self.session.add(instance)
            if commit:
                await self.session.commit()
            else:
                await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except IntegrityError as exc:
            await self.session.rollback()
            raise IntegrityViolationError(str(exc)) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(str(exc)) from exc

    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        return await self.get_all(offset=offset, limit=limit)
