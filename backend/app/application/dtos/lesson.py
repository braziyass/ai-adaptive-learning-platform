from typing import Optional

from pydantic import BaseModel, ConfigDict


class LessonDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    chapter_id: int
    title: str
    content: str
