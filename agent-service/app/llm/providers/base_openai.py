"""
OpenAI风格LLM实现
可复用于DeepSeek等兼容OpenAI接口的服务
"""
from typing import Optional, List, AsyncIterator
from langchain_openai import ChatOpenAI
from app.llm.base import BaseLLM


class OpenAIStyleLLM(BaseLLM):
    """OpenAI风格LLM实现，可复用于DeepSeek等兼容��口"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        temperature: float = 0.7,
        **kwargs
    ):
        self._llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model_name,
            temperature=temperature,
            **kwargs
        )

    def _build_messages(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> List[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = self._build_messages(prompt, system_prompt)
        return self._llm.invoke(messages).content

    async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = self._build_messages(prompt, system_prompt)
        response = await self._llm.ainvoke(messages)
        return response.content

    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        messages = self._build_messages(prompt, system_prompt)
        async for chunk in self._llm.astream(messages):
            if chunk.content:
                yield chunk.content

    def bind_tools(self, tools: List) -> "OpenAIStyleLLM":
        self._llm = self._llm.bind_tools(tools)
        return self
