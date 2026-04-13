"""
提醒设置相关API路由（新增）
"""
from fastapi import APIRouter, HTTPException

from app.routers.schemas import ReminderSettingsRequest, ReminderSettingsResponse

router = APIRouter(prefix="/api/reminder", tags=["reminder"])


@router.get("/settings/{user_id}", response_model=ReminderSettingsResponse)
async def get_reminder_settings(user_id: str):
    """获取用户提醒设置"""
    from app.tools.db_tools import get_reminder_settings
    settings = await get_reminder_settings.ainvoke({"user_id": user_id})
    return ReminderSettingsResponse(
        mode=settings.get("mode", 1),
        custom_times=settings.get("custom_times", []),
        monking_interval=settings.get("monking_interval", 30),
        is_active=settings.get("is_active", True),
    )


@router.put("/settings/{user_id}", response_model=ReminderSettingsResponse)
async def update_reminder_settings(user_id: str, request: ReminderSettingsRequest):
    """更新用户提醒设置"""
    # TODO: 实现数据库更新
    return ReminderSettingsResponse(
        mode=request.mode,
        custom_times=request.custom_times,
        monking_interval=request.monking_interval,
        is_active=True,
    )
