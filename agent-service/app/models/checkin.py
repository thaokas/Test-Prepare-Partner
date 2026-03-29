"""
打卡记录模型
"""
from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, DECIMAL, SmallInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid


class Checkin(Base):
    """打卡记录表"""
    __tablename__ = "checkins"

    checkin_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(String(64), ForeignKey("study_plans.plan_id"), nullable=False)
    checkin_date = Column(Date, nullable=False)
    completed_tasks = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completion_rate = Column(DECIMAL(5, 2), default=0)
    is_makeup = Column(SmallInteger, default=0)  # 0-否 1-是
    streak_broken = Column(SmallInteger, default=0)  # 0-否 1-是
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关系
    user = relationship("User", backref="checkins")
    plan = relationship("StudyPlan", backref="checkins")

    def __repr__(self):
        return f"<Checkin(checkin_id={self.checkin_id}, date={self.checkin_date}, rate={self.completion_rate})>"