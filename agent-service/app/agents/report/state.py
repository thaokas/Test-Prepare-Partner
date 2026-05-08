"""周报生成Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class ReportState(TypedDict):
    # 输入（由调用方直接传入）
    user_id: str
    week_start: str               # YYYY-MM-DD（周一）
    week_end: str                 # YYYY-MM-DD（周日）
    total_plan: List[Dict]        # 本周计划任务列表
    weekly_completed: List[Dict]  # 本周已完成的任务列表

    # 计算指标（calculate_metrics_node 产出）
    subject_stats: List[Dict]     # [{subject, planned, completed, rate, planned_minutes, completed_minutes}]
    total_planned: int            # 本周计划任务总数
    total_completed: int          # 本周完成任务总数
    total_rate: float             # 总完成率（0-100）
    estimated_minutes_total: int  # 本周计划总时长（分钟）
    completed_minutes: int        # 本周完成总时长（分钟）
    streak_days: int              # 本周有打卡记录的不重复天数

    # LLM 分析（analyze_performance_node 产出）
    highlights: List[str]
    issues: List[str]

    # LLM 生成（generate_html_report_node 产出）
    html_content: str             # 完整 HTML 周报
    summary: str                  # 纯文字摘要（降级备用）

    # 输出
    report_id: Optional[str]
    error: Optional[str]
