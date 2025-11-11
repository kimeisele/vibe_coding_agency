"""AI task handler for text generation."""

from __future__ import annotations

import logging
from typing import Any

from agency_toolkit.tasks.base import TaskContext, TaskHandler

logger = logging.getLogger(__name__)


class AITaskHandler(TaskHandler):
    """Task handler for AI text generation using various providers."""

    @property
    def name(self) -> str:
        return "ai"

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate AI task parameters.

        Args:
            params: Task parameters

        Raises:
            ValueError: If required parameters are missing
        """
        # Check for prompt (can be "prompt" or "prompt_template")
        has_prompt = "prompt" in params or "prompt_template" in params
        if not has_prompt:
            raise ValueError("AI task requires 'prompt' or 'prompt_template' parameter")

    def execute(
        self, params: dict[str, Any], context: TaskContext
    ) -> dict[str, Any] | str:
        """Execute AI text generation.

        Args:
            params: Task parameters (prompt, model, temperature, etc.)
            context: Execution context

        Returns:
            Generated text string

        Raises:
            ValueError: If provider initialization fails
        """
        from agency_toolkit.providers import get_text_provider

        # Extract parameters
        prompt_template = params.get("prompt_template") or params.get("prompt", "")
        provider_name = params.get("provider", context.ai_provider or "mistral")
        model = params.get("model")
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 500)
        system_prompt = params.get("system_prompt")

        # Get provider
        try:
            provider_class = get_text_provider(provider_name)
            provider = provider_class()
        except Exception as e:
            raise ValueError(
                f"Failed to initialize AI provider '{provider_name}': {e}"
            ) from e

        # Generate text
        result = provider.generate(
            prompt=prompt_template,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        # Return just the response text (not the full result dict)
        return result.get("response", "")


# Auto-register at module load
from agency_toolkit.tasks.registry import register_task_handler

register_task_handler(AITaskHandler)
