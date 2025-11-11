"""Ollama local text generation provider implementation."""

import logging
from typing import Any

import requests

from agency_toolkit.providers.base import TextProvider

logger = logging.getLogger(__name__)

VALID_MODELS = [
    "llama3.2",
    "llama3.1",
    "mistral",
    "codellama",
    "phi3",
]


class OllamaProvider(TextProvider):
    """Ollama local text generation provider (free, runs locally)."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama provider.

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate text from prompt using Ollama API.

        Args:
            prompt: Text prompt for generation
            model: Model identifier (defaults to llama3.2)
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt for the conversation

        Returns:
            dict with response, model, temperature, max_tokens, timestamp, provider

        Raises:
            ConnectionError: If Ollama server is not running
            Exception: For API errors
        """
        from datetime import datetime

        # Default model
        if model is None:
            model = "llama3.2"

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Call Ollama chat API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=120,  # Ollama can be slow on first run
            )
            response.raise_for_status()

            data = response.json()
            response_content = data["message"]["content"]

            return {
                "response": response_content,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat(),
                "provider": "ollama",
            }

        except requests.ConnectionError as e:
            raise ConnectionError(
                f"Could not connect to Ollama server at {self.base_url}. "
                "Is Ollama running? Install: https://ollama.ai"
            ) from e
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(
                    f"Model '{model}' not found. "
                    f"Pull it first with: ollama pull {model}"
                ) from e
            raise Exception(f"Ollama API error: {e}") from e
        except Exception as e:
            logger.error(f"Ollama API error: {e}", exc_info=True)
            raise Exception(f"Ollama API call failed: {e}") from e

    def estimate_cost(self, prompt_tokens: int, max_tokens: int) -> float:
        """Estimate cost for Ollama request (always free).

        Args:
            prompt_tokens: Estimated number of input tokens
            max_tokens: Maximum output tokens

        Returns:
            float: Always 0.0 (Ollama is free)
        """
        return 0.0

    def get_available_models(self) -> list[str]:
        """Get list of commonly available Ollama models.

        Returns:
            list: Model identifiers
        """
        return VALID_MODELS.copy()
