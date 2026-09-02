from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    user = relationship("User", back_populates="teacher")
