from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    placement_score = Column(Integer, default=0, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    placement_completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="student")
    progress = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")
