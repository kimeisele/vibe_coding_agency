"""Context generation logic for the steward context command."""

# Re-export all collector functions from specialized modules
from .git_collectors import get_git_reality
from .health_collectors import (
    detect_priority_blockers,
    get_system_health,
    get_technical_debt,
)
from .session_collectors import get_last_session_age
from .wu_collectors import get_active_wu, get_blockers


__all__ = [
    "get_git_reality",
    "get_active_wu",
    "get_blockers",
    "get_system_health",
    "get_technical_debt",
    "detect_priority_blockers",
    "get_last_session_age",
]
