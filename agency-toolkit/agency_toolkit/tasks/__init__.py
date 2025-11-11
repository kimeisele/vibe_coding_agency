"""Task handler plugin system for the GRAND AGENCY OS.

This module provides a plugin architecture for task handlers, similar to
the provider system. Each task type (ai, social, briefing, structure) has
its own handler class that implements the TaskHandler interface.
"""

# Import handlers to trigger auto-registration
from agency_toolkit.tasks import (
    ai_handler,  # noqa: F401
    briefing_handler,  # noqa: F401
    image_handler,  # noqa: F401
    social_handler,  # noqa: F401
    structure_handler,  # noqa: F401
)
from agency_toolkit.tasks.base import TaskContext, TaskHandler
from agency_toolkit.tasks.registry import (
    get_task_handler,
    list_task_handlers,
    register_task_handler,
)

__all__ = [
    "TaskHandler",
    "TaskContext",
    "register_task_handler",
    "get_task_handler",
    "list_task_handlers",
]
