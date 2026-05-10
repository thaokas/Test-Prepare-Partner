"""周报生成Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class ReportState(TypedDict):
    # 输入（由调用方直接传入）
    user_id: str
    week_start: str               # YYYY-MM-DD（起始日期）
    week_end: str                 # YYYY-MM-DD（结束日期）
    total_plan: List[Dict]        # 期间计划任务列表
    weekly_completed: List[Dict]  # 期间已完成的任务列表

    # 计算指标（calculate_metrics_node 产出）
    daily_breakdown: List[Dict]   # [{date, planned_count, completed_count, planned_minutes, completed_minutes, rate}]
    subject_stats: List[Dict]     # [{subject, planned, completed, rate, planned_minutes, completed_minutes}]
    total_planned: int            # 期间计划任务总数
    total_completed: int          # 期间完成任务总数
    total_rate: float             # 总完成率（0-100）
    estimated_minutes_total: int  # 期间计划总时长（分钟）
    completed_minutes: int        # 期间完成总时长（分钟）
    streak_days: int              # 期间有打卡记录的不重复天数
    completed_tasks_detail: str   # 已完成任务的文字明细
    report_title: str             # 报告标题（根据日期范围自动生成）
    grade: str                    # 等级评定（S/A/B/C/D）

    # LLM 分析（analyze_performance_node 产出）
    highlights: List[str]
    issues: List[str]

    # LLM 生成（generate_html_report_node 产出）
    html_content: str             # 完整 HTML 周报
    summary: str                  # 纯文字摘要（降级备用）
    suggestions: List[str]        # 后续建议

    # 输出
    report_id: Optional[str]
    error: Optional[str]
