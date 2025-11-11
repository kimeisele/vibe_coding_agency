"""Google Generative AI text generation provider implementation."""

import logging
import os
from typing import Any

from agency_toolkit.core.resilience import require_network, with_retry
from agency_toolkit.providers.base import TextProvider

logger = logging.getLogger(__name__)

# Valid Google Gemini models as of 2024
# See: https://ai.google.dev/gemini-api/docs/models/gemini
VALID_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-2.0-flash-exp",
]


class GoogleProvider(TextProvider):
    """Google Generative AI text generation provider."""

    def __init__(self, api_key: str | None = None):
        """Initialize Google GenAI provider.

        Args:
            api_key: Optional API key. If not provided, reads from
                GOOGLE_API_KEY env var.

        Raises:
            ValueError: If API key not found.
            ImportError: If google-generativeai package not installed.
        """
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise ImportError(
                "Google GenAI SDK not found. Install with:\n"
                "  pip install agency-toolkit[google]"
            ) from e

        self.api_key = api_key or self._get_api_key()
        genai.configure(api_key=self.api_key)
        self._genai = genai

    def _get_api_key(self) -> str:
        """Get GOOGLE_API_KEY from environment.

        Returns:
            API key string.

        Raises:
            ValueError: If API key not found with setup instructions.
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            error_msg = """
GOOGLE_API_KEY not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export GOOGLE_API_KEY='your-key-here'

  # Or add to your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export GOOGLE_API_KEY="your-key"' >> ~/.zshrc
  source ~/.zshrc

Get your key at: https://makersuite.google.com/app/apikey
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
        """Generate text from prompt using Google GenAI API.

        Args:
            prompt: Text prompt for generation
            model: Model identifier (defaults to gemini-1.5-flash)
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

        # Default model (using latest stable flash model)
        if model is None:
            model = "gemini-2.5-flash"

        # Validate model
        if model not in VALID_MODELS:
            raise ValueError(
                f"Invalid model '{model}'. " f"Valid models: {', '.join(VALID_MODELS)}"
            )

        # Build full prompt with system context if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Define API call with retry logic
        @with_retry(max_attempts=3, backoff_factor=2.0)
        @require_network
        def _make_api_call():
            model_instance = self._genai.GenerativeModel(
                model_name=model,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return model_instance.generate_content(full_prompt)

        try:
            response = _make_api_call()
            response_content = response.text

            return {
                "response": response_content,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat(),
                "provider": "google",
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
        if "quota" in error_str or "429" in error_str:
            raise Exception(
                "Google API quota exceeded. Check your billing or try again later."
            ) from error

        # Timeout error
        if "timeout" in error_str:
            raise Exception(
                "Google API timeout. Check your internet connection and try again."
            ) from error

        # Server error (5xx)
        if "500" in error_str or "502" in error_str or "503" in error_str:
            raise Exception(
                f"Google API server error: {error}. Try again in a few minutes."
            ) from error

        # Invalid request or model not found
        if (
            "invalid" in error_str
            or "400" in error_str
            or "404" in error_str
            or "not found" in error_str
        ):
            raise Exception(
                f"Invalid request to Google API: {error}\n"
                f"Valid models: {', '.join(VALID_MODELS)}"
            ) from error

        # Generic error
        logger.error(f"Google API error: {error}", exc_info=True)
        raise Exception(f"Google API call failed: {error}") from error

    def estimate_cost(self, prompt_tokens: int, max_tokens: int) -> float:
        """Estimate cost for a Google GenAI API request.

        Args:
            prompt_tokens: Estimated number of input tokens
            max_tokens: Maximum output tokens

        Returns:
            float: Estimated cost in USD
        """
        # Google GenAI pricing (approximate, as of 2024):
        # Gemini 1.5 Flash: $0.00001875/1K input, $0.000075/1K output
        input_cost = (prompt_tokens / 1000) * 0.00001875
        output_cost = (max_tokens / 1000) * 0.000075
        return input_cost + output_cost

    def get_available_models(self) -> list[str]:
        """Get list of available Google GenAI models.

        Returns:
            list: Model identifiers
        """
        return VALID_MODELS.copy()
