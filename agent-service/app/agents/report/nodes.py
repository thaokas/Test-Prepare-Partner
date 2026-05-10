"""周报生成Agent节点函数"""
import json
import logging
from typing import Dict
from datetime import date, timedelta

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
        text = parts[1].lstrip("json").lstrip("JSON").strip()
    return json.loads(text)


def _compute_grade(rate: float) -> str:
    """根据完成率计算等级"""
    if rate >= 95:
        return "S"
    elif rate >= 80:
        return "A"
    elif rate >= 60:
        return "B"
    elif rate >= 30:
        return "C"
    else:
        return "D"


def _compute_report_title(start_str: str, end_str: str) -> str:
    """根据日期范围生成报告标题"""
    try:
        s = date.fromisoformat(start_str)
        e = date.fromisoformat(end_str)
        days = (e - s).days + 1
        if days == 1:
            return f"{s.month}月{s.day}日 学习报告"
        elif days <= 7:
            return f"{days}日学习报告"
        elif days <= 14:
            return f"双周学习报告"
        else:
            return f"学习阶段报告"
    except Exception:
        return "学习报告"


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
    """生成后续建议列表 HTML"""
    if not suggestions:
        return '<div class="suggestion-item">保持当前节奏，继续加油！</div>'
    return "".join(
        f'<div class="suggestion-item">💡 {s}</div>'
        for s in suggestions
    )


def _build_completed_tasks_html(weekly_completed: list) -> str:
    """生成已完成任务明细 HTML，按日期分组"""
    if not weekly_completed:
        return '<div class="empty-hint" style="text-align:center;padding:16px;">期间暂无已完成任务</div>'

    # 按日期分组
    by_date: Dict[str, list] = {}
    for t in weekly_completed:
        d = t.get("task_date", "未知日期")
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(t)

    html_parts = []
    for d in sorted(by_date.keys()):
        tasks = by_date[d]
        html_parts.append(f'<div style="color:#999;font-size:12px;margin:8px 0 4px;">📅 {d}（{len(tasks)}项）</div>')
        for t in tasks:
            subject = t.get("subject", "未知")
            minutes = t.get("estimated_minutes", 0)
            html_parts.append(
                f'<div class="task-row">'
                f'<span class="task-subject">📖 {subject}</span>'
                f'<span style="color:#999;font-size:12px;">{minutes}min</span>'
                f'</div>'
            )
    return "\n".join(html_parts)


def _build_daily_breakdown_html(daily_breakdown: list) -> str:
    """生成每日进度明细 HTML（计划 vs 实际完成）"""
    if not daily_breakdown:
        return '<div class="empty-hint" style="text-align:center;padding:16px;">暂无每日数据</div>'

    weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]
    rows = []
    for entry in daily_breakdown:
        d = entry.get("date", "")
        planned = entry.get("planned_count", 0)
        completed = entry.get("completed_count", 0)
        rate = entry.get("rate", 0)
        # Parse weekday
        try:
            from datetime import date as dt_date
            parsed = dt_date.fromisoformat(d)
            wd = weekday_labels[parsed.weekday()]
            label = f"{parsed.month}月{parsed.day}日 周{wd}"
        except Exception:
            label = d

        if rate >= 80:
            bar_color = "#4CAF50"
        elif rate >= 50:
            bar_color = "#FF9800"
        elif planned > 0:
            bar_color = "#F44336"
        else:
            bar_color = "#ddd"

        rows.append(
            f'<div style="margin-bottom:12px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
            f'<span style="font-size:13px;color:#444;">{label}</span>'
            f'<span style="font-size:12px;color:#999;">完成 {completed}/{planned} · {rate}%</span>'
            f'</div>'
            f'<div style="background:#f0f0f0;border-radius:999px;height:6px;overflow:hidden;">'
            f'<div style="height:100%;border-radius:999px;background:{bar_color};width:{rate}%;"></div>'
            f'</div>'
            f'</div>'
        )
    return "\n".join(rows)


def _build_daily_breakdown_text(daily_breakdown: list) -> str:
    """生成每日进度的纯文字摘要"""
    if not daily_breakdown:
        return "暂无每日数据"

    lines = []
    for entry in daily_breakdown:
        d = entry.get("date", "")
        planned = entry.get("planned_count", 0)
        completed = entry.get("completed_count", 0)
        rate = entry.get("rate", 0)
        lines.append(f"{d}：计划 {planned} 项，完成 {completed} 项（{rate}%）")
    return "\n".join(lines)


def _build_completed_tasks_text(weekly_completed: list) -> str:
    """生成已完成任务的纯文字明细"""
    if not weekly_completed:
        return "期间无已完成任务"

    by_date: Dict[str, list] = {}
    for t in weekly_completed:
        d = t.get("task_date", "未知日期")
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(t)

    lines = []
    for d in sorted(by_date.keys()):
        tasks = by_date[d]
        subjects = [t.get("subject", "未知") for t in tasks]
        total_min = sum(t.get("estimated_minutes", 0) for t in tasks)
        lines.append(f"{d}：完成 {', '.join(subjects)}，共 {total_min} 分钟")
    return "\n".join(lines)


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

    # 每日进度明细：按日期分组计划 vs 完成
    daily_plan_by_date: Dict[str, Dict] = {}
    for task in total_plan:
        d = task.get("task_date", "")
        if d not in daily_plan_by_date:
            daily_plan_by_date[d] = {"planned_count": 0, "planned_minutes": 0, "completed_count": 0, "completed_minutes": 0}
        daily_plan_by_date[d]["planned_count"] += 1
        daily_plan_by_date[d]["planned_minutes"] += task.get("estimated_minutes", 0)

    for task in weekly_completed:
        d = task.get("task_date", "")
        if d not in daily_plan_by_date:
            daily_plan_by_date[d] = {"planned_count": 0, "planned_minutes": 0, "completed_count": 0, "completed_minutes": 0}
        daily_plan_by_date[d]["completed_count"] += 1
        daily_plan_by_date[d]["completed_minutes"] += task.get("estimated_minutes", 0)

    daily_breakdown = []
    for d in sorted(daily_plan_by_date.keys()):
        day = daily_plan_by_date[d]
        day_rate = round(day["completed_count"] / day["planned_count"] * 100, 1) if day["planned_count"] > 0 else 0.0
        daily_breakdown.append({
            "date": d,
            "planned_count": day["planned_count"],
            "completed_count": day["completed_count"],
            "planned_minutes": day["planned_minutes"],
            "completed_minutes": day["completed_minutes"],
            "rate": day_rate,
        })

    # 已完成任务明细
    completed_tasks_detail = _build_completed_tasks_text(weekly_completed)

    # 报告标题和等级
    week_start = state.get("week_start", "")
    week_end = state.get("week_end", "")
    report_title = _compute_report_title(week_start, week_end)
    grade = _compute_grade(total_rate)

    return {
        "daily_breakdown": daily_breakdown,
        "subject_stats": subject_stats,
        "total_planned": total_planned,
        "total_completed": total_completed,
        "total_rate": total_rate,
        "estimated_minutes_total": estimated_minutes_total,
        "completed_minutes": completed_minutes,
        "streak_days": streak_days,
        "completed_tasks_detail": completed_tasks_detail,
        "report_title": report_title,
        "grade": grade,
    }


async def analyze_performance_node(state: ReportState) -> Dict:
    """LLM 节点：分析表现亮点和问题，输出 JSON"""
    try:
        from app.llm import get_chat_model

        subject_stats_text = "\n".join(
            f"  - {s['subject']}：计划 {s['planned']} 项，完成 {s['completed']} 项，完成率 {s['rate']}%"
            for s in state.get("subject_stats", [])
        ) or "  - 暂无科目数据"

        daily_breakdown_text = _build_daily_breakdown_text(state.get("daily_breakdown", []))

        prompt = ANALYZE_PROMPT.format(
            start_date=state.get("week_start", ""),
            end_date=state.get("week_end", ""),
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            streak_days=state.get("streak_days", 0),
            subject_stats_text=subject_stats_text,
            completed_tasks_detail=state.get("completed_tasks_detail", ""),
            daily_breakdown_text=daily_breakdown_text,
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
    """LLM 节点：生成点评+建议，Python 组装完整 HTML 报告"""
    try:
        from app.llm import get_chat_model

        completed_hours = round(state.get("completed_minutes", 0) / 60, 1)
        highlights = state.get("highlights", [])
        issues = state.get("issues", [])

        prompt = REPORT_TEXT_PROMPT.format(
            start_date=state.get("week_start", ""),
            end_date=state.get("week_end", ""),
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            completed_hours=completed_hours,
            streak_days=state.get("streak_days", 0),
            highlights="、".join(highlights) if highlights else "无",
            issues="、".join(issues) if issues else "无",
            daily_breakdown_text=_build_daily_breakdown_text(state.get("daily_breakdown", [])),
        )

        llm = get_chat_model()
        response = await llm.ainvoke([
            SystemMessage(content="只输出JSON格式数据，不要任何说明文字或代码块标记。"),
            HumanMessage(content=prompt),
        ])
        text = response.content if isinstance(response.content, str) else str(response.content[0])
        result = _parse_json_response(text)
        comment = result.get("comment", "这段时间的表现值得总结，继续加油！")
        suggestions = result.get("suggestions", ["保持每日打卡", "及时复习薄弱科目", "做好计划执行"])

        # 组装 HTML
        html_content = HTML_TEMPLATE.format(
            report_title=state.get("report_title", "学习报告"),
            grade=state.get("grade", "B"),
            start_date=state.get("week_start", ""),
            end_date=state.get("week_end", ""),
            total_rate=state.get("total_rate", 0),
            total_completed=state.get("total_completed", 0),
            total_planned=state.get("total_planned", 0),
            completed_hours=completed_hours,
            streak_days=state.get("streak_days", 0),
            daily_breakdown_html=_build_daily_breakdown_html(state.get("daily_breakdown", [])),
            subject_rows=_build_subject_rows(state.get("subject_stats", [])),
            completed_tasks_html=_build_completed_tasks_html(state.get("weekly_completed", [])),
            highlights_html=_build_list_html(highlights),
            issues_html=_build_list_html(issues),
            comment=comment,
            suggestions_html=_build_suggestions_html(suggestions),
        )

        # 纯文字摘要（降级备用）
        summary = (
            f"{state.get('report_title', '学习报告')} | "
            f"完成率 {state.get('total_rate', 0)}%，"
            f"完成 {state.get('total_completed', 0)}/{state.get('total_planned', 0)} 项任务，"
            f"学习 {completed_hours} 小时，打卡 {state.get('streak_days', 0)} 天。"
            f"等级：{state.get('grade', 'B')}。"
        )

        return {"html_content": html_content, "summary": summary, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"generate_html_report_node error: {e}")
        return {
            "html_content": "",
            "summary": "报告生成失败，请稍后重试。",
            "error": str(e),
        }


async def save_report_node(state: ReportState) -> Dict:
    """工具节点：将报告保存到数据库"""
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
            "suggestions": json.dumps(state.get("suggestions", []), ensure_ascii=False),
            "daily_rates": json.dumps(state.get("subject_stats", []), ensure_ascii=False),
        })
        return {"report_id": result.get("report_id")}
    except Exception as e:
        logger.error(f"save_report_node error: {e}")
        return {"report_id": None, "error": str(e)}
