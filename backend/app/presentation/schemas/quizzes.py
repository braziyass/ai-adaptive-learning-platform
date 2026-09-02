from pydantic import BaseModel, ConfigDict


class QuizCreateRequest(BaseModel):
    lesson_id: int

    model_config = ConfigDict()


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_id: int
