"""
聊天对话API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.user import User
from app.routers.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    对话入口，接收用户消息，返回AI响应
    TODO: 集成LangGraph工作流
    """
    # 检查用户是否存在
    result = await db.execute(
        select(User).where(User.user_id == request.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # TODO: 调用LangGraph工作流处理消息
    # 目前返回简单响应
    return ChatResponse(
        response=f"收到消息：{request.message}",
        action=None,
        data={"user_id": request.user_id}
    )