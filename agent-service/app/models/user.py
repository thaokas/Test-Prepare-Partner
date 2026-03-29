"""
用户模型
"""
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app.models.database import Base
import uuid


class User(Base):
    """用户表"""
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    nickname = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    total_checkins = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, nickname={self.nickname})>"