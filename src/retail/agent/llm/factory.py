"""
LLM provider factory.
"""

from typing import Optional
from .base import LLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
# TODO: Add Anthropic and LlamaCpp providers
from retail.config.settings import settings

def create_llm_provider() -> LLMProvider:
    """
    Create an LLM provider based on the configuration.
    """
    provider = settings.LLM_PROVIDER.lower()
    if provider == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL
        )
    elif provider == "openai":
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    elif provider == "anthropic":
        # TODO: Implement AnthropicProvider
        raise NotImplementedError("Anthropic provider not implemented yet")
    elif provider == "llamacpp":
        # TODO: Implement LlamaCppProvider
        raise NotImplementedError("LlamaCpp provider not implemented yet")
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")