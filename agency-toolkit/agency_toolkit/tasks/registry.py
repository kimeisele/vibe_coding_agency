"""Task handler registry for dynamic task dispatch."""

from __future__ import annotations

from agency_toolkit.tasks.base import TaskHandler

# Global registry (same pattern as providers/provider_loader.py)
_TASK_HANDLERS: dict[str, type[TaskHandler]] = {}


def register_task_handler(handler_class: type[TaskHandler]) -> None:
    """Register a task handler class.

    Args:
        handler_class: TaskHandler subclass to register

    Example:
        register_task_handler(AITaskHandler)
    """
    handler_instance = handler_class()
    name = handler_instance.name
    _TASK_HANDLERS[name] = handler_class


def get_task_handler(name: str) -> TaskHandler:
    """Get a task handler instance by name.

    Args:
        name: Task name (e.g., 'ai', 'social', 'briefing', 'structure')

    Returns:
        Task handler instance ready to execute

    Raises:
        ValueError: If handler not found

    Example:
        handler = get_task_handler("ai")
        handler.validate_params(params)
        result = handler.execute(params, context)
    """
    if name not in _TASK_HANDLERS:
        available = ", ".join(sorted(_TASK_HANDLERS.keys()))
        raise ValueError(
            f"Unknown task handler: '{name}'. " f"Available handlers: {available}"
        )

    handler_class = _TASK_HANDLERS[name]
    return handler_class()


def list_task_handlers() -> list[str]:
    """List all registered task handler names.

    Returns:
        Sorted list of handler names
    """
    return sorted(_TASK_HANDLERS.keys())
