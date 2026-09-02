from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class StudentProgress(Base):
    __tablename__ = "student_progress"

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    completed = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)

    student = relationship("Student", back_populates="progress")
    lesson = relationship("Lesson")
