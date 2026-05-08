"""
提醒相关API路由
"""
from fastapi import APIRouter, HTTPException

from app.agents.reminder import reminder_graph
from app.tools.db_tools import get_reminder_settings, update_reminder_settings
from app.routers.schemas import (
    ReminderSettingsRequest,
    ReminderSettingsResponse,
    ReminderGenerateRequest,
    ReminderGenerateResponse,
)

router = APIRouter(prefix="/api/reminder", tags=["reminder"])


@router.get("/settings/{user_id}", response_model=ReminderSettingsResponse)
async def get_reminder_settings_endpoint(user_id: str):
    """获取用户提醒设置"""
    settings = await get_reminder_settings.ainvoke({"user_id": user_id})
    return ReminderSettingsResponse(
        mode=settings.get("mode", 1),
        custom_times=settings.get("custom_times", []),
        monking_interval=settings.get("monking_interval", 30),
        is_active=settings.get("is_active", True),
    )


@router.put("/settings/{user_id}", response_model=ReminderSettingsResponse)
async def update_reminder_settings_endpoint(user_id: str, request: ReminderSettingsRequest):
    """更新用户提醒设置"""
    await update_reminder_settings.ainvoke({
        "user_id": user_id,
        "mode": request.mode,
        "custom_times": request.custom_times,
        "monking_interval": request.monking_interval,
    })
    return ReminderSettingsResponse(
        mode=request.mode,
        custom_times=request.custom_times,
        monking_interval=request.monking_interval,
        is_active=True,
    )


@router.post("/generate", response_model=ReminderGenerateResponse)
async def generate_reminder(request: ReminderGenerateRequest):
    """生成提醒内容（LLM驱动：根据任务进度和严格模式生成个性化提醒文案）"""
    initial_state = {
        "today_total_tasks": request.today_total_tasks,
        "today_incomplete_tasks": request.today_incomplete_tasks,
        "exam_total_tasks": request.exam_total_tasks,
        "exam_completed_tasks": request.exam_completed_tasks,
        "elapsed_study_days": request.elapsed_study_days,
        "total_study_days": request.total_study_days,
        "strictness_mode": request.strictness_mode,
        "current_time": None,
        "content": "",
        "error": None,
    }

    result = await reminder_graph.ainvoke(initial_state)

    if result.get("error") and not result.get("content"):
        raise HTTPException(status_code=500, detail=result["error"])

    return ReminderGenerateResponse(content=result.get("content", ""))
