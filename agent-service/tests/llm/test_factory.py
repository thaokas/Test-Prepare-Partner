"""
Tests for LLM factory (app/llm/factory.py).

TDD: these tests are written BEFORE the implementation.
Settings and LLM classes are mocked to avoid any real side-effects.
"""
import pytest
from unittest.mock import MagicMock, patch


def _make_settings(provider: str, api_key: str = "key", model: str = "gpt-4"):
    settings = MagicMock()
    settings.llm_provider = provider
    settings.llm_api_key = api_key
    settings.llm_model = model
    return settings


class TestGetLLM:
    def test_returns_openai_llm_for_openai_provider(self):
        from app.llm.factory import get_llm

        mock_openai_instance = MagicMock()
        mock_deepseek_instance = MagicMock()

        with patch("app.llm.factory.get_settings", return_value=_make_settings("openai")), \
             patch("app.llm.factory.OpenAILLM", return_value=mock_openai_instance) as mock_openai_cls, \
             patch("app.llm.factory.DeepSeekLLM", return_value=mock_deepseek_instance):

            result = get_llm()

            mock_openai_cls.assert_called_once_with(api_key="key", model_name="gpt-4")
            assert result is mock_openai_instance

    def test_returns_deepseek_llm_for_deepseek_provider(self):
        from app.llm.factory import get_llm

        mock_openai_instance = MagicMock()
        mock_deepseek_instance = MagicMock()

        with patch("app.llm.factory.get_settings",
                   return_value=_make_settings("deepseek", model="deepseek-chat")), \
             patch("app.llm.factory.OpenAILLM", return_value=mock_openai_instance), \
             patch("app.llm.factory.DeepSeekLLM", return_value=mock_deepseek_instance) as mock_ds_cls:

            result = get_llm()

            mock_ds_cls.assert_called_once_with(api_key="key", model_name="deepseek-chat")
            assert result is mock_deepseek_instance

    def test_raises_value_error_for_unknown_provider(self):
        from app.llm.factory import get_llm

        with patch("app.llm.factory.get_settings",
                   return_value=_make_settings("anthropic")), \
             patch("app.llm.factory.OpenAILLM"), \
             patch("app.llm.factory.DeepSeekLLM"):

            with pytest.raises(ValueError, match="anthropic"):
                get_llm()

    def test_get_llm_passes_api_key_from_settings(self):
        from app.llm.factory import get_llm

        with patch("app.llm.factory.get_settings",
                   return_value=_make_settings("openai", api_key="sk-abc123")), \
             patch("app.llm.factory.OpenAILLM") as mock_cls, \
             patch("app.llm.factory.DeepSeekLLM"):

            get_llm()
            call_kwargs = mock_cls.call_args.kwargs
            assert call_kwargs["api_key"] == "sk-abc123"

    def test_get_llm_passes_model_from_settings(self):
        from app.llm.factory import get_llm

        with patch("app.llm.factory.get_settings",
                   return_value=_make_settings("openai", model="gpt-4-turbo")), \
             patch("app.llm.factory.OpenAILLM") as mock_cls, \
             patch("app.llm.factory.DeepSeekLLM"):

            get_llm()
            call_kwargs = mock_cls.call_args.kwargs
            assert call_kwargs["model_name"] == "gpt-4-turbo"


class TestGetLLMSingleton:
    def setup_method(self):
        """Reset the singleton before each test."""
        import app.llm.factory as factory_module
        factory_module._llm_singleton = None

    def teardown_method(self):
        """Reset the singleton after each test."""
        import app.llm.factory as factory_module
        factory_module._llm_singleton = None

    def test_singleton_returns_same_instance_on_multiple_calls(self):
        from app.llm.factory import get_llm_singleton

        mock_instance = MagicMock()

        with patch("app.llm.factory.get_llm", return_value=mock_instance) as mock_get_llm:
            first = get_llm_singleton()
            second = get_llm_singleton()
            third = get_llm_singleton()

            # get_llm should only be called once despite 3 calls to get_llm_singleton
            mock_get_llm.assert_called_once()
            assert first is second is third is mock_instance

    def test_singleton_calls_get_llm_on_first_call(self):
        from app.llm.factory import get_llm_singleton

        mock_instance = MagicMock()
        with patch("app.llm.factory.get_llm", return_value=mock_instance) as mock_get_llm:
            result = get_llm_singleton()
            mock_get_llm.assert_called_once()
            assert result is mock_instance
