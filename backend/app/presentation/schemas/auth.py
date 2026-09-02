from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str
    password: str

    model_config = ConfigDict()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")
    expires_at: Optional[datetime] = None


class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict()


class LogoutRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict()
