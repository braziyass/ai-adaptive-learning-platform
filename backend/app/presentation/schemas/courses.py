from pydantic import BaseModel, ConfigDict, Field


class CourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=255)

    model_config = ConfigDict()


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    subject: str
