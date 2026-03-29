"""
定时任务调度器

使用APScheduler实现定时任务：
- 每日提醒任务
- 周报生成任务
- 连续打卡检查任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 全局调度器
scheduler = AsyncIOScheduler()


async def daily_reminder_job():
    """
    每日提醒任务
    每天22:00触发，为未完成任务的用户发送提醒
    """
    logger.info(f"[{datetime.now()}] 执行每日提醒任务")

    # TODO: 查询所有进行中的计划
    # TODO: 检查今日是否有未完成任务
    # TODO: 根据用户模式发送提醒
    # TODO: 调用 reminder_graph 生成提醒内容

    print("每日提醒任务执行 - 待实现数据库查询")


async def weekly_report_job():
    """
    周报生成任务
    每周日22:00触发，生成并发送周报
    """
    logger.info(f"[{datetime.now()}] 执行周报生成任务")

    # TODO: 查询所有用户
    # TODO: 聚合本周数据
    # TODO: 生成周报
    # TODO: 发送给用户

    print("周报生成任务执行 - 待实现")


async def streak_checker_job():
    """
    连续打卡检查任务
    每天00:00触发，检查昨天是否有打卡，更新连续打卡状态
    """
    logger.info(f"[{datetime.now()}] 执行连续打卡检查任务")

    # TODO: 查询昨天未打卡的用户
    # TODO: 重置current_streak
    # TODO: 发送关怀消息

    print("连续打卡检查任务执行 - 待实现")


def setup_scheduler():
    """配置并启动调度器"""

    # 每日提醒任务：每天22:00
    scheduler.add_job(
        daily_reminder_job,
        CronTrigger(hour=22, minute=0),
        id="daily_reminder",
        name="每日提醒任务",
        replace_existing=True
    )

    # 周报生成任务：每周日22:00
    scheduler.add_job(
        weekly_report_job,
        CronTrigger(day_of_week="sun", hour=22, minute=0),
        id="weekly_report",
        name="周报生成任务",
        replace_existing=True
    )

    # 连续打卡检查任务：每天00:00
    scheduler.add_job(
        streak_checker_job,
        CronTrigger(hour=0, minute=0),
        id="streak_checker",
        name="连续打卡检查任务",
        replace_existing=True
    )

    logger.info("定时任务调度器配置完成")


def start_scheduler():
    """启动调度器"""
    setup_scheduler()
    scheduler.start()
    logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    """关闭调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已关闭")