from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChapterDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    course_id: int
    title: str
    order: int
