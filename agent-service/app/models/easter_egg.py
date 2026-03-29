"""
彩蛋触发记录模型
"""
from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, SmallInteger, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid


class EasterEgg(Base):
    """彩蛋触发记录表"""
    __tablename__ = "easter_eggs"

    record_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    egg_type = Column(String(50), nullable=False)  # late_night/weekend/early_bird/random
    trigger_date = Column(Date, nullable=False)
    content = Column(String(500), nullable=True)
    is_triggered = Column(SmallInteger, default=0)  # 0-否 1-是

    # 关系
    user = relationship("User", backref="easter_eggs")

    def __repr__(self):
        return f"<EasterEgg(record_id={self.record_id}, type={self.egg_type})>"