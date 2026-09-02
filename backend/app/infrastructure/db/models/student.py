from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    placement_score = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="student")
    progress = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")
