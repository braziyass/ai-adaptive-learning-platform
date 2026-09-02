from pydantic import BaseModel, ConfigDict, Field


class LessonCreateRequest(BaseModel):
    chapter_id: int
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

    model_config = ConfigDict()


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    title: str
    content: str
