"""Google Generative AI text generation provider implementation."""

import logging
import os
from typing import Any

from .base import TextProvider

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
                "  pip install 'meta-audit[google]'"
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
            logger.error(f"Google API error: {e}", exc_info=True)
            raise Exception(f"Google API call failed: {e}") from e

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

    def get_audit_analysis(self, context: str) -> str:
        """
        Generates a high-level analysis of the provided context data.
        """
        system_prompt = """
You are a senior software architect with 20 years of experience, specializing in Python best practices,
code quality, and security. You are conducting a "meta-audit" of a user's project.

You have been provided with data from automated static analysis tools. Your task is to synthesize this
data into a high-level, actionable report for the user.

Focus on:
- Identifying the most critical issues.
- Explaining the *impact* of these issues in simple terms.
- Providing clear, prioritized, and actionable next steps.
- Do not just repeat the raw data. Provide genuine insight.

Analyze the following data and provide your report.
"""
        response = self.generate(
            prompt=context,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.5,
        )
        return response["response"]
