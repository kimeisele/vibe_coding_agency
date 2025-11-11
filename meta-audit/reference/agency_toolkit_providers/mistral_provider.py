"""Mistral AI text generation provider implementation."""

import logging
import os
from typing import Any

from agency_toolkit.core.resilience import (
    rate_limit_mistral,
    require_network,
    with_retry,
)
from agency_toolkit.providers.base import TextProvider

logger = logging.getLogger(__name__)

VALID_MODELS = [
    "mistral-tiny",
    "mistral-small-latest",
    "mistral-medium",
    "mistral-large-latest",
]


class MistralProvider(TextProvider):
    """Mistral AI text generation provider."""

    def __init__(self, api_key: str | None = None):
        """Initialize Mistral provider.

        Args:
            api_key: Optional API key. If not provided, reads from
                MISTRAL_API_KEY env var.

        Raises:
            ValueError: If API key not found.
            ImportError: If mistralai package not installed.
        """
        try:
            from mistralai import Mistral
        except ImportError as e:
            raise ImportError(
                "Mistral AI SDK not found. Install with:\n"
                "  pip install agency-toolkit[mistral]"
            ) from e

        self.api_key = api_key or self._get_api_key()
        self.client = Mistral(api_key=self.api_key)

    def _get_api_key(self) -> str:
        """Get MISTRAL_API_KEY from environment.

        Returns:
            API key string.

        Raises:
            ValueError: If API key not found with setup instructions.
        """
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            error_msg = """
MISTRAL_API_KEY not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export MISTRAL_API_KEY='your-key-here'

  # Or add to your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export MISTRAL_API_KEY="your-key"' >> ~/.zshrc
  source ~/.zshrc

Get your key at: https://console.mistral.ai/
            """.strip()
            raise ValueError(error_msg)
        return api_key

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate text from prompt using Mistral API.

        Args:
            prompt: Text prompt for generation
            model: Model identifier (defaults to mistral-small-latest)
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt for the conversation

        Returns:
            dict with response, model, temperature, max_tokens, timestamp, provider

        Raises:
            ValueError: If invalid model specified
            Exception: For API errors with specific user-friendly messages
        """
        from datetime import datetime

        # Default model
        if model is None:
            model = "mistral-small-latest"

        # Validate model
        if model not in VALID_MODELS:
            raise ValueError(
                f"Invalid model '{model}'. Valid options: {', '.join(VALID_MODELS)}"
            )

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Apply rate limiting
        rate_limit_mistral()

        # Define API call with retry logic
        @with_retry(max_attempts=3, backoff_factor=2.0)
        @require_network
        def _make_api_call():
            return self.client.chat.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        try:
            chat_response = _make_api_call()
            response_content = chat_response.choices[0].message.content

            return {
                "response": response_content,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat(),
                "provider": "mistral",
            }

        except Exception as e:
            self._handle_api_error(e)
            raise

    def _handle_api_error(self, error: Exception) -> None:
        """Handle API errors with specific messages.

        Args:
            error: The exception raised by the API.

        Raises:
            Exception: Re-raises with user-friendly message.
        """
        error_str = str(error).lower()

        # Rate limit error
        if "rate limit" in error_str or "429" in error_str:
            raise Exception(
                "Rate limit exceeded. Wait a few seconds or upgrade your Mistral plan."
            ) from error

        # Timeout error
        if "timeout" in error_str:
            raise Exception(
                "Mistral API timeout. Check your internet connection and try again."
            ) from error

        # Server error (5xx)
        if "500" in error_str or "502" in error_str or "503" in error_str:
            raise Exception(
                f"Mistral API server error: {error}. Try again in a few minutes."
            ) from error

        # Invalid request (model name, parameters, etc.)
        if "invalid" in error_str or "400" in error_str:
            raise Exception(
                f"Invalid request to Mistral API: {error}\n"
                f"Valid models: {', '.join(VALID_MODELS)}"
            ) from error

        # Generic error
        logger.error(f"Mistral API error: {error}", exc_info=True)
        raise Exception(f"Mistral API call failed: {error}") from error

    def estimate_cost(self, prompt_tokens: int, max_tokens: int) -> float:
        """Estimate cost for a Mistral API request.

        Args:
            prompt_tokens: Estimated number of input tokens
            max_tokens: Maximum output tokens

        Returns:
            float: Estimated cost in USD
        """
        # Mistral pricing (approximate, as of 2024):
        # mistral-small: $0.001/1K input, $0.003/1K output
        input_cost = (prompt_tokens / 1000) * 0.001
        output_cost = (max_tokens / 1000) * 0.003
        return input_cost + output_cost

    def get_available_models(self) -> list[str]:
        """Get list of available Mistral models.

        Returns:
            list: Model identifiers
        """
        return VALID_MODELS.copy()

    def enhance_image_prompt(self, concept: str) -> str:
        """Enhance a simple concept into an optimized image generation prompt.

        Args:
            concept: Simple concept description for image generation

        Returns:
            str: Enhanced prompt optimized for image generation

        Raises:
            AIProviderError: If prompt enhancement fails
        """
        from agency_toolkit.exceptions import AIProviderError

        system_prompt = """You are an expert at writing detailed, vivid prompts for AI image generation.
Your task is to transform a simple concept into a rich, descriptive prompt that will generate high-quality images.

Guidelines:
- Include specific visual details (colors, textures, lighting, composition)
- Add artistic style references if appropriate (e.g., "in the style of...")
- Specify mood and atmosphere
- Keep it concise but descriptive (1-3 sentences max)
- Focus on what should be SHOWN, not what should be avoided
- Make the image feel professional and polished"""

        try:
            result = self.generate(
                prompt=concept,
                system_prompt=system_prompt,
                model="mistral-small-latest",
                temperature=0.7,
                max_tokens=200,
            )
            return result["response"].strip()
        except Exception as e:
            logger.error(f"Failed to enhance image prompt for concept '{concept}': {e}")
            raise AIProviderError(f"Image prompt enhancement failed: {e}") from e
