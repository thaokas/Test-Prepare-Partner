"""
OpenAI官方API提供者
"""
from app.llm.providers.base_openai import OpenAIStyleLLM


class OpenAILLM(OpenAIStyleLLM):
    """OpenAI官方API"""

    def __init__(self, api_key: str, model_name: str = "gpt-4", **kwargs):
        super().__init__(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            model_name=model_name,
            **kwargs
        )
