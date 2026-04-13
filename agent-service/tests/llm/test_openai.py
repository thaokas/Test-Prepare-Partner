"""
Tests for OpenAILLM provider (app/llm/providers/openai.py).

TDD: these tests are written BEFORE the implementation.
All ChatOpenAI calls are mocked so no real API calls are made.
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_chat_openai(monkeypatch):
    """Patch ChatOpenAI inside base_openai (the real construction site)."""
    mock_cls = MagicMock()
    mock_instance = MagicMock()
    mock_cls.return_value = mock_instance
    monkeypatch.setattr(
        "app.llm.providers.base_openai.ChatOpenAI", mock_cls
    )
    return mock_cls, mock_instance


class TestOpenAILLM:
    def test_inherits_from_openai_style_llm(self, mock_chat_openai):
        from app.llm.providers.openai import OpenAILLM
        from app.llm.providers.base_openai import OpenAIStyleLLM

        llm = OpenAILLM(api_key="mykey")
        assert isinstance(llm, OpenAIStyleLLM)

    def test_default_model_is_gpt4(self, mock_chat_openai):
        from app.llm.providers.openai import OpenAILLM

        mock_cls, _ = mock_chat_openai
        OpenAILLM(api_key="mykey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4"

    def test_base_url_is_openai(self, mock_chat_openai):
        from app.llm.providers.openai import OpenAILLM

        mock_cls, _ = mock_chat_openai
        OpenAILLM(api_key="mykey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["base_url"] == "https://api.openai.com/v1"

    def test_custom_model_name(self, mock_chat_openai):
        from app.llm.providers.openai import OpenAILLM

        mock_cls, _ = mock_chat_openai
        OpenAILLM(api_key="mykey", model_name="gpt-3.5-turbo")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["model"] == "gpt-3.5-turbo"

    def test_api_key_forwarded(self, mock_chat_openai):
        from app.llm.providers.openai import OpenAILLM

        mock_cls, _ = mock_chat_openai
        OpenAILLM(api_key="sk-secretkey")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["api_key"] == "sk-secretkey"
