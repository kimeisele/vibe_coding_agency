"""Base classes for task handler plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TaskContext:
    """Execution context for a task.

    Provides type-safe access to configuration, previous task outputs,
    and archetype/solution metadata.

    Attributes:
        config: Global Config object
        step_context: Outputs from previous tasks (e.g., {"tagline": "..."})
        raw_context: Unformatted context with original types (lists, dicts, etc.)
                     Used to pass structured data between tasks
        archetype_id: Current archetype being processed (optional)
        solution_id: Current solution being executed (optional)
        project_name: Project name if available
        ai_provider: AI provider name if specified
    """

    config: Any  # Config type from models
    step_context: dict[str, Any]
    raw_context: dict[str, Any]  # Unformatted context with original types
    archetype_id: str | None = None
    solution_id: str | None = None
    project_name: str | None = None
    ai_provider: str | None = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from step_context with fallback."""
        return self.step_context.get(key, default)

    def get_raw(self, key: str, default: Any = None) -> Any:
        """Get raw (unformatted) value from raw_context with fallback.

        Use this to access structured data like lists or dicts that
        should not be stringified. Useful for passing data between tasks.

        Args:
            key: Key to look up
            default: Default value if key not found

        Returns:
            Raw value from raw_context, preserving its original type
        """
        return self.raw_context.get(key, default)


class TaskHandler(ABC):
    """Base class for all task handlers (Strategy Pattern).

    Task handlers implement the logic for specific task types in the
    GRAND AGENCY OS workflow system. Each handler validates parameters
    and executes the task with access to the execution context.

    Example:
        class MyTaskHandler(TaskHandler):
            @property
            def name(self) -> str:
                return "mytask"

            def validate_params(self, params: dict) -> None:
                if "required_field" not in params:
                    raise ValueError("Missing required_field")

            def execute(self, params: dict, context: TaskContext) -> dict:
                # Implementation here
                return {"result": "success"}
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique task name (e.g., 'ai', 'social', 'briefing')."""
        pass

    @abstractmethod
    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate params before execution (fail-fast).

        Args:
            params: Task parameters from JSON

        Raises:
            ValueError: If params are invalid or missing required fields
        """
        pass

    @abstractmethod
    def execute(
        self, params: dict[str, Any], context: TaskContext
    ) -> dict[str, Any] | str | Any:
        """Execute the task.

        Args:
            params: Task parameters (already validated)
            context: Execution context with config and step outputs

        Returns:
            Task output (will be stored in step_context if output_key is set)
        """
        pass
