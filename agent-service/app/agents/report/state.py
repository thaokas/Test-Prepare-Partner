"""周报生成Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class ReportState(TypedDict):
    # 输入
    user_id: str
    week_start: str     # YYYY-MM-DD (周一)
    week_end: str       # YYYY-MM-DD (周日)

    # 原始数据
    daily_checkins: List[Dict]

    # 计算指标
    daily_rates: List[Dict]
    average_rate: float
    week_over_week: float
    current_streak: int
    best_study_time: Optional[str]

    # LLM分析
    highlights: List[str]
    issues: List[str]

    # LLM生成
    summary: str
    suggestions: List[str]

    # 输出
    report_id: Optional[str]
    error: Optional[str]
