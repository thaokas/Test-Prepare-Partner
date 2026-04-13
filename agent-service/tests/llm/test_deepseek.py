"""
Tests for DeepSeekLLM provider (app/llm/providers/deepseek.py).

TDD: these tests are written BEFORE the implementation.
All ChatOpenAI calls are mocked so no real API calls are made.
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_chat_openai(monkeypatch):
    """Patch ChatOpenAI inside base_openai."""
    mock_cls = MagicMock()
    mock_instance = MagicMock()
    mock_cls.return_value = mock_instance
    monkeypatch.setattr(
        "app.llm.providers.base_openai.ChatOpenAI", mock_cls
    )
    return mock_cls, mock_instance


class TestDeepSeekLLM:
    def test_inherits_from_openai_style_llm(self, mock_chat_openai):
        from app.llm.providers.deepseek import DeepSeekLLM
        from app.llm.providers.base_openai import OpenAIStyleLLM

        llm = DeepSeekLLM(api_key="dskey")
        assert isinstance(llm, OpenAIStyleLLM)

    def test_default_model_is_deepseek_chat(self, mock_chat_openai):
        from app.llm.providers.deepseek import DeepSeekLLM

        mock_cls, _ = mock_chat_openai
        DeepSeekLLM(api_key="dskey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["model"] == "deepseek-chat"

    def test_base_url_is_deepseek(self, mock_chat_openai):
        from app.llm.providers.deepseek import DeepSeekLLM

        mock_cls, _ = mock_chat_openai
        DeepSeekLLM(api_key="dskey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"

    def test_custom_model_name(self, mock_chat_openai):
        from app.llm.providers.deepseek import DeepSeekLLM

        mock_cls, _ = mock_chat_openai
        DeepSeekLLM(api_key="dskey", model_name="deepseek-coder")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["model"] == "deepseek-coder"

    def test_api_key_forwarded(self, mock_chat_openai):
        from app.llm.providers.deepseek import DeepSeekLLM

        mock_cls, _ = mock_chat_openai
        DeepSeekLLM(api_key="ds-secretkey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["api_key"] == "ds-secretkey"
