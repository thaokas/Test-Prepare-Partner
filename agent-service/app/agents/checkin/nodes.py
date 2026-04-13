"""打卡处理Agent节点函数"""
import json
import logging
from datetime import datetime
from typing import Dict

from app.agents.checkin.state import CheckinState
from app.agents.checkin.prompts import CHECKIN_PARSE_PROMPT, CHECKIN_ENCOURAGEMENT_PROMPT

logger = logging.getLogger(__name__)


async def parse_content_node(state: CheckinState) -> Dict:
    """使用LLM解析打卡内容，提取完成的任务关键词"""
    try:
        from app.llm import get_llm
        from app.tools.db_tools import get_today_tasks

        today_tasks = await get_today_tasks.ainvoke({"user_id": state["user_id"]})
        tasks_text = "\n".join(
            f"- {t.get('subject', '')}: {t.get('task_content', '')}" for t in today_tasks
        ) or "（暂无今日任务记录）"

        prompt = CHECKIN_PARSE_PROMPT.format(
            today_tasks=tasks_text,
            content=state["content"],
        )
        llm = get_llm()
        response = await llm.ainvoke(prompt, system_prompt="你是备考督导助手，只输出JSON格式数据。")

        text = response.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text)

        return {
            "parsed_tasks": result.get("completed_tasks", []) + result.get("partial_tasks", []),
            "confidence": result.get("confidence", 0.8),
        }
    except Exception as e:
        logger.error(f"parse_content_node error: {e}")
        return {"parsed_tasks": [], "confidence": 0.0, "error": str(e)}


async def identify_tasks_node(state: CheckinState) -> Dict:
    """根据关键词匹配今日任务（工具节点）"""
    try:
        from app.tools.db_tools import match_tasks_by_keywords, get_today_tasks

        all_tasks = await get_today_tasks.ainvoke({"user_id": state["user_id"]})
        matched = await match_tasks_by_keywords.ainvoke({
            "user_id": state["user_id"],
            "keywords": state.get("parsed_tasks", []),
        })
        return {
            "matched_tasks": matched,
            "completed_count": len(matched),
            "total_count": len(all_tasks),
        }
    except Exception as e:
        logger.error(f"identify_tasks_node error: {e}")
        return {"matched_tasks": [], "completed_count": 0, "total_count": 0}


async def calculate_rate_node(state: CheckinState) -> Dict:
    """计算完成率（纯计算节点）"""
    total = state.get("total_count", 0)
    completed = state.get("completed_count", 0)
    rate = (completed / total * 100) if total > 0 else 0.0
    return {"completion_rate": round(rate, 1)}


async def check_streak_node(state: CheckinState) -> Dict:
    """检查并更新连续打卡天数（工具节点）"""
    try:
        from app.tools.db_tools import get_user_streak, update_user_streak

        current_streak = await get_user_streak.ainvoke({"user_id": state["user_id"]})
        new_streak = current_streak + 1
        await update_user_streak.ainvoke({"user_id": state["user_id"], "new_streak": new_streak})
        return {"new_streak": new_streak, "streak_updated": True}
    except Exception as e:
        logger.error(f"check_streak_node error: {e}")
        return {"new_streak": 0, "streak_updated": False}


async def check_easter_egg_node(state: CheckinState) -> Dict:
    """检查是否触发彩蛋条件"""
    try:
        from app.tools.rag_tools import get_easter_egg_message

        streak = state.get("new_streak", 0)
        hour = datetime.now().hour

        egg_type = None
        if streak == 3:
            egg_type = "streak_3"
        elif streak == 7:
            egg_type = "streak_7"
        elif 23 <= hour or hour < 5:
            egg_type = "late_night"
        elif 5 <= hour < 7:
            egg_type = "early_bird"

        if egg_type:
            message = get_easter_egg_message.invoke({"egg_type": egg_type})
            return {"easter_egg": message or None}
        return {"easter_egg": None}
    except Exception as e:
        logger.error(f"check_easter_egg_node error: {e}")
        return {"easter_egg": None}


async def generate_encouragement_node(state: CheckinState) -> Dict:
    """使用LLM生成个性化鼓励话术（LLM节点）"""
    try:
        from app.llm import get_llm

        prompt = CHECKIN_ENCOURAGEMENT_PROMPT.format(
            completion_rate=state.get("completion_rate", 0),
            streak_days=state.get("new_streak", 0),
            checkin_time=datetime.now().strftime("%H:%M"),
        )
        llm = get_llm()
        encouragement = await llm.ainvoke(prompt)
        return {"encouragement": encouragement.strip()}
    except Exception as e:
        logger.error(f"generate_encouragement_node error: {e}")
        from app.tools.rag_tools import get_encouragement_by_rate
        fallback = get_encouragement_by_rate.invoke({"completion_rate": state.get("completion_rate", 0)})
        return {"encouragement": fallback}


async def save_checkin_node(state: CheckinState) -> Dict:
    """保存打卡记录到数据库（工具节点）"""
    try:
        from app.tools.db_tools import create_checkin_record, get_active_plan

        plan = await get_active_plan.ainvoke({"user_id": state["user_id"]})
        plan_id = plan.get("plan_id") if plan else ""

        result = await create_checkin_record.ainvoke({
            "user_id": state["user_id"],
            "plan_id": plan_id or "",
            "completed_tasks": [t.get("id", "") for t in state.get("matched_tasks", [])],
            "total_tasks": state.get("total_count", 0),
            "completion_rate": state.get("completion_rate", 0),
            "content": state["content"],
        })
        return {"checkin_id": result.get("checkin_id")}
    except Exception as e:
        logger.error(f"save_checkin_node error: {e}")
        return {"checkin_id": None, "error": str(e)}
