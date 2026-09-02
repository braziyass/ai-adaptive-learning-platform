from typing import Optional

from pydantic import BaseModel, ConfigDict


class CourseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    title: str
    subject: str
