"""
打卡相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date

from app.models.database import get_db
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.models.task import Task
from app.models.checkin import Checkin
from app.routers.schemas import CheckinRequest, CheckinResponse

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


# 鼓励话术映射
ENCOURAGEMENT_MAP = {
    10: "迈出第一步就是胜利！今天你已经打败了50%的拖延症患者～小搭会一直陪着你！",
    25: "四分之一里程碑达成！小搭从书包里探出头给你加油～",
    50: "半程庆祝！小搭为你转圈圈～继续加油！",
    75: "冲刺阶段！小搭握拳为你加油，就差一点点啦！",
    100: "🏆 恭喜完成今日所有任务！小搭从书包里掏出一颗糖送给你～可以安心喝杯奶茶，明天继续冲！"
}


def get_encouragement(completion_rate: float) -> str:
    """根据完成率获取鼓励话术"""
    if completion_rate >= 100:
        return ENCOURAGEMENT_MAP[100]
    elif completion_rate >= 75:
        return ENCOURAGEMENT_MAP[75]
    elif completion_rate >= 50:
        return ENCOURAGEMENT_MAP[50]
    elif completion_rate >= 25:
        return ENCOURAGEMENT_MAP[25]
    else:
        return ENCOURAGEMENT_MAP[10]


@router.post("", response_model=CheckinResponse)
async def checkin(
    request: CheckinRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    打卡处理
    """
    # 检查用户
    result = await db.execute(
        select(User).where(User.user_id == request.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取活跃计划
    result = await db.execute(
        select(StudyPlan).where(
            StudyPlan.user_id == request.user_id,
            StudyPlan.plan_status == 0
        )
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="未找到进行中的计划")

    # 获取今日任务
    today = date.today()
    result = await db.execute(
        select(Task).where(
            and_(
                Task.plan_id == plan.plan_id,
                Task.task_date == today,
                Task.status != 2  # 未完成
            )
        )
    )
    incomplete_tasks = result.scalars().all()

    # TODO: 使用LLM解析打卡内容，匹配任务
    # 目前简单处理：标记所有未完成任务为完成
    completed_count = len(incomplete_tasks)
    for task in incomplete_tasks:
        task.status = 2  # 已完成

    # 获取今日所有任务
    result = await db.execute(
        select(Task).where(
            and_(
                Task.plan_id == plan.plan_id,
                Task.task_date == today
            )
        )
    )
    all_tasks = result.scalars().all()
    total_count = len(all_tasks)

    # 计算完成率
    completed_total = sum(1 for t in all_tasks if t.status == 2)
    completion_rate = (completed_total / total_count * 100) if total_count > 0 else 0

    # 更新连续打卡
    # 检查昨天是否打卡
    yesterday = today - __import__('datetime').timedelta(days=1)
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.user_id == request.user_id,
                Checkin.checkin_date == yesterday
            )
        )
    )
    yesterday_checkin = result.scalar_one_or_none()

    if yesterday_checkin or user.current_streak == 0:
        user.current_streak += 1
        if user.current_streak > user.max_streak:
            user.max_streak = user.current_streak

    user.total_checkins += 1

    # 创建打卡记录
    checkin_record = Checkin(
        user_id=request.user_id,
        plan_id=plan.plan_id,
        checkin_date=today,
        completed_tasks=completed_total,
        total_tasks=total_count,
        completion_rate=completion_rate
    )
    db.add(checkin_record)

    await db.commit()

    # 获取鼓励话术
    encouragement = get_encouragement(completion_rate)

    return CheckinResponse(
        completed_tasks=completed_total,
        total_tasks=total_count,
        completion_rate=round(completion_rate, 2),
        streak=user.current_streak,
        encouragement=encouragement,
        easter_egg=None
    )