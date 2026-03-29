"""
备考计划模型
"""
from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, DECIMAL, SmallInteger, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid


class StudyPlan(Base):
    """备考计划表"""
    __tablename__ = "study_plans"

    plan_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    exam_name = Column(String(100), nullable=False)
    exam_type = Column(String(64), nullable=False)  # 考研、期末、考证、考公、语言、期中
    current_mode = Column(SmallInteger, default=1)  # 0-静默 1-温柔 2-强化 3-唐僧
    exam_date = Column(Date, nullable=False)
    daily_hours = Column(DECIMAL(3, 1), nullable=False)
    foundation_level = Column(SmallInteger, default=1)  # 0-零基础 1-有一定基础 2-已复习一轮
    weak_subjects = Column(String(200), nullable=True)  # JSON数组
    plan_status = Column(SmallInteger, default=0)  # 0-进行中 1-已完成 2-已暂停
    created_at = Column(TIMESTAMP, server_default=func.now())
    current_phase = Column(SmallInteger, default=1)  # 1-基础 2-强化 3-冲刺

    # 关系
    user = relationship("User", backref="plans")

    def __repr__(self):
        return f"<StudyPlan(plan_id={self.plan_id}, exam_name={self.exam_name})>"