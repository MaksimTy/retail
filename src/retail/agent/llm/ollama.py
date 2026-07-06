"""
Ollama LLM provider implementation.
"""

import os
from typing import Any, Dict, List, Optional
import requests
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    """Ollama LLM provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate text from a prompt using Ollama."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any
    ) -> str:
        """Generate a chat completion from a list of messages using Ollama."""
        # Ollama's chat endpoint expects a specific format
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]

    def is_available(self) -> bool:
        """Check if the Ollama server is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False