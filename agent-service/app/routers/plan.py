"""计划生成相关接口 — LLM代理 + 网络搜索代理"""
import logging

from fastapi import APIRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.llm import get_chat_model
from app.tools.search_tools import _web_search
from app.routers.schemas import LlmChatRequest, LlmChatResponse, SearchRequest, SearchResponse, SearchResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plan", tags=["计划生成"])


@router.post("/llm/chat", response_model=LlmChatResponse)
async def llm_chat(req: LlmChatRequest) -> LlmChatResponse:
    """LLM代理接口 — 前端Agent模块通过此接口调用大模型"""
    try:
        llm = get_chat_model()
        messages = []

        if req.system_prompt:
            messages.append(SystemMessage(content=req.system_prompt))

        for m in req.messages:
            if m.get("role") == "user":
                messages.append(HumanMessage(content=m["content"]))
            elif m.get("role") == "assistant":
                messages.append(AIMessage(content=m["content"]))

        resp = await llm.ainvoke(messages)
        return LlmChatResponse(content=resp.content)
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        return LlmChatResponse(content="", error=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest) -> SearchResponse:
    """网络搜索代理接口 — 前端Agent模块通过此接口搜索备考信息"""
    try:
        raw = _web_search(req.query, max_results=5)
        results = [
            SearchResult(
                title=r.get("title", ""),
                snippet=r.get("snippet", ""),
                url=r.get("url", ""),
            )
            for r in raw
        ]
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return SearchResponse(results=[], error=str(e))
