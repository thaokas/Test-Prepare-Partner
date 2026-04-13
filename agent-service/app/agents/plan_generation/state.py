"""计划生成Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class PlanGenerationState(TypedDict):
    # 输入
    user_id: str
    exam_name: str
    exam_type: str
    exam_date: str
    daily_hours: float
    foundation_level: int       # 0-零基础 1-有一定基础 2-基础扎实
    weak_subjects: List[str]

    # 搜索结果
    exam_info: Dict

    # 计算结果
    days_remaining: int
    current_phase: int          # 1-基础 2-强化 3-冲刺
    phase_name: str

    # LLM生成的任务
    tasks: List[Dict]

    # 输出
    plan_id: Optional[str]
    message: str
    error: Optional[str]
