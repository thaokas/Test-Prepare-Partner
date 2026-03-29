"""
周报相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, timedelta

from app.models.database import get_db
from app.models.user import User
from app.models.checkin import Checkin
from app.routers.schemas import WeeklyReportResponse

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取周报
    """
    # 检查用户
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 计算本周日期范围
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    week_end = week_start + timedelta(days=6)  # 本周日

    # 上周日期范围
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)

    # 获取本周打卡记录
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.user_id == user_id,
                Checkin.checkin_date >= week_start,
                Checkin.checkin_date <= week_end
            )
        ).order_by(Checkin.checkin_date)
    )
    this_week_checkins = result.scalars().all()

    # 获取上周打卡记录
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.user_id == user_id,
                Checkin.checkin_date >= last_week_start,
                Checkin.checkin_date <= last_week_end
            )
        )
    )
    last_week_checkins = result.scalars().all()

    # 计算数据
    daily_rates = [
        {
            "date": c.checkin_date.isoformat(),
            "rate": float(c.completion_rate)
        }
        for c in this_week_checkins
    ]

    this_week_avg = (
        sum(float(c.completion_rate) for c in this_week_checkins) / len(this_week_checkins)
        if this_week_checkins else 0
    )

    last_week_avg = (
        sum(float(c.completion_rate) for c in last_week_checkins) / len(last_week_checkins)
        if last_week_checkins else 0
    )

    week_over_week = (
        (this_week_avg - last_week_avg) / last_week_avg * 100
        if last_week_avg > 0 else 0
    )

    # 生成总结
    if this_week_avg >= 80:
        summary = f"本周表现优秀！平均完成率{this_week_avg:.1f}%，继续保持！"
    elif this_week_avg >= 50:
        summary = f"本周表现良好，平均完成率{this_week_avg:.1f}%，还有提升空间哦～"
    else:
        summary = f"本周平均完成率{this_week_avg:.1f}%，下周加油！小搭陪你一起努力！"

    return WeeklyReportResponse(
        user_id=user_id,
        week_start=week_start,
        week_end=week_end,
        daily_rates=daily_rates,
        average_rate=round(this_week_avg, 2),
        week_over_week=round(week_over_week, 2),
        current_streak=user.current_streak,
        best_study_time=None,  # TODO: 统计最佳学习时段
        summary=summary
    )