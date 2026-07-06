"""
OpenAI LLM provider implementation.
"""

import os
from typing import Any, Dict, List, Optional
import openai
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if self.api_key:
            openai.api_key = self.api_key

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate text from a prompt using OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API key is not set.")
        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].text.strip()

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate a chat completion from a list of messages using OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API key is not set.")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content.strip()

    def is_available(self) -> bool:
        """Check if the OpenAI API key is set."""
        return bool(self.api_key)