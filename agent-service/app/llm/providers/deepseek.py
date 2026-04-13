"""
DeepSeek API提供者（兼容OpenAI接口）
"""
from app.llm.providers.base_openai import OpenAIStyleLLM


class DeepSeekLLM(OpenAIStyleLLM):
    """DeepSeek API（兼容OpenAI接口）"""

    def __init__(self, api_key: str, model_name: str = "deepseek-chat", **kwargs):
        super().__init__(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            model_name=model_name,
            **kwargs
        )
