"""
语言模型工厂 — 纯文本对话，直接返回 LangChain ChatOpenAI 实例
"""
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from app.config import get_settings


def get_chat_model(
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """
    返回语言模型实例（ChatOpenAI）。
    所有参数均可选，未传则读取环境变量 / config。
    """
    settings = get_settings()
    secret_api_key = SecretStr(api_key or settings.llm_api_key)
    return ChatOpenAI(
        api_key=secret_api_key,
        base_url=base_url or settings.llm_base_url or None,
        model=model or settings.llm_model,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )
