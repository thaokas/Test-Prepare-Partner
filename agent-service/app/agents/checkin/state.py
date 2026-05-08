"""打卡处理Agent状态定义"""
from typing import TypedDict, Optional


class CheckinState(TypedDict):
    # 输入
    image_url: Optional[str]          # 打卡图片URL（可选）
    completed_content: str            # 今日完成的计划内容与完成程度
    overall_completion_rate: float    # 整个备考计划完成比例（0-100）

    # 中间结果
    image_summary: Optional[str]      # 图片内容摘要（由多模态模型生成）

    # 输出
    encouragement: str
    error: Optional[str]
