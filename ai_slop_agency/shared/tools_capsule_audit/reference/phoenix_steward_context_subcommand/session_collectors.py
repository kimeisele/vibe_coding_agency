"""Session data collection for the steward context command.

PERFORMANCE: SQLAlchemy imports are lazy-loaded.
"""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


def get_last_session_age(session: "Session") -> str:
    """Get the age of the most recent steward session."""
    try:
        # LAZY IMPORT: Avoid SQLAlchemy table creation on module load (CF-006)
        from ...models import StewardSession

        last_session = (
            session.query(StewardSession)
            .order_by(StewardSession.started_at.desc())
            .first()
        )
        if not last_session:
            return "No previous sessions"

        now = datetime.now(UTC)
        started_at = last_session.started_at
        if started_at.tzinfo is None:
            from datetime import timezone

            started_at = started_at.replace(tzinfo=timezone.utc)

        delta = now - started_at
        hours = delta.total_seconds() / 3600

        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            return f"{int(hours / 24)}d ago"
    except Exception as e:
        logger.error(f"Failed to get last session age: {e}")
        return "Unknown"
