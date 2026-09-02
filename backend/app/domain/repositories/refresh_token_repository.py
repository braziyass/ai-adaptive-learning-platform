from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Sequence

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshToken:
        raise NotImplementedError

    @abstractmethod
    async def get_by_token(self, token_str: str) -> Optional[RefreshToken]:
        raise NotImplementedError

    @abstractmethod
    async def revoke(self, token_str: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_for_user(self, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_active_for_user(self, user_id: int) -> Sequence[RefreshToken]:
        raise NotImplementedError
