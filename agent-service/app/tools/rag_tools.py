"""
RAG检索工具（LangChain Tool）
"""
from typing import Optional

from langchain.tools import tool

from app.rag.retriever import get_retriever


@tool
def get_encouragement_by_rate(completion_rate: float) -> str:
    """根据任务完成率获取鼓励话术

    Args:
        completion_rate: 完成率（0-100）

    Returns:
        鼓励话术文本
    """
    retriever = get_retriever()
    encouragement = retriever.get_encouragement(completion_rate)
    return encouragement.get("text", "加油！")


@tool
def get_strategy_for_exam(exam_type: str, phase: int) -> str:
    """获取特定考试类型的备考策略

    Args:
        exam_type: 考试类型（考研/期末/考证/考公/语言）
        phase: 阶段（1-基础 2-强化 3-冲刺）

    Returns:
        备考策略建议
    """
    retriever = get_retriever()
    strategy = retriever.get_exam_strategy(exam_type, phase)

    if not strategy:
        return f"暂无{exam_type}的备考策略"

    return f"【{strategy.get('focus', '')}】{strategy.get('tips', '')}"


@tool
def get_comfort_message(emotion: str) -> str:
    """获取情感安慰话术

    Args:
        emotion: 情绪类型（tired/frustrated/anxious）

    Returns:
        安慰话术
    """
    retriever = get_retriever()
    return retriever.get_comfort_word(emotion)


@tool
def get_random_easter_egg() -> str:
    """随机获取一个彩蛋内容

    Returns:
        彩蛋内容
    """
    import random

    retriever = get_retriever()
    egg_types = ["late_night", "early_bird", "weekend", "random"]

    # 根据当前时间选择彩蛋类型
    from datetime import datetime
    hour = datetime.now().hour

    if 23 <= hour or hour < 5:
        egg_type = "late_night"
    elif 5 <= hour < 7:
        egg_type = "early_bird"
    elif datetime.now().weekday() >= 5:  # 周末
        egg_type = "weekend"
    else:
        egg_type = random.choice(egg_types)

    egg = retriever.get_easter_egg(egg_type)
    return egg or "小搭陪你～"


@tool
def get_daily_tip() -> str:
    """获取每日小贴士

    Returns:
        小贴士内容
    """
    retriever = get_retriever()
    return retriever.get_random_tip()


# 工具列表
RAG_TOOLS = [
    get_encouragement_by_rate,
    get_strategy_for_exam,
    get_comfort_message,
    get_random_easter_egg,
    get_daily_tip
]