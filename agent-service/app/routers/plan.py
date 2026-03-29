"""
计划相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
import json

from app.models.database import get_db
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.models.task import Task
from app.routers.schemas import PlanGenerateRequest, PlanGenerateResponse, TodayTasksResponse, TaskSchema

router = APIRouter(prefix="/api/plan", tags=["plan"])


def calculate_phase(days_remaining: int) -> int:
    """计算当前阶段"""
    if days_remaining > 90:
        return 1  # 基础阶段
    elif days_remaining >= 45:
        return 2  # 强化阶段
    else:
        return 3  # 冲刺阶段


@router.post("/generate", response_model=PlanGenerateResponse)
async def generate_plan(
    request: PlanGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成备考计划
    """
    # 检查用户是否存在
    result = await db.execute(
        select(User).where(User.user_id == request.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 计算剩余天数和阶段
    days_remaining = (request.exam_date - date.today()).days
    if days_remaining <= 0:
        raise HTTPException(status_code=400, detail="考试日期必须在未来")

    current_phase = calculate_phase(days_remaining)

    # 创建计划
    plan = StudyPlan(
        user_id=request.user_id,
        exam_name=request.exam_name,
        exam_type=request.exam_type,
        exam_date=request.exam_date,
        daily_hours=request.daily_hours,
        foundation_level=request.foundation_level,
        weak_subjects=json.dumps(request.weak_subjects) if request.weak_subjects else None,
        current_phase=current_phase,
        current_mode=1  # 默认温柔模式
    )
    db.add(plan)
    await db.flush()  # 获取plan_id

    # TODO: 调用LangGraph生成详细任务
    # 目前生成示例任务
    tasks = generate_sample_tasks(
        plan.plan_id,
        days_remaining,
        request.daily_hours,
        current_phase
    )
    for task in tasks:
        db.add(task)

    await db.commit()

    return PlanGenerateResponse(
        plan_id=plan.plan_id,
        total_tasks=len(tasks),
        phases=[{
            "phase": current_phase,
            "name": ["", "基础阶段", "强化阶段", "冲刺阶段"][current_phase],
            "days_remaining": days_remaining
        }],
        message=f"计划创建成功！距离{request.exam_name}还有{days_remaining}天"
    )


def generate_sample_tasks(
    plan_id: str,
    days_remaining: int,
    daily_hours: float,
    phase: int
) -> list[Task]:
    """
    生成示例任务
    TODO: 替换为LangGraph智能生成
    """
    tasks = []
    daily_minutes = int(daily_hours * 60)

    # 生成未来7天的任务作为示例
    for i in range(min(7, days_remaining)):
        task_date = date.today() + timedelta(days=i)

        # 简单分配任务
        morning_task = Task(
            plan_id=plan_id,
            task_date=task_date,
            subject="学习",
            task_content=f"第{i+1}天学习任务",
            estimated_minutes=daily_minutes // 2,
            task_type=1,
            phase=phase,
            status=0
        )
        tasks.append(morning_task)

        afternoon_task = Task(
            plan_id=plan_id,
            task_date=task_date,
            subject="复习",
            task_content=f"第{i+1}天复习任务",
            estimated_minutes=daily_minutes // 2,
            task_type=2,
            phase=phase,
            status=0
        )
        tasks.append(afternoon_task)

    return tasks


@router.get("/today", response_model=TodayTasksResponse)
async def get_today_tasks(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日任务
    """
    # 获取用户当前活跃计划
    result = await db.execute(
        select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.plan_status == 0  # 进行中
        )
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="未找到进行中的计划")

    # 获取今日任务
    today = date.today()
    result = await db.execute(
        select(Task).where(
            Task.plan_id == plan.plan_id,
            Task.task_date == today
        ).order_by(Task.task_id)
    )
    tasks = result.scalars().all()

    task_list = [TaskSchema.model_validate(t) for t in tasks]
    completed_count = sum(1 for t in tasks if t.status == 2)
    total_count = len(tasks)
    completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

    return TodayTasksResponse(
        tasks=task_list,
        completed_count=completed_count,
        total_count=total_count,
        completion_rate=round(completion_rate, 2)
    )