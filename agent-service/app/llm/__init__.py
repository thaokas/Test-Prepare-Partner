"""
LLM模块
提供LLM工厂函数，供应用其他模块使用
"""
from .factory import get_llm, get_llm_singleton

__all__ = ["get_llm", "get_llm_singleton"]
