from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class ReminderSetting(Base):
    __tablename__ = "reminder_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    mode = Column(Integer, default=1)               # 0-静默 1-温柔 2-强化 3-唐僧
    custom_times = Column(JSON, default=list)       # ["21:00", "22:00"]
    monking_interval = Column(Integer, default=30)  # 唐僧模式间隔(分钟)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def mode_name(self) -> str:
        names = {0: "静默模式", 1: "温柔模式", 2: "强化模式", 3: "唐僧模式"}
        return names.get(self.mode, "未知模式")
