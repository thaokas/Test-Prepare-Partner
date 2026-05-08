"""
LLM 模块
- get_chat_model : 纯文本语言模型，返回 ChatOpenAI
- get_vision_model: 多模态模型（文本 + 图片），返回 ChatOpenAI
- get_llm         : 向后兼容别名，等同于 get_chat_model
"""
from .chat import get_chat_model
from .vision import get_vision_model

# 向后兼容：现有调用 get_llm() 的地方暂不修改
get_llm = get_chat_model

__all__ = ["get_chat_model", "get_vision_model", "get_llm"]
