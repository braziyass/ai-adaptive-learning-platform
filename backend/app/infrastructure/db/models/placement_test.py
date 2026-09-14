from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.enums import QuestionTypeEnum


class PlacementTest(Base):
    __tablename__ = "placement_tests"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    questions = relationship("PlacementTestQuestion", back_populates="placement_test", cascade="all, delete-orphan")


class PlacementTestQuestion(Base):
    __tablename__ = "placement_test_questions"

    id = Column(Integer, primary_key=True)
    placement_test_id = Column(Integer, ForeignKey("placement_tests.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    type = Column(Enum(QuestionTypeEnum), nullable=False)
    meta = Column("metadata", JSON, nullable=True)

    placement_test = relationship("PlacementTest", back_populates="questions")
