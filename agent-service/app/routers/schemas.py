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
    plan_id: str
    total_tasks: int
    phases: List[Dict[str, Any]]
    message: str


class CheckinResponse(BaseModel):
    """打卡响应"""
    completed_tasks: int
    total_tasks: int
    completion_rate: float
    streak: int
    encouragement: str
    easter_egg: Optional[str] = None


class TodayTasksResponse(BaseModel):
    """今日任务响应"""
    tasks: List[TaskSchema]
    completed_count: int
    total_count: int
    completion_rate: float


class WeeklyReportResponse(BaseModel):
    """周报响应"""
    user_id: str
    week_start: date
    week_end: date
    daily_rates: List[Dict[str, Any]]
    average_rate: float
    week_over_week: float
    current_streak: int
    best_study_time: Optional[str] = None
    summary: str