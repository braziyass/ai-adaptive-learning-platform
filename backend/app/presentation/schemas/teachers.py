from pydantic import BaseModel, ConfigDict


class TeacherCreateRequest(BaseModel):
    user_id: int

    model_config = ConfigDict()


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
