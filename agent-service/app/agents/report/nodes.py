"""周报生成Agent节点函数"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict

from app.agents.report.state import ReportState
from app.agents.report.prompts import ANALYZE_PROMPT, SUMMARY_PROMPT, SUGGESTIONS_PROMPT

logger = logging.getLogger(__name__)


async def aggregate_data_node(state: ReportState) -> Dict:
    """获取本周打卡数据（工具节点）"""
    try:
        from app.tools.db_tools import get_weekly_data, get_user_streak

        week_start = state["week_start"]
        week_end = state.get("week_end") or str(
            datetime.strptime(week_start, "%Y-%m-%d").date() + timedelta(days=6)
        )

        data = await get_weekly_data.ainvoke({"user_id": state["user_id"], "week_start": week_start})
        streak = await get_user_streak.ainvoke({"user_id": state["user_id"]})

        return {
            "week_end": week_end,
            "daily_checkins": data.get("daily_checkins", []),
            "current_streak": streak,
        }
    except Exception as e:
        logger.error(f"aggregate_data_node error: {e}")
        return {"daily_checkins": [], "current_streak": 0, "week_end": state.get("week_end", "")}


async def calculate_metrics_node(state: ReportState) -> Dict:
    """计算本周指标（纯计算节点）"""
    checkins = state.get("daily_checkins", [])
    daily_rates = [
        {"date": c.get("checkin_date", ""), "rate": c.get("completion_rate", 0)}
        for c in checkins
    ]

    rates = [c.get("completion_rate", 0) for c in checkins]
    average_rate = round(sum(rates) / len(rates), 1) if rates else 0.0

    # 环比（简化：与0对比，实际应查上周数据）
    week_over_week = 0.0

    # 最佳学习时间（从checkin_time中提取）
    best_study_time = None
    if checkins:
        times = [c.get("checkin_time", "") for c in checkins if c.get("checkin_time")]
        if times:
            best_study_time = max(set(times), key=times.count)

    return {
        "daily_rates": daily_rates,
        "average_rate": average_rate,
        "week_over_week": week_over_week,
        "best_study_time": best_study_time,
    }


async def analyze_performance_node(state: ReportState) -> Dict:
    """使用LLM分析表现亮点和问题（LLM节点）"""
    try:
        from app.llm import get_llm

        prompt = ANALYZE_PROMPT.format(
            average_rate=state.get("average_rate", 0),
            week_over_week=state.get("week_over_week", 0),
            current_streak=state.get("current_streak", 0),
            daily_rates=json.dumps(state.get("daily_rates", []), ensure_ascii=False),
        )
        llm = get_llm()
        response = await llm.ainvoke(prompt, system_prompt="只输出JSON格式数据。")
        text = response.strip()
        if "```" in text:
            text = text.split("```")[1].lstrip("json")
        result = json.loads(text)
        return {
            "highlights": result.get("highlights", []),
            "issues": result.get("issues", []),
        }
    except Exception as e:
        logger.error(f"analyze_performance_node error: {e}")
        return {"highlights": [], "issues": []}


async def generate_summary_node(state: ReportState) -> Dict:
    """使用LLM生成周报总结（LLM节点）"""
    try:
        from app.llm import get_llm

        prompt = SUMMARY_PROMPT.format(
            average_rate=state.get("average_rate", 0),
            highlights="、".join(state.get("highlights", [])) or "继续努力",
            issues="、".join(state.get("issues", [])) or "无明显问题",
        )
        llm = get_llm()
        summary = await llm.ainvoke(prompt)

        # 生成建议
        suggestion_prompt = SUGGESTIONS_PROMPT.format(
            average_rate=state.get("average_rate", 0),
            issues="、".join(state.get("issues", [])) or "无",
        )
        sug_response = await llm.ainvoke(suggestion_prompt, system_prompt="只输出JSON数组格式。")
        sug_text = sug_response.strip()
        if "```" in sug_text:
            sug_text = sug_text.split("```")[1].lstrip("json")
        suggestions = json.loads(sug_text)

        return {"summary": summary.strip(), "suggestions": suggestions}
    except Exception as e:
        logger.error(f"generate_summary_node error: {e}")
        return {"summary": "本周表现良好，继续加油！", "suggestions": ["保持每日打卡", "及时复习薄弱科目"]}


async def save_report_node(state: ReportState) -> Dict:
    """保存周报到数据库（工具节点）"""
    try:
        from app.tools.db_tools import save_weekly_report, get_active_plan

        plan = await get_active_plan.ainvoke({"user_id": state["user_id"]})
        plan_id = plan.get("plan_id") if plan else ""

        result = await save_weekly_report.ainvoke({
            "user_id": state["user_id"],
            "plan_id": plan_id or "",
            "week_start": state["week_start"],
            "week_end": state.get("week_end", ""),
            "average_rate": state.get("average_rate", 0),
            "summary": state.get("summary", ""),
            "suggestions": json.dumps(state.get("suggestions", []), ensure_ascii=False),
            "daily_rates": json.dumps(state.get("daily_rates", []), ensure_ascii=False),
        })
        return {"report_id": result.get("report_id")}
    except Exception as e:
        logger.error(f"save_report_node error: {e}")
        return {"report_id": None, "error": str(e)}
