from typing import Optional

from pydantic import BaseModel, ConfigDict


class StudentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    user_id: int
    current_level: int
    placement_score: int
