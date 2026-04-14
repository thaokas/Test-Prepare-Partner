"""Planner Agent 节点函数"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, AIMessage
from app.llm import get_chat_model
from app.agents.planner.prompts import (
    PARSE_INPUT_PROMPT,
    CHECK_FIELDS_PROMPT,
    PARSE_REPLY_PROMPT,
    GENERATE_PLAN_PROMPT,
    RESOURCE_SUMMARY_PROMPT,
    get_foundation_level_desc,
)

logger = logging.getLogger(__name__)

# ── 常量：估算完成备考所需最少天数的基准 ──────────────────────────────
# 假设备考总量约 200 个学习单元（每单元 75 分钟），作为启发式估算
_TOTAL_STUDY_UNITS = 200
_UNIT_MINUTES = 75


async def calculate_study_time_node(state: Dict) -> Dict:
    """计算备考时间分配：总天数、阶段划分、预计完成日期（纯计算节点）"""
    try:
        exam_date = datetime.strptime(state["exam_date"], "%Y-%m-%d").date()
        today = date.today()
        total_days = (exam_date - today).days

        if total_days <= 0:
            return {
                "total_days": 0,
                "phases": [],
                "estimated_completion_date": str(exam_date),
                "error": "考试日期已过或为今天",
            }

        phases: List[Dict] = []
        cursor = today
        remaining = total_days

        # 基础阶段：剩余超过 90 天的部分
        if remaining > 90:
            foundation_days = remaining - 90
            foundation_end = cursor + timedelta(days=foundation_days - 1)
            phases.append({
                "phase": 1,
                "phase_name": "基础阶段",
                "start_date": str(cursor),
                "end_date": str(foundation_end),
                "days": foundation_days,
            })
            cursor = foundation_end + timedelta(days=1)
            remaining = 90

        # 强化阶段：剩余 31-90 天
        if remaining > 30:
            reinforcement_days = remaining - 30
            reinforcement_end = cursor + timedelta(days=reinforcement_days - 1)
            phases.append({
                "phase": 2,
                "phase_name": "强化阶段",
                "start_date": str(cursor),
                "end_date": str(reinforcement_end),
                "days": reinforcement_days,
            })
            cursor = reinforcement_end + timedelta(days=1)
            remaining = 30

        # 冲刺阶段：最后 ≤30 天
        sprint_end = exam_date - timedelta(days=1)
        if cursor <= sprint_end:
            phases.append({
                "phase": 3,
                "phase_name": "冲刺阶段",
                "start_date": str(cursor),
                "end_date": str(sprint_end),
                "days": (sprint_end - cursor).days + 1,
            })

        # 预估能否在考试日前完成备考
        daily_hours = state.get("daily_hours") or 2.0
        rest_days_per_week = state.get("rest_days_per_week") or 1
        effective_study_days_ratio = (7 - rest_days_per_week) / 7
        units_per_day = (daily_hours * 60) / _UNIT_MINUTES
        min_days = max(
            int(_TOTAL_STUDY_UNITS / (units_per_day * effective_study_days_ratio)),
            30,  # 至少备考 30 天
        )

        if min_days < total_days:
            completion_date = today + timedelta(days=min_days)
            # 不超过考试日
            estimated_completion_date = str(min(completion_date, exam_date - timedelta(days=1)))
        else:
            estimated_completion_date = str(exam_date)

        return {
            "total_days": total_days,
            "phases": phases,
            "estimated_completion_date": estimated_completion_date,
        }
    except Exception as e:
        logger.error(f"calculate_study_time_node error: {e}")
        return {
            "total_days": 90,
            "phases": [{"phase": 1, "phase_name": "基础阶段",
                        "start_date": str(date.today()),
                        "end_date": str(date.today() + timedelta(days=89)),
                        "days": 90}],
            "estimated_completion_date": state.get("exam_date", ""),
            "error": str(e),
        }


def _extract_json(text: str) -> Dict:
    """从 LLM 响应文本中提取 JSON（去除 markdown 代码块）"""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        # 取第一个代码块内容
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


async def parse_input_node(state: Dict) -> Dict:
    """解析用户初始输入，提取考试信息字段（LLM 节点）"""
    try:
        messages = state.get("messages", [])
        last_human = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
            ""
        )

        prompt = PARSE_INPUT_PROMPT.format(
            message=last_human,
            resource_summary=state.get("resource_summary", "（无资料）"),
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        data = _extract_json(response.content if isinstance(response.content, str) else str(response.content))

        updates: Dict = {}
        for field in ("exam_name", "exam_type", "exam_date", "daily_hours",
                      "foundation_level", "weak_subjects", "rest_days_per_week"):
            val = data.get(field)
            if val is not None:
                updates[field] = val

        # 合并 URL 列表（去重）
        existing_urls = state.get("urls", [])
        existing_pdf = state.get("pdf_urls", [])
        existing_img = state.get("image_urls", [])
        new_urls = [u for u in data.get("urls", []) if u not in existing_urls]
        new_pdf = [u for u in data.get("pdf_urls", []) if u not in existing_pdf]
        new_img = [u for u in data.get("image_urls", []) if u not in existing_img]
        if new_urls or existing_urls:
            updates["urls"] = existing_urls + new_urls
        if new_pdf or existing_pdf:
            updates["pdf_urls"] = existing_pdf + new_pdf
        if new_img or existing_img:
            updates["image_urls"] = existing_img + new_img

        return updates
    except Exception as e:
        logger.error(f"parse_input_node error: {e}")
        return {"error": str(e)}
