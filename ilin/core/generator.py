"""LLM generation backends with streaming support."""

# Developer: Vishal Raj V, Senior Engineer

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from ilin.config import settings


class LLMBackend(ABC):
    """Abstract base for LLM generation backends."""

    @abstractmethod
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text from prompt, yielding chunks for streaming."""
        ...


class LlamaCppBackend(LLMBackend):
    """Generate text using llama.cpp GGUF models."""

    def __init__(self):
        """Initialize llama.cpp backend. Model loaded on first generate."""
        self.model = None

    def _load_model(self):
        """Load the GGUF model if not already loaded."""
        if self.model is None:
            from llama_cpp import Llama

            self.model = Llama(
                model_path=str(settings.llm_model_path),
                n_ctx=4096,
                n_threads=4,
                verbose=False,
            )

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text with llama.cpp, yielding token chunks."""
        self._load_model()
        output = self.model(
            prompt,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            stream=True,
        )
        for chunk in output:
            text = chunk["choices"][0]["text"]
            if text:
                yield text


class OpenAICompatibleBackend(LLMBackend):
    """Generate text using any OpenAI-compatible API endpoint."""

    def __init__(self):
        """Initialize OpenAI-compatible backend."""
        self.client = None

    def _get_client(self):
        """Get or create the OpenAI client."""
        if self.client is None:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                base_url=settings.llm_openai_base_url,
                api_key=settings.llm_openai_api_key or "sk-dummy",
            )
        return self.client

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text via OpenAI-compatible API with streaming."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=settings.llm_openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm_backend() -> LLMBackend:
    """Factory function to create the configured LLM backend."""
    if settings.llm_backend == "openai":
        return OpenAICompatibleBackend()
    return LlamaCppBackend()
