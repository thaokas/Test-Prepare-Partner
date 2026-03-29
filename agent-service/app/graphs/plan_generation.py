"""
计划生成工作流 (LangGraph)

状态节点：
START → collect_info → calculate_phase → generate_tasks → save_to_db → END
"""
from typing import TypedDict, List, Optional
from datetime import date, timedelta
import json

from langgraph.graph import StateGraph, END

from app.models.study_plan import StudyPlan
from app.models.task import Task


class PlanGenerationState(TypedDict):
    """计划生成工作流状态"""
    user_id: str
    exam_name: str
    exam_type: str
    exam_date: date
    daily_hours: float
    foundation_level: int
    weak_subjects: Optional[List[str]]

    # 计算结果
    days_remaining: int
    current_phase: int
    phase_name: str

    # 生成的任务
    tasks: List[dict]

    # 结果
    plan_id: Optional[str]
    message: Optional[str]
    error: Optional[str]


def calculate_phase_node(state: PlanGenerationState) -> dict:
    """计算当前阶段节点"""
    days_remaining = (state["exam_date"] - date.today()).days

    if days_remaining > 90:
        phase = 1
        phase_name = "基础阶段"
    elif days_remaining >= 45:
        phase = 2
        phase_name = "强化阶段"
    else:
        phase = 3
        phase_name = "冲刺阶段"

    return {
        "days_remaining": days_remaining,
        "current_phase": phase,
        "phase_name": phase_name
    }


def generate_tasks_node(state: PlanGenerationState) -> dict:
    """生成任务节点

    任务分配规则：
    - 按每日可用时长分配科目权重
    - 薄弱科目额外+20%时长
    - 单任务时长控制在45-90分钟
    - 零基础用户减少新知识量，增加复习频次
    """
    tasks = []
    daily_minutes = int(state["daily_hours"] * 60)
    days = min(state["days_remaining"], 30)  # 最多生成30天任务

    # 根据基础水平调整
    learn_ratio = {0: 0.4, 1: 0.5, 2: 0.6}.get(state["foundation_level"], 0.5)

    for i in range(days):
        task_date = date.today() + timedelta(days=i)

        # 学习任务
        learn_minutes = int(daily_minutes * learn_ratio)
        tasks.append({
            "task_date": task_date.isoformat(),
            "subject": "学习",
            "task_content": f"第{i+1}天学习任务",
            "estimated_minutes": min(learn_minutes, 90),
            "task_type": 1,  # 学习
            "phase": state["current_phase"],
            "status": 0
        })

        # 复习任务
        review_minutes = int(daily_minutes * (1 - learn_ratio))
        tasks.append({
            "task_date": task_date.isoformat(),
            "subject": "复习",
            "task_content": f"第{i+1}天复习任务",
            "estimated_minutes": min(review_minutes, 90),
            "task_type": 2,  # 复习
            "phase": state["current_phase"],
            "status": 0
        })

    return {"tasks": tasks}


def create_plan_generation_graph():
    """创建计划生成工作流图"""
    workflow = StateGraph(PlanGenerationState)

    # 添加节点
    workflow.add_node("calculate_phase", calculate_phase_node)
    workflow.add_node("generate_tasks", generate_tasks_node)

    # 设置入口
    workflow.set_entry_point("calculate_phase")

    # 添加边
    workflow.add_edge("calculate_phase", "generate_tasks")
    workflow.add_edge("generate_tasks", END)

    return workflow.compile()


# 导出编译后的图
plan_generation_graph = create_plan_generation_graph()