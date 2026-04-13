"""
LLM工厂模块
根据配置创建对应的LLM实例
"""
from typing import Optional
from app.llm.base import BaseLLM
from app.config import get_settings
from app.llm.providers.openai import OpenAILLM
from app.llm.providers.deepseek import DeepSeekLLM


def get_llm() -> BaseLLM:
    """工厂方法：根据配置创建LLM实例"""
    settings = get_settings()
    provider = settings.llm_provider

    if provider == "openai":
        return OpenAILLM(
            api_key=settings.llm_api_key,
            model_name=settings.llm_model
        )
    elif provider == "deepseek":
        return DeepSeekLLM(
            api_key=settings.llm_api_key,
            model_name=settings.llm_model
        )

    raise ValueError(f"Unknown LLM provider: {provider}")


_llm_singleton: Optional[BaseLLM] = None


def get_llm_singleton() -> BaseLLM:
    """单例模式获取LLM实例"""
    global _llm_singleton
    if _llm_singleton is None:
        _llm_singleton = get_llm()
    return _llm_singleton
