"""Work unit data collection for the steward context command.

PERFORMANCE: SQLAlchemy imports are lazy-loaded.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

import yaml


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


def get_active_wu(session: "Session") -> dict[str, Any] | None:
    """Get active work unit from current steward session."""
    try:
        # LAZY IMPORT: Only load steward.db when needed (WU-ARCH-001B)
        from ...db import get_active_session

        active = get_active_session(session)
        if not active or not active.active_work_unit_id:
            return None

        wu_file = Path(f"work_units/{active.active_work_unit_id}.yaml")
        if not wu_file.exists():
            # FIX P1-003: Return a dict with error info instead of None
            # This prevents TypeError when caller tries to access dict keys
            logger.warning(
                f"WU file not found: {wu_file} (cleaning stale session {active.id})"
            )
            active.active_work_unit_id = None  # Clear stale reference
            session.commit()
            # Return error dict instead of None for consistent API
            return {
                "id": "WU-MISSING",
                "title": "Unknown (file not found)",
                "status": "UNKNOWN",
                "test_status": "N/A (file missing)",
                "error": f"Work unit file not found: {wu_file}",
            }

        with wu_file.open() as f:
            wu_data = yaml.safe_load(f)

        # Test status: use 'phoenix test coverage' or 'pytest' separately
        # Removed slow subprocess check (was adding 5s latency to context)
        test_status = "Run 'pytest' to check"

        return {
            "id": active.active_work_unit_id,
            "title": wu_data.get("title", "Unknown"),
            "status": wu_data.get("status", "UNKNOWN"),
            "test_status": test_status,
        }
    except Exception as e:
        logger.error(f"Failed to get active WU: {e}")
        return None


def get_blockers(skip: bool = True) -> list[dict[str, str]]:
    """Extract blockers from WU files.

    Args:
        skip: If True, skip blocker analysis for performance (default: True).
              Set to False to enable blocker scanning (adds ~7.5s).

    Returns:
        List of blocker dictionaries with wu_id and reason.
    """
    # Performance optimization: Skip by default (saves 7.5s parsing 108 YAML files)
    if skip:
        return []

    blockers: List[Dict[str, str]] = []

    wu_dir = Path("work_units")

    if not wu_dir.exists():
        return blockers

    try:
        for wu_file in wu_dir.glob("WU-*.yaml"):
            try:
                with open(wu_file) as f:
                    wu = yaml.safe_load(f)

                if wu and wu.get("status") == "BLOCKED":
                    reason = wu.get("blocked_reason", "Unknown")

                    blockers.append(
                        {
                            "wu_id": wu.get("id", wu_file.stem),
                            "reason": reason,
                        }
                    )

            except Exception as e:
                logger.warning(f"Failed to parse {wu_file}: {e}")

                continue

    except Exception as e:
        logger.error(f"Failed to scan for blockers: {e}")

    return blockers


def get_wu_metrics(wu_id: str) -> dict[str, Any]:
    """Get metrics for a work unit.

    Returns test count, complexity score, lines of code.
    Uses cached results if available (max 5 min old).

    OPTIMIZATION: Disabled expensive subprocess calls (radon, find).
    These add 2-3s to context generation. Metrics are optional.
    """
    metrics = {
        "test_count": 0,
        "test_passed": 0,
        "test_failed": 0,
        "complexity_score": 0.0,
        "complexity_level": "UNKNOWN",
        "lines_of_code": 0,
    }

    # All metrics collection is disabled for performance.
    # These calls were taking 2-3s and aren't critical for context.
    # Use dedicated commands for detailed metrics:
    #   - pytest for tests
    #   - radon mi for complexity
    #   - find for LOC

    return metrics


def get_next_commands(wu_status: str) -> list[str]:
    """Get recommended next commands based on WU status.

    Smart recommendations:
    - IN_PROGRESS: Run tests + lint
    - REVIEW: Run tests + complexity check
    - COMPLETED: Run full quality gate
    """
    commands = []

    if wu_status == "IN_PROGRESS":
        commands = [
            "make test-fast       # Run tests in parallel",
            "make lint            # Check code style",
            "phoenix rag ingest   # Update knowledge base",
        ]
    elif wu_status == "REVIEW":
        commands = [
            "make check           # Full linting + formatting",
            "make test-cov        # Coverage analysis",
            "phoenix audit run    # System health check",
        ]
    elif wu_status == "COMPLETED":
        commands = [
            "make quality-gate    # Full quality checks",
            "phoenix steward handover  # Create summary",
        ]
    else:
        commands = [
            "phoenix work-unit list    # See available work",
            "phoenix steward context   # Refresh context",
        ]

    return commands
