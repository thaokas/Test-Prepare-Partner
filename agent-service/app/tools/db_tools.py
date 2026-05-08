"""
DB工具（存根）—— Agent 不直接与数据库交互，这些工具返回占位响应。
实际数据库操作由后端 Java 服务通过 AgentClientService 完成。
"""
from typing import Dict, List, Any

from langchain.tools import tool


@tool
async def get_user_profile(user_id: str) -> Dict:
    """获取用户配置信息（存根）"""
    return {"user_id": user_id, "name": "", "daily_hours": 2.0}


@tool
async def get_active_plan(user_id: str) -> Dict:
    """获取用户当前激活的备考计划（存根）"""
    return {"plan_id": None, "exam_name": "", "exam_type": "", "exam_date": ""}


@tool
async def create_study_plan(
    user_id: str,
    exam_name: str,
    exam_type: str,
    exam_date: str,
    daily_hours: float,
    tasks: List[Dict],
) -> Dict:
    """创建备考计划（存根，不写库，仅返回占位 plan_id）"""
    import uuid
    return {
        "plan_id": str(uuid.uuid4()),
        "total_tasks": len(tasks),
    }


@tool
async def get_today_tasks(user_id: str) -> List[Dict]:
    """获取用户今日任务列表（存根）"""
    return []


@tool
async def get_reminder_settings(user_id: str) -> Dict:
    """获取用户提醒设置（存根）"""
    return {
        "mode": 1,
        "custom_times": [],
        "monking_interval": 30,
        "is_active": True,
    }


@tool
async def update_reminder_settings(
    user_id: str,
    mode: int,
    custom_times: List[str],
    monking_interval: int,
) -> Dict:
    """更新用户提醒设置（存根，不写库）"""
    return {"success": True}


@tool
async def save_weekly_report(
    user_id: str,
    plan_id: str,
    week_start: str,
    week_end: str,
    average_rate: float,
    summary: str,
    suggestions: str,
    daily_rates: str,
) -> Dict:
    """保存周报（存根，不写库，仅返回占位 report_id）"""
    import uuid
    return {"report_id": str(uuid.uuid4())}


DB_TOOLS = [
    get_user_profile,
    get_active_plan,
    create_study_plan,
    get_today_tasks,
    get_reminder_settings,
    update_reminder_settings,
    save_weekly_report,
]
