"""Social media task handler for post generation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agency_toolkit.tasks.base import TaskContext, TaskHandler

logger = logging.getLogger(__name__)


class SocialTaskHandler(TaskHandler):
    """Task handler for social media post generation."""

    @property
    def name(self) -> str:
        return "social"

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate social media task parameters.

        Args:
            params: Task parameters

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Social tasks can work with defaults, but validate types if provided
        if "style" in params:
            valid_styles = ["modern", "minimal", "bold"]
            if params["style"] not in valid_styles:
                raise ValueError(
                    f"Invalid style '{params['style']}'. "
                    f"Valid: {', '.join(valid_styles)}"
                )

        if "format" in params:
            valid_formats = ["square", "story", "landscape"]
            if params["format"] not in valid_formats:
                raise ValueError(
                    f"Invalid format '{params['format']}'. "
                    f"Valid: {', '.join(valid_formats)}"
                )

    def execute(self, params: dict[str, Any], context: TaskContext) -> dict[str, Any]:
        """Execute social media post generation.

        Args:
            params: Task parameters (text, style, color, format, etc.)
            context: Execution context

        Returns:
            Social post generation result
        """
        from agency_toolkit.core.social.generator import generate as generate_social

        # Extract parameters with defaults
        project_name = context.project_name or "Project"
        text = params.get("text", f"Announcing {project_name}")
        style = params.get("style", "modern")
        color = params.get("color", "blue")
        format_name = params.get("format", "square")
        output_dir = Path(params.get("output_dir", "./output/social"))

        # Pass bg_concept from context if it exists
        bg_concept = context.get("bg_concept")

        # Read explicit background image path from raw_context
        # (from previous image generation task, not stringified)
        background_image_path = context.get_raw("background_image_path", default=None)

        return generate_social(
            text=text,
            style=style,
            color=color,
            format_name=format_name,
            output_dir=output_dir,
            dry_run=params.get("dry_run", False),
            bg_concept=bg_concept,
            background_image_path=background_image_path,
        )


# Auto-register at module load
from agency_toolkit.tasks.registry import register_task_handler

register_task_handler(SocialTaskHandler)
