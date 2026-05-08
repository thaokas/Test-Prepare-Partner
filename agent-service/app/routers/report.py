"""
周报相关API路由
"""
from fastapi import APIRouter, HTTPException
from datetime import date, timedelta

from app.agents.report import report_graph
from app.routers.schemas import WeeklyReportRequest, WeeklyReportResponse

router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("/weekly", response_model=WeeklyReportResponse)
async def generate_weekly_report(request: WeeklyReportRequest):
    """生成周报（传入本周计划任务列表 + 已完成任务列表，LLM 生成 HTML 周报）"""
    week_end = request.week_end or str(
        date.fromisoformat(request.week_start) + timedelta(days=6)
    )

    initial_state = {
        "user_id": request.user_id,
        "week_start": request.week_start,
        "week_end": week_end,
        "total_plan": request.total_plan,
        "weekly_completed": request.weekly_completed,
        # 以下由各节点填充
        "subject_stats": [],
        "total_planned": 0,
        "total_completed": 0,
        "total_rate": 0.0,
        "estimated_minutes_total": 0,
        "completed_minutes": 0,
        "streak_days": 0,
        "highlights": [],
        "issues": [],
        "html_content": "",
        "summary": "",
        "report_id": None,
        "error": None,
    }

    result = await report_graph.ainvoke(initial_state)

    if result.get("error") and not result.get("html_content"):
        raise HTTPException(status_code=500, detail=result["error"])

    return WeeklyReportResponse(
        report_id=result.get("report_id"),
        user_id=request.user_id,
        week_start=request.week_start,
        week_end=week_end,
        total_rate=result.get("total_rate", 0.0),
        html_content=result.get("html_content", ""),
        summary=result.get("summary", ""),
    )
