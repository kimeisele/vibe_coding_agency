"""
Task handler for AI image generation.
Implements the image generation tool in the orchestrator workflow system.
"""

from __future__ import annotations

import logging
from typing import Any

from agency_toolkit.image_gen import generate_image
from agency_toolkit.tasks.base import TaskContext, TaskHandler
from agency_toolkit.tasks.registry import register_task_handler

logger = logging.getLogger(__name__)


class ImageTaskHandler(TaskHandler):
    """Task handler for AI image generation via orchestrator."""

    @property
    def name(self) -> str:
        """Handler name for registry."""
        return "image"

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate image generation parameters.

        Required params:
            - prompt: Text description of image to generate

        Optional params:
            - provider: Image provider ('pollinations' or 'replicate')
            - seed: Reproducibility seed
            - output_dir: Output directory path
            - dry_run: Preview without actual generation
        """
        if "prompt" not in params:
            raise ValueError("Image task requires 'prompt' parameter")

        if not params.get("prompt"):
            raise ValueError("Image task 'prompt' cannot be empty")

        if "provider" in params:
            valid_providers = ["pollinations", "replicate"]
            if params["provider"] not in valid_providers:
                raise ValueError(
                    f"Invalid provider '{params['provider']}'. "
                    f"Valid options: {', '.join(valid_providers)}"
                )

    def execute(self, params: dict[str, Any], context: TaskContext) -> str:
        """Execute image generation task.

        Args:
            params: Task parameters (prompt, provider, seed, etc.)
            context: Orchestrator context (for accessing previous outputs)

        Returns:
            str: File path to generated image

        Raises:
            ValueError: If prompt is empty or provider invalid
        """
        prompt = params.get("prompt")
        provider = params.get("provider", "pollinations")
        seed = params.get("seed")

        logger.info(
            f"ImageTaskHandler.execute: "
            f"prompt='{prompt[:50]}...' "
            f"provider='{provider}' "
            f"seed={seed}"
        )

        # Call core image generation function
        result = generate_image(
            prompt=prompt,
            provider=provider,
            seed=seed,
            config=context.config,
        )

        # Return file path (will be stored in step_context as string)
        output_path = result.get("path")

        if not output_path:
            raise ValueError("Image generation failed: no output path returned")

        logger.info(f"ImageTaskHandler: Image generated at {output_path}")
        return str(output_path)


# Auto-register this handler in the task registry
register_task_handler(ImageTaskHandler)
