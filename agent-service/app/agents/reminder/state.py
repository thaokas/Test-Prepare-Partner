"""监督提醒Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class ReminderState(TypedDict):
    # 输入
    user_id: str
    mode: int           # 0-静默 1-温柔 2-强化 3-唐僧
    trigger_time: str   # HH:MM

    # 未完成任务
    incomplete_tasks: List[Dict]
    remaining_count: int

    # 用户状态
    recent_completion_rate: float
    streak_days: int

    # 提醒策略
    strategy: str
    tone: str

    # LLM生成的提醒内容
    content: str

    # 输出
    error: Optional[str]
