"""
计划相关API路由 — 多轮对话式备考计划生成
"""
import uuid
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agents.planner import planner_graph
from app.tools.db_tools import get_today_tasks
from app.routers.schemas import (
    PlanChatRequest,
    PlanChatResponse,
    PlanGenerateRequest,
    PlanGenerateResponse,
    TodayTasksResponse,
)

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.post("/chat", response_model=PlanChatResponse)
async def chat_plan(request: PlanChatRequest):
    """多轮对话式备考计划生成（支持追问和中断恢复）"""
    # 确定线程 ID（新对话生成新 ID，续聊使用已有 ID）
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # 构造初始 state（新对话首次调用时）
    initial_state = {
        "user_id": request.user_id,
        "messages": [HumanMessage(content=request.message)],
        "urls": request.urls or [],
        "pdf_urls": request.pdf_urls or [],
        "image_urls": request.image_urls or [],
        "resource_summary": "",
        "exam_name": None,
        "exam_type": None,
        "exam_date": None,
        "daily_hours": None,
        "foundation_level": None,
        "weak_subjects": [],
        "rest_days_per_week": 1,
        "clarification_rounds": 0,
        "clarification_question": None,
        "exam_info": {},
        "total_days": 0,
        "phases": [],
        "estimated_completion_date": "",
        "tasks": [],
        "plan_id": None,
        "message": "",
        "error": None,
    }

    # 判断是否是续聊（已有 thread_id 且图有中断状态）
    if request.thread_id:
        # 恢复中断：用户回复追问
        result = await planner_graph.ainvoke(
            Command(resume=request.message),
            config=config,
        )
    else:
        # 新对话：传入初始 state
        result = await planner_graph.ainvoke(initial_state, config=config)

    # 检查图是否在 ask_user 处中断（需要追问）
    state_snapshot = planner_graph.get_state(config)
    next_nodes = state_snapshot.next

    if next_nodes and "ask_user" in next_nodes:
        # 图在 ask_user 前中断，需要追问
        clarification = state_snapshot.values.get("clarification_question", "")
        return PlanChatResponse(
            thread_id=thread_id,
            status="waiting_for_input",
            message=clarification or "请补充更多信息",
            clarification_question=clarification,
        )

    # 图执行完毕
    if result.get("error") and not result.get("plan_id"):
        return PlanChatResponse(
            thread_id=thread_id,
            status="error",
            message=result.get("error", "计划生成失败"),
        )

    return PlanChatResponse(
        thread_id=thread_id,
        status="completed",
        message=result.get("message", "备考计划已生成"),
        plan_id=result.get("plan_id"),
        tasks=result.get("tasks", []),
    )


# ── 兼容旧接口 ──────────────────────────────────────────────────────

@router.post("/generate", response_model=PlanGenerateResponse)
async def generate_plan(request: PlanGenerateRequest):
    """一次性生成备考计划（不追问，兼容旧接口）"""
    initial_state = {
        "user_id": request.user_id,
        "messages": [HumanMessage(content=f"我要备考{request.exam_name}")],
        "urls": [],
        "pdf_urls": [],
        "image_urls": [],
        "resource_summary": "",
        "exam_name": request.exam_name,
        "exam_type": request.exam_type,
        "exam_date": str(request.exam_date),
        "daily_hours": request.daily_hours,
        "foundation_level": request.foundation_level,
        "weak_subjects": request.weak_subjects or [],
        "rest_days_per_week": 1,
        "clarification_rounds": 6,  # 强制跳过追问
        "clarification_question": None,
        "exam_info": {},
        "total_days": 0,
        "phases": [],
        "estimated_completion_date": "",
        "tasks": [],
        "plan_id": None,
        "message": "",
        "error": None,
    }

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    result = await planner_graph.ainvoke(initial_state, config=config)

    if result.get("error") and not result.get("plan_id"):
        raise HTTPException(status_code=500, detail=result["error"])

    return PlanGenerateResponse(
        plan_id=result.get("plan_id"),
        total_tasks=len(result.get("tasks", [])),
        message=result.get("message", "计划生成完成"),
        tasks=result.get("tasks", []),
    )


@router.get("/today")
async def get_today_tasks_endpoint(user_id: str):
    """获取今日任务"""
    tasks = await get_today_tasks.ainvoke({"user_id": user_id})
    return {"tasks": tasks, "total": len(tasks)}