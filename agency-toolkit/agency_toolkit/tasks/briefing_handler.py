"""Briefing task handler for document generation."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any

from agency_toolkit.tasks.base import TaskContext, TaskHandler

logger = logging.getLogger(__name__)


class BriefingTaskHandler(TaskHandler):
    """Task handler for briefing document generation."""

    @property
    def name(self) -> str:
        return "briefing"

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate briefing task parameters.

        Args:
            params: Task parameters

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Briefing can work with defaults from context
        if "format_type" in params:
            valid_formats = ["pdf", "md"]
            if params["format_type"] not in valid_formats:
                raise ValueError(
                    f"Invalid format_type '{params['format_type']}'. "
                    f"Valid: {', '.join(valid_formats)}"
                )

    def execute(self, params: dict[str, Any], context: TaskContext) -> dict[str, Any]:
        """Execute briefing document generation.

        Args:
            params: Task parameters (client_name, project_name, type, etc.)
            context: Execution context

        Returns:
            Briefing generation result
        """
        from agency_toolkit.core.briefing import BriefingData
        from agency_toolkit.core.briefing import generate as generate_briefing

        # Extract parameters with context fallbacks
        project_name = context.project_name or "Project"
        format_type = params.get("format_type", "pdf")
        output_dir = Path(params.get("output_dir", "./output/briefings"))

        # Build BriefingData from context
        goals = context.get("goals", [])
        objectives_str = "; ".join(goals) if isinstance(goals, list) else str(goals)

        # Normalize project_type to valid enum value
        solution_name = context.get("solution_name", "Other")
        project_type_map = {
            "web": "Web",
            "print": "Print",
            "social": "Social",
            "video": "Video",
        }
        project_type = "Other"
        for key, value in project_type_map.items():
            if key.lower() in solution_name.lower():
                project_type = value
                break

        briefing_data = BriefingData(
            client_name=params.get("client_name", context.project_name or "Client"),
            project_name=params.get("project_name", project_name),
            project_type=params.get("type", project_type),
            objectives=objectives_str,
            target_audience=params.get("target_audience", "General audience"),
            deliverables=params.get("deliverables", ["Website", "Branding"]),
            deadline=params.get("deadline", date(2024, 12, 31)),
            budget=(
                float(params.get("budget", 0))
                if params.get("budget") != "TBD"
                else None
            ),
            notes=params.get("notes", "Generated via GRAND AGENCY OS"),
        )

        return generate_briefing(
            briefing_data=briefing_data,
            format_type=format_type,
            output_dir=output_dir,
            dry_run=params.get("dry_run", False),
            step_context=context.step_context,
        )


# Auto-register at module load
from agency_toolkit.tasks.registry import register_task_handler

register_task_handler(BriefingTaskHandler)
