from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)

    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
