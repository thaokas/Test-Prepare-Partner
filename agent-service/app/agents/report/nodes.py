"""周报生成Agent节点函数"""
import json
import logging
from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.report.state import ReportState
from app.agents.report.prompts import ANALYZE_PROMPT, REPORT_TEXT_PROMPT, HTML_TEMPLATE

logger = logging.getLogger(__name__)


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _parse_json_response(text: str) -> dict:
    """从 LLM 响应中提取 JSON，兼容 ```json ... ``` 包裹格式"""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        # parts[1] 是代码块内容，去掉可能的 "json\n" 前缀
        text = parts[1].lstrip("json").lstrip("JSON").strip()
    return json.loads(text)


def _build_subject_rows(subject_stats: list) -> str:
    """生成各科明细的 HTML 表格行"""
    rows = []
    for s in subject_stats:
        rate = s.get("rate", 0)
        if rate >= 80:
            color_cls = "tag-green"
        elif rate >= 50:
            color_cls = "tag-orange"
        else:
            color_cls = "tag-red"
        rows.append(
            f'<tr>'
            f'<td>{s["subject"]}</td>'
            f'<td>{s["planned"]}</td>'
            f'<td>{s["completed"]}</td>'
            f'<td class="{color_cls}">{rate}%</td>'
            f'</tr>'
        )
    return "\n        ".join(rows) if rows else '<tr><td colspan="4" style="color:#bbb;text-align:center;">暂无数据</td></tr>'


def _build_list_html(items: list, css_class: str = "list-item") -> str:
    """生成亮点/问题列表 HTML"""
    if not items:
        return '<div class="empty-hint">暂无</div>'
    return "".join(f'<div class="{css_class}">{item}</div>' for item in items)


def _build_suggestions_html(suggestions: list) -> str:
    """生成下周建议列表 HTML"""
    if not suggestions:
        return '<div class="suggestion-item">保持当前节奏，继续加油！</div>'
    return "".join(
        f'<div class="suggestion-item">💡 {s}</div>'
        for s in suggestions
    )


# ── 节点函数 ──────────────────────────────────────────────────────────────────

async def calculate_metrics_node(state: ReportState) -> Dict:
    """纯计算节点：按科目汇总完成情况，不调用 LLM"""
    total_plan = state.get("total_plan", [])
    weekly_completed = state.get("weekly_completed", [])

    # 按科目汇总计划数据
    plan_by_subject: Dict[str, Dict] = {}
    for task in total_plan:
        subject = task.get("subject") or "其他"
        if subject not in plan_by_subject:
            plan_by_subject[subject] = {"planned": 0, "planned_minutes": 0}
        plan_by_subject[subject]["planned"] += 1
        plan_by_subject[subject]["planned_minutes"] += task.get("estimated_minutes", 0)

    # 按科目汇总完成数据
    completed_by_subject: Dict[str, Dict] = {}
    for task in weekly_completed:
        subject = task.get("subject") or "其他"
        if subject not in completed_by_subject:
            completed_by_subject[subject] = {"completed": 0, "completed_minutes": 0}
        completed_by_subject[subject]["completed"] += 1
        completed_by_subject[subject]["completed_minutes"] += task.get("estimated_minutes", 0)

    # 合并各科统计
    all_subjects = set(list(plan_by_subject.keys()) + list(completed_by_subject.keys()))
    subject_stats = []
    for subject in sorted(all_subjects):
        planned = plan_by_subject.get(subject, {}).get("planned", 0)
        planned_minutes = plan_by_subject.get(subject, {}).get("planned_minutes", 0)
        completed = completed_by_subject.get(subject, {}).get("completed", 0)
        completed_minutes = completed_by_subject.get(subject, {}).get("completed_minutes", 0)
        rate = round(completed / planned * 100, 1) if planned > 0 else 0.0
        subject_stats.append({
            "subject": subject,
            "planned": planned,
            "completed": completed,
            "rate": rate,
            "planned_minutes": planned_minutes,
            "completed_minutes": completed_minutes,
        })

    total_planned = len(total_plan)
    total_completed = len(weekly_completed)
    total_rate = round(total_completed / total_planned * 100, 1) if total_planned > 0 else 0.0
    estimated_minutes_total = sum(t.get("estimated_minutes", 0) for t in total_plan)
    completed_minutes = sum(t.get("estimated_minutes", 0) for t in weekly_completed)

    # 打卡天数：weekly_completed 中有记录的不重复日期数
    unique_dates = {t.get("task_date", "") for t in weekly_completed if t.get("task_date")}
    streak_days = len(unique_dates)

    return {
        "subject_stats": subject_stats,
        "total_planned": total_planned,
        "total_completed": total_completed,
        "total_rate": total_rate,
        "estimated_minutes_total": estimated_minutes_total,
        "completed_minutes": completed_minutes,
        "streak_days": streak_days,
    }


async def analyze_performance_node(state: ReportState) -> Dict:
    """LLM 节点：分析表现亮点和问题，输出 JSON"""
    try:
        from app.llm import get_chat_model

        subject_stats_text = "\n".join(
            f"  - {s['subject']}：计划 {s['planned']} 项，完成 {s['completed']} 项，完成率 {s['rate']}%"
            for s in state.get("subject_stats", [])
        ) or "  - 暂无科目数据"

        prompt = ANALYZE_PROMPT.format(
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            streak_days=state.get("streak_days", 0),
            subject_stats_text=subject_stats_text,
        )

        llm = get_chat_model()
        response = await llm.ainvoke([
            SystemMessage(content="只输出JSON格式数据，不要任何说明文字或代码块标记。"),
            HumanMessage(content=prompt),
        ])
        text = response.content if isinstance(response.content, str) else str(response.content[0])
        result = _parse_json_response(text)
        return {
            "highlights": result.get("highlights", []),
            "issues": result.get("issues", []),
        }
    except Exception as e:
        logger.error(f"analyze_performance_node error: {e}")
        return {"highlights": [], "issues": []}


async def generate_html_report_node(state: ReportState) -> Dict:
    """LLM 节点：生成风趣点评+建议，Python 组装完整 HTML 周报"""
    try:
        from app.llm import get_chat_model

        completed_hours = round(state.get("completed_minutes", 0) / 60, 1)
        highlights = state.get("highlights", [])
        issues = state.get("issues", [])

        prompt = REPORT_TEXT_PROMPT.format(
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            completed_hours=completed_hours,
            streak_days=state.get("streak_days", 0),
            highlights="、".join(highlights) if highlights else "无",
            issues="、".join(issues) if issues else "无",
        )

        llm = get_chat_model()
        response = await llm.ainvoke([
            SystemMessage(content="只输出JSON格式数据，不要任何说明文字或代码块标记。"),
            HumanMessage(content=prompt),
        ])
        text = response.content if isinstance(response.content, str) else str(response.content[0])
        result = _parse_json_response(text)
        comment = result.get("comment", "本周表现不错，继续保持！")
        suggestions = result.get("suggestions", ["保持每日打卡", "及时复习薄弱科目", "做好计划执行"])

        # 组装 HTML
        html_content = HTML_TEMPLATE.format(
            week_start=state.get("week_start", ""),
            week_end=state.get("week_end", ""),
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            completed_hours=completed_hours,
            streak_days=state.get("streak_days", 0),
            subject_rows=_build_subject_rows(state.get("subject_stats", [])),
            highlights_html=_build_list_html(highlights),
            issues_html=_build_list_html(issues),
            comment=comment,
            suggestions_html=_build_suggestions_html(suggestions),
        )

        # 纯文字摘要（降级备用）
        summary = f"本周完成率 {state.get('total_rate', 0)}%，完成 {state.get('total_completed', 0)}/{state.get('total_planned', 0)} 项任务，学习 {completed_hours} 小时，打卡 {state.get('streak_days', 0)} 天。"

        return {"html_content": html_content, "summary": summary}
    except Exception as e:
        logger.error(f"generate_html_report_node error: {e}")
        return {
            "html_content": "",
            "summary": "周报生成失败，请稍后重试。",
            "error": str(e),
        }


async def save_report_node(state: ReportState) -> Dict:
    """工具节点：将周报保存到数据库"""
    try:
        from app.tools.db_tools import save_weekly_report, get_active_plan

        plan = await get_active_plan.ainvoke({"user_id": state["user_id"]})
        plan_id = plan.get("plan_id") if plan else ""

        result = await save_weekly_report.ainvoke({
            "user_id": state["user_id"],
            "plan_id": plan_id or "",
            "week_start": state["week_start"],
            "week_end": state.get("week_end", ""),
            "average_rate": state.get("total_rate", 0),
            "summary": state.get("html_content") or state.get("summary", ""),
            "suggestions": json.dumps([], ensure_ascii=False),
            "daily_rates": json.dumps(state.get("subject_stats", []), ensure_ascii=False),
        })
        return {"report_id": result.get("report_id")}
    except Exception as e:
        logger.error(f"save_report_node error: {e}")
        return {"report_id": None, "error": str(e)}
