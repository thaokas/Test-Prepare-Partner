"""监督提醒Agent节点函数"""
import json
import logging
from typing import Dict

from app.agents.reminder.state import ReminderState
from app.agents.reminder.prompts import (
    REMINDER_ANALYZE_PROMPT, REMINDER_GENERATE_PROMPT, TONE_DESCRIPTIONS
)

logger = logging.getLogger(__name__)


async def get_incomplete_tasks_node(state: ReminderState) -> Dict:
    """获取今日未完成任务（工具节点）"""
    try:
        from app.tools.db_tools import get_today_tasks, get_checkin_history, get_user_streak

        all_tasks = await get_today_tasks.ainvoke({"user_id": state["user_id"]})
        incomplete = [t for t in all_tasks if t.get("status", 0) != 2]

        history = await get_checkin_history.ainvoke({"user_id": state["user_id"], "days": 7})
        recent_rate = 0.0
        if history:
            recent_rate = sum(h.get("completion_rate", 0) for h in history) / len(history)

        streak = await get_user_streak.ainvoke({"user_id": state["user_id"]})

        return {
            "incomplete_tasks": incomplete,
            "remaining_count": len(incomplete),
            "recent_completion_rate": round(recent_rate, 1),
            "streak_days": streak,
        }
    except Exception as e:
        logger.error(f"get_incomplete_tasks_node error: {e}")
        return {"incomplete_tasks": [], "remaining_count": 0, "recent_completion_rate": 0.0, "streak_days": 0}


async def analyze_user_status_node(state: ReminderState) -> Dict:
    """使用LLM分析用户状态（LLM节点）"""
    if state.get("mode", 1) == 0:
        return {"strategy": "silent", "tone": "none"}
    try:
        from app.llm import get_llm
        from app.models.reminder_setting import ReminderSetting

        mode_names = {0: "静默", 1: "温柔", 2: "强化", 3: "唐僧"}
        prompt = REMINDER_ANALYZE_PROMPT.format(
            remaining_count=state.get("remaining_count", 0),
            recent_completion_rate=state.get("recent_completion_rate", 0),
            streak_days=state.get("streak_days", 0),
            mode_name=mode_names.get(state.get("mode", 1), "温柔"),
        )
        llm = get_llm()
        response = await llm.ainvoke(prompt, system_prompt="只输出JSON格式数据。")
        text = response.strip()
        if "```" in text:
            text = text.split("```")[1].lstrip("json")
        result = json.loads(text)
        return {
            "strategy": result.get("status", "on_track"),
            "tone": result.get("suggested_tone", "gentle"),
        }
    except Exception as e:
        logger.error(f"analyze_user_status_node error: {e}")
        return {"strategy": "on_track", "tone": "gentle"}


async def generate_reminder_node(state: ReminderState) -> Dict:
    """使用LLM生成提醒内容（LLM节点）"""
    if state.get("mode", 1) == 0:
        return {"content": ""}
    try:
        from app.llm import get_llm

        task_summary = "、".join(
            t.get("subject", "") for t in state.get("incomplete_tasks", [])[:3]
        ) or "未完成任务"

        tone_desc = TONE_DESCRIPTIONS.get(state.get("mode", 1), "温柔体贴")
        prompt = REMINDER_GENERATE_PROMPT.format(
            tone_desc=tone_desc,
            remaining_count=state.get("remaining_count", 0),
            task_summary=task_summary,
            status=state.get("strategy", "on_track"),
            trigger_time=state.get("trigger_time", "21:00"),
        )
        llm = get_llm()
        content = await llm.ainvoke(prompt)
        return {"content": content.strip()}
    except Exception as e:
        logger.error(f"generate_reminder_node error: {e}")
        return {"content": f"还有{state.get('remaining_count', 0)}个任务未完成，加油！", "error": str(e)}
