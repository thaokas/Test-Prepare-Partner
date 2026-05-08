"""
打卡相关API路由
"""
from fastapi import APIRouter, HTTPException

from app.agents.checkin import checkin_graph
from app.routers.schemas import CheckinRequest, CheckinResponse

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/", response_model=CheckinResponse)
async def process_checkin(request: CheckinRequest):
    """打卡处理（LLM驱动：根据完成内容生成鼓励文案）"""
    initial_state = {
        "completed_content": request.completed_content,
        "overall_completion_rate": request.overall_completion_rate,
        "image_url": request.image_url,
        "encouragement": "",
        "error": None,
    }

    result = await checkin_graph.ainvoke(initial_state)

    if result.get("error") and not result.get("encouragement"):
        raise HTTPException(status_code=500, detail=result["error"])

    return CheckinResponse(encouragement=result.get("encouragement", "今天也很努力，继续加油！"))
