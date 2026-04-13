"""打卡处理Agent状态定义"""
from typing import TypedDict, List, Dict, Optional


class CheckinState(TypedDict):
    # 输入
    user_id: str
    content: str
    checkin_type: int           # 1-文字 2-图片

    # LLM解析结果
    parsed_tasks: List[str]     # 提取的任务关键词
    confidence: float

    # 匹配结果
    matched_tasks: List[Dict]
    completed_count: int
    total_count: int

    # 计算结果
    completion_rate: float
    streak_updated: bool
    new_streak: int

    # 彩蛋
    easter_egg: Optional[str]

    # LLM生成的鼓励
    encouragement: str

    # 输出
    checkin_id: Optional[str]
    error: Optional[str]
