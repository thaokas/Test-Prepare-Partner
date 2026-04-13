"""
定时任务调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def send_reminder_job():
    """每日提醒任务（21:00 和 22:00 触发）"""
    logger.info(f"[{datetime.now()}] 执行每日提醒任务")
    try:
        from app.agents.reminder import reminder_graph
        from app.tools.db_tools import get_users_for_reminder

        trigger_time = datetime.now().strftime("%H:%M")
        users = await get_users_for_reminder.ainvoke({"trigger_time": trigger_time})

        for user in users:
            initial_state = {
                "user_id": user.get("id"),
                "mode": user.get("reminder_mode", 1),
                "trigger_time": trigger_time,
                "incomplete_tasks": [],
                "remaining_count": 0,
                "recent_completion_rate": 0.0,
                "streak_days": 0,
                "strategy": "",
                "tone": "",
                "content": "",
                "error": None,
            }
            result = await reminder_graph.ainvoke(initial_state)
            if result.get("content"):
                logger.info(f"Reminder for user {user.get('id')}: {result['content'][:50]}...")
    except Exception as e:
        logger.error(f"send_reminder_job error: {e}")


async def generate_weekly_report_job():
    """周报生成任务（每周日 22:00 触发）"""
    logger.info(f"[{datetime.now()}] 执行周报生成任务")
    try:
        from app.agents.report import report_graph
        from app.tools.db_tools import get_users_for_reminder
        from datetime import date, timedelta

        today = date.today()
        week_start = str(today - timedelta(days=today.weekday()))
        week_end = str(date.fromisoformat(week_start) + timedelta(days=6))

        # 复用 get_users_for_reminder 获取活跃用户
        users = await get_users_for_reminder.ainvoke({"trigger_time": "22:00"})

        for user in users:
            initial_state = {
                "user_id": user.get("id"),
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
            await report_graph.ainvoke(initial_state)
            logger.info(f"Weekly report generated for user {user.get('id')}")
    except Exception as e:
        logger.error(f"generate_weekly_report_job error: {e}")


def setup_scheduler():
    """配置定时任务"""
    # 温柔模式：22:00
    scheduler.add_job(
        send_reminder_job,
        CronTrigger(hour=22, minute=0),
        id="reminder_22",
        name="提醒任务22:00",
        replace_existing=True,
    )
    # 强化模式：21:00 额外触发
    scheduler.add_job(
        send_reminder_job,
        CronTrigger(hour=21, minute=0),
        id="reminder_21",
        name="提醒任务21:00",
        replace_existing=True,
    )
    # 周报：每周日 22:00
    scheduler.add_job(
        generate_weekly_report_job,
        CronTrigger(day_of_week="sun", hour=22, minute=0),
        id="weekly_report",
        name="周报生成任务",
        replace_existing=True,
    )
    logger.info("定时任务调度器配置完成")


def start_scheduler():
    setup_scheduler()
    scheduler.start()
    logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("定时任务调度器已关闭")
