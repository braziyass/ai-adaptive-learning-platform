from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentAdminCreateDTO(BaseModel):
    model_config = ConfigDict()

    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)
    current_level: int = Field(default=1, ge=1)
    placement_score: int = Field(default=0, ge=0)


class StudentAdminUpdateDTO(BaseModel):
    model_config = ConfigDict()

    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)
    current_level: int = Field(default=1, ge=1)
    placement_score: int = Field(default=0, ge=0)


class StudentAdminReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    current_level: int
    placement_score: int
