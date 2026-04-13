from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False, unique=True)
    nickname = Column(String, nullable=True)
    foundation_level = Column(Integer, default=0)
    target_exam = Column(String, nullable=True)
    weak_subjects = Column(JSON, default=list)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    total_checkins = Column(Integer, default=0)
    reminder_mode = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
