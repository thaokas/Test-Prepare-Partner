"""监督提醒Agent节点函数"""
import logging
from datetime import datetime
from typing import Dict

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from app.agents.reminder.state import ReminderState
from app.agents.reminder.prompts import get_reminder_prompt

logger = logging.getLogger(__name__)


@tool
def get_current_time() -> str:
    """获取当前的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def get_current_time_node(state: ReminderState) -> Dict:
    """LLM 通过工具调用获取当前时间（工具节点）。

    若模式为 silent，直接短路返回空内容。
    否则，绑定 get_current_time 工具让 LLM 发出 tool_call，
    Python 执行工具并将时间写入 state。
    """
    if state.get("strictness_mode") == "silent":
        return {"content": "", "current_time": None}

    try:
        from app.llm import get_chat_model

        llm = get_chat_model().bind_tools([get_current_time])
        response = await llm.ainvoke(
            [HumanMessage(content="请使用工具获取当前时间。")]
        )

        # 执行 LLM 发出的 tool_call
        if response.tool_calls:
            result = get_current_time.invoke({})
            return {"current_time": result}

        # Fallback：LLM 未发出 tool_call，直接取时间
        logger.warning("get_current_time_node: LLM did not emit tool_call, using fallback")
        return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    except Exception as e:
        logger.error(f"get_current_time_node error: {e}")
        return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "error": str(e)}


async def generate_reminder_node(state: ReminderState) -> Dict:
    """根据严格程度模式生成提醒内容（LLM 节点）。"""
    try:
        from app.llm import get_chat_model

        # ── 派生统计数据 ──────────────────────────────────────────────────────
        today_total = len(state.get("today_total_tasks") or [])
        today_incomplete = len(state.get("today_incomplete_tasks") or [])
        today_done = today_total - today_incomplete

        exam_total = len(state.get("exam_total_tasks") or [])
        exam_done = len(state.get("exam_completed_tasks") or [])
        exam_rate = round(exam_done / exam_total * 100, 1) if exam_total > 0 else 0.0

        elapsed_days = state.get("elapsed_study_days", 0.0)
        total_days = state.get("total_study_days", 0.0)
        time_rate = round(elapsed_days / total_days * 100, 1) if total_days > 0 else 0.0

        # 未完成任务名称，最多展示 5 个
        incomplete_tasks = state.get("today_incomplete_tasks") or []
        incomplete_names = "、".join(
            t.get("subject") or t.get("name") or t.get("title") or "未知任务"
            for t in incomplete_tasks[:5]
        ) or "无"

        # ── 构造 Prompt ───────────────────────────────────────────────────────
        mode = state.get("strictness_mode", "gentle")
        prompt_template = get_reminder_prompt(mode)
        prompt = prompt_template.format(
            current_time=state.get("current_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            today_done=today_done,
            today_total=today_total,
            incomplete_names=incomplete_names,
            exam_done=exam_done,
            exam_total=exam_total,
            exam_rate=exam_rate,
            elapsed_days=elapsed_days,
            total_days=total_days,
            time_rate=time_rate,
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)
        return {"content": content.strip()}

    except Exception as e:
        logger.error(f"generate_reminder_node error: {e}")
        incomplete_count = len(state.get("today_incomplete_tasks") or [])
        return {
            "content": f"还有 {incomplete_count} 个任务未完成，加油！",
            "error": str(e),
        }
