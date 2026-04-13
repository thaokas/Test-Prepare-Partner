from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index('idx_user_date', 'user_id', 'task_date'),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("study_plans.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    task_date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    task_content = Column(String, nullable=False)
    estimated_minutes = Column(Integer, default=60)
    task_type = Column(Integer, default=1)   # 1-学习 2-复习 3-测试 4-其他
    phase = Column(Integer, default=1)
    status = Column(Integer, default=0)      # 0-待完成 1-进行中 2-已完成
    actual_minutes = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    keywords = Column(JSON, default=list)    # 用于打卡匹配
    created_at = Column(DateTime, server_default=func.now())
