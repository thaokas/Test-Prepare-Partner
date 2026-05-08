"""监督提醒Agent状态定义"""
from typing import TypedDict, List, Dict, Optional, Literal

StrictnessMode = Literal["silent", "gentle", "intensive", "nightmare", "tangseng"]


class ReminderState(TypedDict):
    # ── 后端传入 ──────────────────────────────────────────────────────────────
    today_total_tasks: List[Dict]       # 今日全部任务
    today_incomplete_tasks: List[Dict]  # 今日未完成任务
    exam_total_tasks: List[Dict]        # 备考全部任务
    exam_completed_tasks: List[Dict]    # 备考已完成任务
    elapsed_study_days: float           # 已消耗备考天数
    total_study_days: float             # 备考总天数
    strictness_mode: StrictnessMode     # silent/gentle/intensive/nightmare/tangseng

    # ── 工具节点填充 ──────────────────────────────────────────────────────────
    current_time: Optional[str]         # LLM 调用 get_current_time 工具后写入

    # ── 输出 ──────────────────────────────────────────────────────────────────
    content: str
    error: Optional[str]
