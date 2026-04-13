"""
Tests for BaseLLM abstract class (app/llm/base.py).

TDD: these tests are written BEFORE the implementation.
"""
import pytest
from typing import Optional, List, AsyncIterator


class TestBaseLLMAbstract:
    """Test that BaseLLM is properly abstract."""

    def test_cannot_instantiate_base_llm(self):
        """BaseLLM must be abstract and cannot be instantiated directly."""
        from app.llm.base import BaseLLM
        with pytest.raises(TypeError):
            BaseLLM()  # type: ignore

    def test_concrete_subclass_must_implement_all_methods(self):
        """A fully concrete subclass can be instantiated."""
        from app.llm.base import BaseLLM

        class ConcreteLLM(BaseLLM):
            def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "response"

            async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "async response"

            async def stream(
                self, prompt: str, system_prompt: Optional[str] = None
            ) -> AsyncIterator[str]:
                yield "chunk"

            def bind_tools(self, tools: List) -> "ConcreteLLM":
                return self

        # Should not raise
        instance = ConcreteLLM()
        assert isinstance(instance, BaseLLM)

    def test_partial_implementation_raises_type_error_missing_invoke(self):
        """Subclass missing 'invoke' cannot be instantiated."""
        from app.llm.base import BaseLLM

        class PartialLLM(BaseLLM):
            # invoke is missing
            async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "async response"

            async def stream(
                self, prompt: str, system_prompt: Optional[str] = None
            ) -> AsyncIterator[str]:
                yield "chunk"

            def bind_tools(self, tools: List) -> "PartialLLM":
                return self

        with pytest.raises(TypeError):
            PartialLLM()

    def test_partial_implementation_raises_type_error_missing_ainvoke(self):
        """Subclass missing 'ainvoke' cannot be instantiated."""
        from app.llm.base import BaseLLM

        class PartialLLM(BaseLLM):
            def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "response"

            # ainvoke is missing

            async def stream(
                self, prompt: str, system_prompt: Optional[str] = None
            ) -> AsyncIterator[str]:
                yield "chunk"

            def bind_tools(self, tools: List) -> "PartialLLM":
                return self

        with pytest.raises(TypeError):
            PartialLLM()

    def test_partial_implementation_raises_type_error_missing_stream(self):
        """Subclass missing 'stream' cannot be instantiated."""
        from app.llm.base import BaseLLM

        class PartialLLM(BaseLLM):
            def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "response"

            async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "async response"

            # stream is missing

            def bind_tools(self, tools: List) -> "PartialLLM":
                return self

        with pytest.raises(TypeError):
            PartialLLM()

    def test_partial_implementation_raises_type_error_missing_bind_tools(self):
        """Subclass missing 'bind_tools' cannot be instantiated."""
        from app.llm.base import BaseLLM

        class PartialLLM(BaseLLM):
            def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "response"

            async def ainvoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
                return "async response"

            async def stream(
                self, prompt: str, system_prompt: Optional[str] = None
            ) -> AsyncIterator[str]:
                yield "chunk"

            # bind_tools is missing

        with pytest.raises(TypeError):
            PartialLLM()

    def test_base_llm_has_all_abstract_methods(self):
        """BaseLLM declares exactly the four required abstract methods."""
        from app.llm.base import BaseLLM
        import inspect

        abstract_methods = {
            name
            for name, method in inspect.getmembers(BaseLLM, predicate=inspect.isfunction)
            if getattr(method, "__isabstractmethod__", False)
        }
        expected = {"invoke", "ainvoke", "stream", "bind_tools"}
        assert abstract_methods == expected
