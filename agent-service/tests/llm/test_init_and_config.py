"""
Tests for llm module __init__ files and config updates (Task 14).

Verifies:
- app/llm/__init__.py exports get_llm and get_llm_singleton
- app/llm/providers/__init__.py exports OpenAILLM and DeepSeekLLM
- app/config.py Settings has the three new fields (llm_provider, llm_temperature, llm_max_tokens)
"""
import pytest
from unittest.mock import MagicMock, patch


class TestLLMModuleInit:
    """Test app/llm/__init__.py exports."""

    def test_get_llm_importable_from_llm_package(self):
        from app.llm import get_llm
        assert callable(get_llm)

    def test_get_llm_singleton_importable_from_llm_package(self):
        from app.llm import get_llm_singleton
        assert callable(get_llm_singleton)

    def test_llm_all_exports(self):
        import app.llm as llm_pkg
        assert "get_llm" in llm_pkg.__all__
        assert "get_llm_singleton" in llm_pkg.__all__


class TestProvidersInit:
    """Test app/llm/providers/__init__.py exports."""

    def test_openai_llm_importable_from_providers(self):
        with patch("app.llm.providers.base_openai.ChatOpenAI", MagicMock()):
            from app.llm.providers import OpenAILLM
            assert OpenAILLM is not None

    def test_deepseek_llm_importable_from_providers(self):
        with patch("app.llm.providers.base_openai.ChatOpenAI", MagicMock()):
            from app.llm.providers import DeepSeekLLM
            assert DeepSeekLLM is not None

    def test_providers_all_exports(self):
        import app.llm.providers as providers_pkg
        assert "OpenAILLM" in providers_pkg.__all__
        assert "DeepSeekLLM" in providers_pkg.__all__


class TestConfigUpdates:
    """Test that Settings has the new fields added in Task 14."""

    def test_settings_has_llm_provider_field(self):
        from app.config import Settings
        s = Settings()
        assert hasattr(s, "llm_provider")

    def test_settings_llm_provider_default_is_openai(self):
        from app.config import Settings
        s = Settings()
        assert s.llm_provider == "openai"

    def test_settings_has_llm_temperature_field(self):
        from app.config import Settings
        s = Settings()
        assert hasattr(s, "llm_temperature")

    def test_settings_llm_temperature_default(self):
        from app.config import Settings
        s = Settings()
        assert s.llm_temperature == 0.7

    def test_settings_has_llm_max_tokens_field(self):
        from app.config import Settings
        s = Settings()
        assert hasattr(s, "llm_max_tokens")

    def test_settings_llm_max_tokens_default(self):
        from app.config import Settings
        s = Settings()
        assert s.llm_max_tokens == 4096

    def test_existing_fields_still_present(self):
        """Ensure original fields were not removed."""
        from app.config import Settings
        s = Settings()
        assert hasattr(s, "llm_api_key")
        assert hasattr(s, "llm_base_url")
        assert hasattr(s, "llm_model")
        assert hasattr(s, "database_url")
        assert hasattr(s, "embedding_model")
        assert hasattr(s, "host")
        assert hasattr(s, "port")
        assert hasattr(s, "debug")
