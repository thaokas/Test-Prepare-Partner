from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    exam_name = Column(String, nullable=False)
    exam_type = Column(String, nullable=False)
    exam_date = Column(Date, nullable=False)
    daily_hours = Column(Float, default=2.0)
    status = Column(Integer, default=0)
    current_phase = Column(Integer, default=1)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    @property
    def phase_name(self) -> str:
        names = {1: "基础阶段", 2: "强化阶段", 3: "冲刺阶段"}
        return names.get(self.current_phase, "未知阶段")
