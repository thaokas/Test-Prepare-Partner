"""
配置管理模块
从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # LLM (language model)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7

    # Vision / multimodal model (falls back to LLM settings if not set)
    vision_api_key: str = ""
    vision_base_url: str = ""
    vision_model: str = "gpt-4o"

    # Embedding
    embedding_model: str = "text-embedding-3-small"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()