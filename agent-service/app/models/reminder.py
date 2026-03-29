"""
提醒记录模型
"""
from sqlalchemy import Column, String, Integer, TIMESTAMP, SmallInteger, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid


class Reminder(Base):
    """提醒记录表"""
    __tablename__ = "reminders"

    reminder_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    plan_id = Column(String(64), ForeignKey("study_plans.plan_id"), nullable=False)
    reminder_type = Column(SmallInteger, nullable=False)  # 1-每日提醒 2-催更提醒 3-周报提醒
    trigger_time = Column(TIMESTAMP, nullable=False)
    content = Column(String(1000), nullable=True)
    is_sent = Column(SmallInteger, default=0)  # 0-否 1-是
    sent_at = Column(TIMESTAMP, nullable=True)

    # 关系
    user = relationship("User", backref="reminders")
    plan = relationship("StudyPlan", backref="reminders")

    def __repr__(self):
        return f"<Reminder(reminder_id={self.reminder_id}, type={self.reminder_type})>"