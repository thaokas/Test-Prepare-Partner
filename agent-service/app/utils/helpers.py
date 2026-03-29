"""
工具函数
"""
from datetime import date, timedelta
from typing import Optional


def calculate_days_remaining(exam_date: date) -> int:
    """计算距离考试还有多少天"""
    delta = exam_date - date.today()
    return max(0, delta.days)


def calculate_phase(days_remaining: int) -> int:
    """
    计算当前阶段
    1: 基础阶段 (>90天)
    2: 强化阶段 (45-90天)
    3: 冲刺阶段 (<45天)
    """
    if days_remaining > 90:
        return 1
    elif days_remaining >= 45:
        return 2
    else:
        return 3


def get_phase_name(phase: int) -> str:
    """获取阶段名称"""
    names = {1: "基础阶段", 2: "强化阶段", 3: "冲刺阶段"}
    return names.get(phase, "未知阶段")


def calculate_completion_rate(completed: int, total: int) -> float:
    """计算完成率"""
    if total <= 0:
        return 0.0
    return round((completed / total) * 100, 2)


def get_week_date_range(base_date: Optional[date] = None) -> tuple[date, date]:
    """获取指定日期所在周的日期范围（周一到周日）"""
    if base_date is None:
        base_date = date.today()

    week_start = base_date - timedelta(days=base_date.weekday())
    week_end = week_start + timedelta(days=6)

    return week_start, week_end


def format_duration(minutes: int) -> str:
    """格式化时长"""
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours}小时"
    return f"{hours}小时{remaining_minutes}分钟"