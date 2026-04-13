from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    __table_args__ = (Index('idx_user_week', 'user_id', 'week_start'),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("study_plans.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    average_rate = Column(Float, default=0.0)
    week_over_week = Column(Float, default=0.0)
    streak_days = Column(Integer, default=0)
    best_study_time = Column(String, nullable=True)
    summary = Column(String, nullable=False, default="")
    suggestions = Column(String, nullable=False, default="[]")  # JSON string
    daily_rates = Column(String, nullable=False, default="[]")  # JSON string
    created_at = Column(DateTime, server_default=func.now())
