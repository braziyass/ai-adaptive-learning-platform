from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.enums import QuestionTypeEnum


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    type = Column(Enum(QuestionTypeEnum), nullable=False)
    # 'metadata' is a reserved attribute on Declarative classes; map DB column 'metadata' to attribute 'meta'
    meta = Column('metadata', JSON, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
