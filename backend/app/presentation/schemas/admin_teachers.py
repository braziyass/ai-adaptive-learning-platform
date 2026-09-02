from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TeacherCreateRequest(BaseModel):
    model_config = ConfigDict()

    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)


class TeacherUpdateRequest(BaseModel):
    model_config = ConfigDict()

    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
