"""
RAG工具 - 从知识库检索鼓励话术、备考策略、彩蛋等
"""
from langchain.tools import tool

from app.rag.retriever import get_retriever


@tool
def get_encouragement_by_rate(completion_rate: float) -> str:
    """根据任务完成率从知识库获取鼓励话术

    Args:
        completion_rate: 完成率（0-100）

    Returns:
        鼓励话术文本
    """
    retriever = get_retriever()
    result = retriever.get_encouragement(completion_rate)
    return result.get("text", "加油，你做得很棒！")


@tool
def get_exam_strategy(exam_type: str, phase: int) -> str:
    """获取指定考试类型和备考阶段的策略建议

    Args:
        exam_type: 考试类型（考研/期末/考证/考公/语言）
        phase: 备考阶段（1-基础 2-强化 3-冲刺）

    Returns:
        备考策略建议文本
    """
    retriever = get_retriever()
    strategy = retriever.get_exam_strategy(exam_type, phase)
    if not strategy:
        return f"暂无{exam_type}的备考策略，请结合自身情况制定计划。"
    return f"【{strategy.get('focus', '')}】{strategy.get('tips', '')}"


@tool
def get_easter_egg_message(egg_type: str) -> str:
    """获取指定类型的彩蛋消息

    Args:
        egg_type: 彩蛋类型（late_night/early_bird/weekend/streak_3/streak_7）

    Returns:
        彩蛋消息文本
    """
    retriever = get_retriever()
    message = retriever.get_easter_egg(egg_type)
    return message or ""


RAG_TOOLS = [
    get_encouragement_by_rate,
    get_exam_strategy,
    get_easter_egg_message,
]
