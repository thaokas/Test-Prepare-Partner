"""Planner Agent 状态定义"""
from typing import TypedDict, List, Dict, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class PlannerState(TypedDict):
    # ── 输入 ──────────────────────────────────────
    user_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    urls: List[str]
    pdf_urls: List[str]
    image_urls: List[str]

    # ── 从自然语言/资料提取的考试信息 ────────────
    exam_name: Optional[str]
    exam_type: Optional[str]
    exam_date: Optional[str]          # YYYY-MM-DD
    daily_hours: Optional[float]
    foundation_level: Optional[int]   # 0=零基础 1=有一定基础 2=已复习一轮
    weak_subjects: List[str]
    rest_days_per_week: int           # 默认 1

    # ── 追问控制 ────────────────────────────────
    clarification_rounds: int         # 已追问轮数，上限 6
    clarification_question: Optional[str]

    # ── 资料分析 & 搜索 ───────────────────────────
    resource_summary: str
    exam_info: Dict

    # ── 时间计算 ─────────────────────────────────
    total_days: int
    phases: List[Dict]                # [{phase, phase_name, start_date, end_date, days}]
    estimated_completion_date: str    # 可能早于 exam_date

    # ── 输出 ─────────────────────────────────────
    tasks: List[Dict]
    plan_id: Optional[str]
    message: str
    error: Optional[str]
