"""计划生成Agent节点函数"""
import json
import logging
from datetime import date, datetime
from typing import Dict

from app.agents.plan_generation.state import PlanGenerationState
from app.agents.plan_generation.prompts import PLAN_GENERATION_PROMPT, get_foundation_level_desc

logger = logging.getLogger(__name__)


async def calculate_phase_node(state: PlanGenerationState) -> Dict:
    """计算当前备考阶段（纯计算节点）"""
    try:
        exam_date = datetime.strptime(state["exam_date"], "%Y-%m-%d").date()
        today = date.today()
        days_remaining = (exam_date - today).days

        if days_remaining > 90:
            current_phase = 1
            phase_name = "基础阶段"
        elif days_remaining > 30:
            current_phase = 2
            phase_name = "强化阶段"
        else:
            current_phase = 3
            phase_name = "冲刺阶段"

        return {
            "days_remaining": days_remaining,
            "current_phase": current_phase,
            "phase_name": phase_name,
        }
    except Exception as e:
        logger.error(f"calculate_phase_node error: {e}")
        return {"days_remaining": 90, "current_phase": 1, "phase_name": "基础阶段", "error": str(e)}


async def search_exam_info_node(state: PlanGenerationState) -> Dict:
    """搜索考试信息（工具节点）"""
    try:
        from app.tools.search_tools import search_exam_info
        result = await search_exam_info.ainvoke({
            "exam_name": state["exam_name"],
            "exam_type": state["exam_type"]
        })
        return {"exam_info": result}
    except Exception as e:
        logger.error(f"search_exam_info_node error: {e}")
        return {"exam_info": {}}


async def generate_tasks_node(state: PlanGenerationState) -> Dict:
    """使用LLM生成个性化任务（LLM节点）"""
    try:
        from app.llm import get_llm

        generate_days = min(state["days_remaining"], 14)
        prompt = PLAN_GENERATION_PROMPT.format(
            exam_name=state["exam_name"],
            exam_type=state["exam_type"],
            exam_date=state["exam_date"],
            days_remaining=state["days_remaining"],
            phase_name=state["phase_name"],
            daily_hours=state["daily_hours"],
            foundation_level_desc=get_foundation_level_desc(state["foundation_level"]),
            weak_subjects="、".join(state.get("weak_subjects", [])) or "无特别薄弱科目",
            exam_info=json.dumps(state.get("exam_info", {}), ensure_ascii=False),
            generate_days=generate_days,
            current_phase=state["current_phase"],
        )

        llm = get_llm()
        response = await llm.ainvoke(prompt, system_prompt="你是一名专业备考规划师，只输出JSON格式数据。")

        # 提取JSON
        text = response.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        tasks = json.loads(text)
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"generate_tasks_node error: {e}")
        return {"tasks": [], "error": str(e)}


async def save_plan_node(state: PlanGenerationState) -> Dict:
    """保存计划和任务到数据库（工具节点）"""
    try:
        from app.tools.db_tools import create_study_plan
        result = await create_study_plan.ainvoke({
            "user_id": state["user_id"],
            "exam_name": state["exam_name"],
            "exam_type": state["exam_type"],
            "exam_date": state["exam_date"],
            "daily_hours": state["daily_hours"],
            "tasks": state.get("tasks", []),
        })
        return {
            "plan_id": result.get("plan_id"),
            "message": f"已为你生成{len(state.get('tasks', []))}个学习任务，加油！",
        }
    except Exception as e:
        logger.error(f"save_plan_node error: {e}")
        return {"plan_id": None, "message": "计划生成失败，请重试。", "error": str(e)}
