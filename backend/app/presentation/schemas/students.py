from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StudentCreateRequest(BaseModel):
    user_id: int
    current_level: Optional[int] = Field(default=1, ge=1)
    placement_score: Optional[int] = Field(default=0, ge=0)

    model_config = ConfigDict()


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    current_level: int
    placement_score: int
