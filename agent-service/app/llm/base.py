"""
LLM抽象基类
定义所有LLM提供者必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List, AsyncIterator


class BaseLLM(ABC):
    """LLM抽象基类"""

    @abstractmethod
    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """同步调用"""
        pass

    @abstractmethod
    async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """异步调用"""
        pass

    @abstractmethod
    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """流式输出"""
        pass

    @abstractmethod
    def bind_tools(self, tools: List) -> "BaseLLM":
        """绑定工具"""
        pass
