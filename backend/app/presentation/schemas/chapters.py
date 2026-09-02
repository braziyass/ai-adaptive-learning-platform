from pydantic import BaseModel, ConfigDict, Field


class ChapterCreateRequest(BaseModel):
    course_id: int
    title: str = Field(..., min_length=1, max_length=255)
    order: int = Field(..., ge=0)

    model_config = ConfigDict()


class ChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    order: int
