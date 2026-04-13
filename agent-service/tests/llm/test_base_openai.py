"""
Tests for OpenAIStyleLLM base provider (app/llm/providers/base_openai.py).

TDD: these tests are written BEFORE the implementation.
All ChatOpenAI calls are mocked so no real API calls are made.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Optional, List


@pytest.fixture
def mock_chat_openai(monkeypatch):
    """Patch ChatOpenAI wherever it is imported inside base_openai."""
    mock_cls = MagicMock()
    mock_instance = MagicMock()
    mock_cls.return_value = mock_instance
    monkeypatch.setattr(
        "app.llm.providers.base_openai.ChatOpenAI", mock_cls
    )
    return mock_cls, mock_instance


class TestBuildMessages:
    """Test _build_messages helper."""

    def test_build_messages_without_system_prompt(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        messages = llm._build_messages("Hello")
        assert messages == [{"role": "user", "content": "Hello"}]

    def test_build_messages_with_system_prompt(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        messages = llm._build_messages("Hello", system_prompt="You are helpful.")
        assert messages == [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]

    def test_build_messages_none_system_prompt_omitted(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        messages = llm._build_messages("Hi", system_prompt=None)
        roles = [m["role"] for m in messages]
        assert "system" not in roles


class TestInvoke:
    """Test synchronous invoke."""

    def test_invoke_calls_llm_invoke_with_messages(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai
        mock_response = MagicMock()
        mock_response.content = "Hello back"
        mock_instance.invoke.return_value = mock_response

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        result = llm.invoke("Hello")

        mock_instance.invoke.assert_called_once_with(
            [{"role": "user", "content": "Hello"}]
        )
        assert result == "Hello back"

    def test_invoke_with_system_prompt(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai
        mock_response = MagicMock()
        mock_response.content = "Sure!"
        mock_instance.invoke.return_value = mock_response

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        result = llm.invoke("Hello", system_prompt="Be concise.")

        expected_messages = [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hello"},
        ]
        mock_instance.invoke.assert_called_once_with(expected_messages)
        assert result == "Sure!"


class TestAinvoke:
    """Test async ainvoke."""

    @pytest.mark.asyncio
    async def test_ainvoke_calls_llm_ainvoke(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai
        mock_response = MagicMock()
        mock_response.content = "Async response"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        result = await llm.ainvoke("Hello")

        mock_instance.ainvoke.assert_called_once_with(
            [{"role": "user", "content": "Hello"}]
        )
        assert result == "Async response"

    @pytest.mark.asyncio
    async def test_ainvoke_with_system_prompt(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai
        mock_response = MagicMock()
        mock_response.content = "Got it"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        result = await llm.ainvoke("Hi", system_prompt="System here.")

        expected_messages = [
            {"role": "system", "content": "System here."},
            {"role": "user", "content": "Hi"},
        ]
        mock_instance.ainvoke.assert_called_once_with(expected_messages)
        assert result == "Got it"


class TestStream:
    """Test async streaming."""

    @pytest.mark.asyncio
    async def test_stream_yields_chunks(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai

        async def fake_astream(messages):
            for text in ["Hello", " ", "world"]:
                chunk = MagicMock()
                chunk.content = text
                yield chunk

        mock_instance.astream = fake_astream

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        chunks = []
        async for chunk in llm.stream("Hello"):
            chunks.append(chunk)

        assert chunks == ["Hello", " ", "world"]

    @pytest.mark.asyncio
    async def test_stream_skips_empty_chunks(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai

        async def fake_astream(messages):
            for text in ["Hello", "", "world"]:
                chunk = MagicMock()
                chunk.content = text
                yield chunk

        mock_instance.astream = fake_astream

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        chunks = []
        async for chunk in llm.stream("Hello"):
            chunks.append(chunk)

        # Empty string chunks should be filtered out
        assert "" not in chunks
        assert "Hello" in chunks
        assert "world" in chunks


class TestBindTools:
    """Test bind_tools method."""

    def test_bind_tools_delegates_to_inner_llm(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, mock_instance = mock_chat_openai
        mock_bound = MagicMock()
        mock_instance.bind_tools.return_value = mock_bound

        llm = OpenAIStyleLLM(
            api_key="key", base_url="http://example.com", model_name="gpt-4"
        )
        tools = [MagicMock(), MagicMock()]
        result = llm.bind_tools(tools)

        mock_instance.bind_tools.assert_called_once_with(tools)
        assert result is llm  # returns self
        assert llm._llm is mock_bound  # inner llm replaced


class TestOpenAIStyleLLMInit:
    """Test constructor wires ChatOpenAI correctly."""

    def test_init_passes_params_to_chat_openai(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, _ = mock_chat_openai
        OpenAIStyleLLM(
            api_key="mykey",
            base_url="http://myhost/v1",
            model_name="gpt-3.5-turbo",
            temperature=0.3,
        )
        mock_cls.assert_called_once_with(
            api_key="mykey",
            base_url="http://myhost/v1",
            model="gpt-3.5-turbo",
            temperature=0.3,
        )

    def test_init_default_temperature(self, mock_chat_openai):
        from app.llm.providers.base_openai import OpenAIStyleLLM

        mock_cls, _ = mock_chat_openai
        OpenAIStyleLLM(
            api_key="mykey",
            base_url="http://myhost/v1",
            model_name="gpt-4",
        )
        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["temperature"] == 0.7
