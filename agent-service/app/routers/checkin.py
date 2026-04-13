"""
打卡相关API路由
"""
from fastapi import APIRouter, HTTPException

from app.agents.checkin import checkin_graph
from app.routers.schemas import CheckinRequest, CheckinResponse

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/", response_model=CheckinResponse)
async def process_checkin(request: CheckinRequest):
    """打卡处理（LLM驱动：智能解析打卡内容并匹配任务）"""
    initial_state = {
        "user_id": request.user_id,
        "content": request.content,
        "checkin_type": request.checkin_type,
        "parsed_tasks": [],
        "confidence": 0.0,
        "matched_tasks": [],
        "completed_count": 0,
        "total_count": 0,
        "completion_rate": 0.0,
        "streak_updated": False,
        "new_streak": 0,
        "easter_egg": None,
        "encouragement": "",
        "checkin_id": None,
        "error": None,
    }

    result = await checkin_graph.ainvoke(initial_state)

    if result.get("error") and not result.get("checkin_id"):
        raise HTTPException(status_code=500, detail=result["error"])

    return CheckinResponse(
        checkin_id=result.get("checkin_id"),
        completion_rate=result.get("completion_rate", 0.0),
        matched_tasks=result.get("matched_tasks", []),
        encouragement=result.get("encouragement", "加油！"),
        easter_egg=result.get("easter_egg"),
        streak_days=result.get("new_streak", 0),
    )
