from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.entities.enums import Role


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
