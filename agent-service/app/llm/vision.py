"""
多模态模型工厂 — 支持文本 + 图片输入，直接返回 LangChain ChatOpenAI 实例。

用法示例：
    from langchain_core.messages import HumanMessage

    llm = get_vision_model()
    msg = HumanMessage(content=[
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": "https://..."}},
    ])
    response = await llm.ainvoke([msg])
"""
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from app.config import get_settings


def get_vision_model(
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """
    返回多模态模型实例（ChatOpenAI）。
    未传参数优先使用 vision_* 配置，再回退到 llm_* 配置。
    """
    settings = get_settings()
    resolved_api_key = api_key or settings.vision_api_key or settings.llm_api_key or None
    resolved_base_url = base_url or settings.vision_base_url or settings.llm_base_url or None
    resolved_model = model or settings.vision_model
    resolved_temp = temperature if temperature is not None else settings.llm_temperature

    return ChatOpenAI(
        api_key=SecretStr(resolved_api_key), # type: ignore
        base_url=resolved_base_url,
        model=resolved_model,
        temperature=resolved_temp,
    )
