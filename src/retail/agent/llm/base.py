"""
Abstract base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate a chat completion from a list of messages."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available and configured correctly."""
        pass