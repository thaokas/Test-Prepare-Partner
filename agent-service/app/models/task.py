"""
任务模型
"""
from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, SmallInteger, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"

    task_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(64), ForeignKey("study_plans.plan_id"), nullable=False)
    task_date = Column(Date, nullable=False)
    subject = Column(String(50), nullable=False)
    task_content = Column(String(500), nullable=False)
    estimated_minutes = Column(Integer, nullable=False)
    task_type = Column(SmallInteger, default=1)  # 1-学习 2-复习 3-刷题 4-模考
    phase = Column(SmallInteger, nullable=False)  # 1-基础 2-强化 3-冲刺
    status = Column(SmallInteger, default=0)  # 0-未开始 1-进行中 2-已完成 3-已跳过
    completed_at = Column(TIMESTAMP, nullable=True)
    checkin_type = Column(SmallInteger, nullable=True)  # 1-文字 2-图片

    # 关系
    plan = relationship("StudyPlan", backref="tasks")

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, subject={self.subject}, status={self.status})>"