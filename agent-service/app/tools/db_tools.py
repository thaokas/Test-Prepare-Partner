"""
数据库工具层 - 供Agent调用的LangChain工具
所有工具返回Dict/List，便于LLM解析
"""
from typing import Optional, List, Dict
from datetime import date, datetime

from langchain.tools import tool


@tool
async def get_user_profile(user_id: str) -> Dict:
    """获取用户备考档案（基础水平、目标考试、薄弱科目等）

    Args:
        user_id: 用户ID

    Returns:
        包含用户备考信息的字典
    """
    # TODO: 实现数据库查询
    return {
        "user_id": user_id,
        "username": None,
        "foundation_level": 0,
        "target_exam": None,
        "weak_subjects": [],
        "current_streak": 0,
        "reminder_mode": 1
    }


@tool
async def get_active_plan(user_id: str) -> Optional[Dict]:
    """获取用户当前进行中的备考计划

    Args:
        user_id: 用户ID

    Returns:
        计划信息字典，无计划时返回None
    """
    # TODO: 实现数据库查询
    return None


@tool
async def create_study_plan(
    user_id: str,
    exam_name: str,
    exam_type: str,
    exam_date: str,
    daily_hours: float,
    tasks: List[Dict]
) -> Dict:
    """创建新的备考计划并批量插入任务

    Args:
        user_id: 用户ID
        exam_name: 考试名称
        exam_type: 考试类型
        exam_date: 考试日期（YYYY-MM-DD）
        daily_hours: 每日学习时长
        tasks: 任务列表

    Returns:
        包含plan_id的字典
    """
    # TODO: 实现数据库插入
    return {"plan_id": None, "total_tasks": len(tasks)}


@tool
async def get_today_tasks(user_id: str) -> List[Dict]:
    """获取用户今日任务列表

    Args:
        user_id: 用户ID

    Returns:
        今日任务列表
    """
    # TODO: 实现数据库查询
    return []


@tool
async def match_tasks_by_keywords(user_id: str, keywords: List[str]) -> List[Dict]:
    """根据关键词匹配用户今日任务（用于打卡解析）

    Args:
        user_id: 用户ID
        keywords: 从打卡内容中提取的关键词列表

    Returns:
        匹配到的任务列表
    """
    # TODO: 实现关键词匹配查询
    return []


@tool
async def update_task_status(task_id: str, status: int) -> bool:
    """更新任务状态

    Args:
        task_id: 任务ID
        status: 状态码（0-待完成 1-进行中 2-已完成）

    Returns:
        更新是否成功
    """
    # TODO: 实现数据库更新
    return True


@tool
async def create_checkin_record(
    user_id: str,
    plan_id: str,
    completed_tasks: List[str],
    total_tasks: int,
    completion_rate: float,
    content: str
) -> Dict:
    """创建打卡记录

    Args:
        user_id: 用户ID
        plan_id: 计划ID
        completed_tasks: 已完成任务ID列表
        total_tasks: 今日总任务数
        completion_rate: 完成率（0-1）
        content: 打卡内容文本

    Returns:
        包含checkin_id的字典
    """
    # TODO: 实现数据库插入
    return {"checkin_id": None, "completion_rate": completion_rate}


@tool
async def get_checkin_history(user_id: str, days: int = 7) -> List[Dict]:
    """获取用户最近N天的打卡历史

    Args:
        user_id: 用户ID
        days: 查询天数（默认7天）

    Returns:
        打卡记录列表
    """
    # TODO: 实现数据库查询
    return []


@tool
async def get_user_streak(user_id: str) -> int:
    """获取用户当前连续打卡天数

    Args:
        user_id: 用户ID

    Returns:
        连续打卡天数
    """
    # TODO: 实现数据库查询
    return 0


@tool
async def update_user_streak(user_id: str, new_streak: int) -> bool:
    """更新用户连续打卡天数

    Args:
        user_id: 用户ID
        new_streak: 新的连续天数

    Returns:
        更新是否成功
    """
    # TODO: 实现数据库更新
    return True


@tool
async def get_reminder_settings(user_id: str) -> Dict:
    """获取用户提醒模式设置

    Args:
        user_id: 用户ID

    Returns:
        提醒设置字典
    """
    # TODO: 实现数据库查询
    return {
        "mode": 1,
        "custom_times": [],
        "monking_interval": 30,
        "is_active": True
    }


@tool
async def get_users_for_reminder(trigger_time: str) -> List[Dict]:
    """获取当前时间需要发送提醒的用户列表

    Args:
        trigger_time: 触发时间（HH:MM格式）

    Returns:
        需要提醒的用户列表
    """
    # TODO: 实现数据库查询
    return []


@tool
async def get_weekly_data(user_id: str, week_start: str) -> Dict:
    """获取用户指定周的学习数据，用于生成周报

    Args:
        user_id: 用户ID
        week_start: 周一日期（YYYY-MM-DD）

    Returns:
        包含每日打卡数据的字典
    """
    # TODO: 实现数据库查询
    return {
        "daily_checkins": [],
        "total_tasks": 0,
        "completed_tasks": 0
    }


@tool
async def save_weekly_report(
    user_id: str,
    plan_id: str,
    week_start: str,
    week_end: str,
    average_rate: float,
    summary: str,
    suggestions: str,
    daily_rates: str
) -> Dict:
    """保存周报记录

    Args:
        user_id: 用户ID
        plan_id: 计划ID
        week_start: 周开始日期
        week_end: 周结束日期
        average_rate: 平均完成率
        summary: LLM生成的总结
        suggestions: LLM生成的建议（JSON字符串）
        daily_rates: 每日完成率（JSON字符串）

    Returns:
        包含report_id的字典
    """
    # TODO: 实现数据库插入
    return {"report_id": None}


DB_TOOLS = [
    get_user_profile,
    get_active_plan,
    create_study_plan,
    get_today_tasks,
    match_tasks_by_keywords,
    update_task_status,
    create_checkin_record,
    get_checkin_history,
    get_user_streak,
    update_user_streak,
    get_reminder_settings,
    get_users_for_reminder,
    get_weekly_data,
    save_weekly_report,
]
