from __future__ import annotations

from datetime import datetime, timedelta
import secrets

from jose import jwt

from app.core.config import settings


class TokenService:
    def __init__(self, secret_key: str = settings.jwt_secret_key, algorithm: str = settings.jwt_algorithm):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, subject: str, expires_delta: timedelta | None = None, extra: dict | None = None) -> str:
        now = datetime.utcnow()
        expire = now + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
        payload = {"sub": str(subject), "exp": expire, "iat": now}
        if extra:
            payload.update(extra)
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def generate_refresh_token(self) -> str:
        # return a secure opaque token (not JWT)
        return secrets.token_urlsafe(64)
