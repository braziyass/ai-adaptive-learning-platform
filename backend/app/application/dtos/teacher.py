from typing import Optional

from pydantic import BaseModel, ConfigDict


class TeacherDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    user_id: int
