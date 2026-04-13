"""
周报相关API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date, timedelta

from app.agents.report import report_graph
from app.routers.schemas import WeeklyReportResponse

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/weekly/{user_id}", response_model=WeeklyReportResponse)
async def get_weekly_report(user_id: str, week_start: Optional[str] = None):
    """获取周报（LLM驱动：智能分析本周学习表现）"""
    if week_start is None:
        today = date.today()
        week_start = str(today - timedelta(days=today.weekday()))

    week_end = str(date.fromisoformat(week_start) + timedelta(days=6))

    initial_state = {
        "user_id": user_id,
        "week_start": week_start,
        "week_end": week_end,
        "daily_checkins": [],
        "daily_rates": [],
        "average_rate": 0.0,
        "week_over_week": 0.0,
        "current_streak": 0,
        "best_study_time": None,
        "highlights": [],
        "issues": [],
        "summary": "",
        "suggestions": [],
        "report_id": None,
        "error": None,
    }

    result = await report_graph.ainvoke(initial_state)

    return WeeklyReportResponse(
        report_id=result.get("report_id"),
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        average_rate=result.get("average_rate", 0.0),
        summary=result.get("summary", "本周数据暂无"),
        suggestions=result.get("suggestions", []),
    )
