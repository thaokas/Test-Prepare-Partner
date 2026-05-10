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
    completed_content: str = Field(..., description="今日完成的计划内容描述")
    overall_completion_rate: float = Field(..., ge=0, le=100, description="整体备考完成率（0-100）")
    image_url: Optional[str] = Field(default=None, description="打卡图片URL（可选）")


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
    encouragement: str


class ReminderGenerateRequest(BaseModel):
    """提醒生成请求"""
    today_total_tasks: List[Dict[str, Any]] = Field(..., description="今日全部任务")
    today_incomplete_tasks: List[Dict[str, Any]] = Field(..., description="今日未完成任务")
    exam_total_tasks: List[Dict[str, Any]] = Field(..., description="备考全部任务")
    exam_completed_tasks: List[Dict[str, Any]] = Field(..., description="备考已完成任务")
    elapsed_study_days: float = Field(..., ge=0, description="已消耗备考天数")
    total_study_days: float = Field(..., gt=0, description="备考总天数")
    strictness_mode: str = Field("gentle", description="silent/gentle/intensive/nightmare/tangseng")


class ReminderGenerateResponse(BaseModel):
    """提醒生成响应"""
    content: str


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


class WeeklyReportRequest(BaseModel):
    """学习报告生成请求（支持任意日期范围，不限于自然周）"""
    user_id: str
    week_start: str = Field(..., description="起始日期，YYYY-MM-DD")
    week_end: Optional[str] = Field(default=None, description="结束日期，YYYY-MM-DD，不传则自动推算为起始+6天")
    total_plan: List[Dict[str, Any]] = Field(..., description="期间计划任务列表")
    weekly_completed: List[Dict[str, Any]] = Field(..., description="期间已完成的任务列表")


class WeeklyReportResponse(BaseModel):
    """学习报告响应"""
    report_id: Optional[str] = None
    user_id: str
    week_start: str
    week_end: str
    total_rate: float
    html_content: str
    summary: str
    total_planned: int = 0
    total_completed: int = 0
    completed_hours: float = 0.0
    streak_days: int = 0
    subject_stats: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    report_title: str = ""
    grade: str = ""
    daily_breakdown: List[Dict[str, Any]] = []


class ProfileSummary(BaseModel):
    """已收集的备考信息摘要"""
    exam_name: Optional[str] = None
    exam_type: Optional[str] = None
    exam_date: Optional[str] = None
    daily_hours: Optional[float] = None
    foundation_level: Optional[int] = None
    weak_subjects: List[str] = []
    rest_days_per_week: int = 1
    missing_fields: List[str] = []
    is_ready: bool = False


class PlanChatRequest(BaseModel):
    """多轮对话式计划生成请求（无状态 — 前端持有所有对话状态）"""
    user_id: str = "anonymous"
    message: str
    profile: Optional[ProfileSummary] = None
    search_results: List[str] = []
    messages: List[Dict[str, str]] = []


class PlanChatResponse(BaseModel):
    """多轮对话式计划生成响应（无状态）"""
    status: str  # "waiting_for_input" | "completed" | "error"
    action: str = ""  # "search" | "ask_user" | "generate_plan"
    message: str
    profile: Optional[ProfileSummary] = None
    search_results: List[str] = []
    messages: List[Dict[str, str]] = []
    plan_id: Optional[str] = None
    tasks: List[Dict[str, Any]] = []


# ── LLM Proxy & Search schemas ──

class LlmChatRequest(BaseModel):
    """LLM代理请求"""
    messages: List[Dict[str, str]] = []
    system_prompt: str = ""


class LlmChatResponse(BaseModel):
    """LLM代理响应"""
    content: str
    error: Optional[str] = None


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str


class SearchResult(BaseModel):
    """单条搜索结果"""
    title: str = ""
    snippet: str = ""
    url: str = ""


class SearchResponse(BaseModel):
    """搜索响应"""
    results: List[SearchResult] = []
    error: Optional[str] = None