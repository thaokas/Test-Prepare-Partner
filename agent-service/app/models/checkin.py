from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class CheckinRecord(Base):
    __tablename__ = "checkin_records"
    __table_args__ = (Index('idx_user_plan_date', 'user_id', 'plan_id', 'checkin_date'),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("study_plans.id"), nullable=False)
    checkin_date = Column(Date, nullable=False)
    checkin_time = Column(DateTime, server_default=func.now())
    content = Column(String, nullable=False)
    checkin_type = Column(Integer, default=1)    # 1-文字 2-图片
    completed_task_ids = Column(JSON, default=list)
    total_tasks = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    streak_days = Column(Integer, default=0)
    easter_egg = Column(String, nullable=True)
    encouragement = Column(String, nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now())
