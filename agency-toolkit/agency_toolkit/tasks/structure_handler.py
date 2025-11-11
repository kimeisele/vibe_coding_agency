"""Structure task handler for folder creation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agency_toolkit.tasks.base import TaskContext, TaskHandler

logger = logging.getLogger(__name__)


class StructureTaskHandler(TaskHandler):
    """Task handler for folder structure creation."""

    @property
    def name(self) -> str:
        return "structure"

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate structure task parameters.

        Args:
            params: Task parameters

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Structure can work with defaults from context
        # Support both "type" and "structure_type" for backwards compatibility
        structure_type = params.get("type") or params.get("structure_type")
        if structure_type:
            valid_types = ["web", "print", "social", "video", "app"]
            if structure_type not in valid_types:
                raise ValueError(
                    f"Invalid structure type '{structure_type}'. "
                    f"Valid: {', '.join(valid_types)}"
                )

    def execute(self, params: dict[str, Any], context: TaskContext) -> dict[str, Any]:
        """Execute folder structure creation.

        Args:
            params: Task parameters (client, project, type, base_path, etc.)
            context: Execution context

        Returns:
            Structure generation result
        """
        from agency_toolkit.core.structure.generator import (
            generate as generate_structure,
        )

        # Extract parameters with context fallbacks
        project_name = context.project_name or "Project"
        # Client: params > archetype_name > project_name > "Client"
        client = (
            params.get("client")
            or context.get("archetype_name")
            or context.project_name
            or "Client"
        )
        project = params.get("project", project_name)
        # Support both "type" and "structure_type" for backwards compatibility
        structure_type = params.get("type") or params.get("structure_type", "web")
        base_path = Path(params.get("base_path", "./output"))

        return generate_structure(
            client=client,
            project=project,
            structure_type=structure_type,
            base_path=base_path,
            dry_run=params.get("dry_run", False),
            force=params.get("force", False),
        )


# Auto-register at module load
from agency_toolkit.tasks.registry import register_task_handler

register_task_handler(StructureTaskHandler)
