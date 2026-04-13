"""
Pydantic schemas for API request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import IntEnum


# Enums
class SupervisionMode(IntEnum):
    SILENT = 0
    GENTLE = 1
    INTENSIVE = 2
    MONKING = 3


class Phase(IntEnum):
    FOUNDATION = 1
    REINFORCEMENT = 2
    SPRINT = 3


class TaskType(IntEnum):
    LEARN = 1
    REVIEW = 2
    PRACTICE = 3
    MOCK_EXAM = 4


class TaskStatus(IntEnum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    SKIPPED = 3


# Request schemas
class ChatRequest(BaseModel):
    """对话请求"""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class PlanGenerateRequest(BaseModel):
    """计划生成请求"""
    user_id: str
    exam_name: str = Field(..., description="考试名称，如：考研数学")
    exam_type: str = Field(..., description="考试类型：考研/期末/考证/考公/语言/期中")
    exam_date: date = Field(..., description="考试日期")
    daily_hours: float = Field(..., gt=0, le=24, description="每日可用时长（小时）")
    foundation_level: int = Field(1, ge=0, le=2, description="基础水平：0-零基础 1-有一定基础 2-已复习一轮")
    weak_subjects: Optional[List[str]] = Field(default=None, description="薄弱科目列表")


class CheckinRequest(BaseModel):
    """打卡请求"""
    user_id: str
    content: str = Field(..., description="打卡内容")
    checkin_type: int = Field(1, ge=1, le=2, description="打卡方式：1-文字 2-图片")


# Response schemas
class ChatResponse(BaseModel):
    """对话响应"""
    response: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TaskSchema(BaseModel):
    """任务数据"""
    task_id: str
    task_date: date
    subject: str
    task_content: str
    estimated_minutes: int
    task_type: int
    phase: int
    status: int

    class Config:
        from_attributes = True


class PlanGenerateResponse(BaseModel):
    """计划生成响应"""
    plan_id: Optional[str]
    total_tasks: int
    message: str
    tasks: List[Dict[str, Any]] = []


class CheckinResponse(BaseModel):
    """打卡响应"""
    checkin_id: Optional[str] = None
    completion_rate: float
    matched_tasks: List[Dict[str, Any]] = []
    encouragement: str
    easter_egg: Optional[str] = None
    streak_days: int


class TodayTasksResponse(BaseModel):
    """今日任务响应"""
    tasks: List[TaskSchema]
    completed_count: int
    total_count: int
    completion_rate: float


class ReminderSettingsRequest(BaseModel):
    """提醒设置请求"""
    mode: int = Field(1, ge=0, le=3, description="提醒模式：0-静默 1-温柔 2-强化 3-唐僧")
    custom_times: List[str] = []
    monking_interval: int = Field(30, ge=5, le=120)


class ReminderSettingsResponse(BaseModel):
    """提醒设置响应"""
    mode: int
    custom_times: List[str]
    monking_interval: int
    is_active: bool


class WeeklyReportResponse(BaseModel):
    """周报响应"""
    report_id: Optional[str] = None
    user_id: str
    week_start: str
    week_end: str
    average_rate: float
    summary: str
    suggestions: List[str] = []