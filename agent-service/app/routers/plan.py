"""
计划相关API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.agents.plan_generation import plan_generation_graph
from app.routers.schemas import PlanGenerateRequest, PlanGenerateResponse, TodayTasksResponse

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.post("/generate", response_model=PlanGenerateResponse)
async def generate_plan(request: PlanGenerateRequest):
    """生成备考计划（LLM驱动）"""
    initial_state = {
        "user_id": request.user_id,
        "exam_name": request.exam_name,
        "exam_type": request.exam_type,
        "exam_date": str(request.exam_date),
        "daily_hours": request.daily_hours,
        "foundation_level": request.foundation_level,
        "weak_subjects": request.weak_subjects or [],
        "exam_info": {},
        "days_remaining": 0,
        "current_phase": 1,
        "phase_name": "",
        "tasks": [],
        "plan_id": None,
        "message": "",
        "error": None,
    }

    result = await plan_generation_graph.ainvoke(initial_state)

    if result.get("error") and not result.get("plan_id"):
        raise HTTPException(status_code=500, detail=result["error"])

    return PlanGenerateResponse(
        plan_id=result.get("plan_id"),
        total_tasks=len(result.get("tasks", [])),
        message=result.get("message", "计划生成完成"),
        tasks=result.get("tasks", []),
    )


@router.get("/today")
async def get_today_tasks(user_id: str):
    """获取今日任务"""
    from app.tools.db_tools import get_today_tasks as _get_today_tasks
    tasks = await _get_today_tasks.ainvoke({"user_id": user_id})
    return {"tasks": tasks, "total": len(tasks)}
