"""Steward context utilities and helpers."""

import json
import logging
from datetime import datetime
from typing import Any


logger = logging.getLogger(__name__)


def output_context_json(
    git_reality: dict[str, Any] | None,
    active_wu: dict[str, Any] | None,
    system_health: dict[str, Any] | None,
    tech_debt: dict[str, Any] | None,
    priority_blockers: dict[str, list[str]],
    last_session_age: str,
    rag_knowledge: list[dict[str, Any]] | None = None,
    action_recommendations: list[dict[str, Any]] | None = None,
    worker_health: dict[str, Any] | None = None,
) -> None:
    """Output full context as JSON."""
    from .health_collectors import check_rag_health
    from .wu_collectors import get_next_commands, get_wu_metrics

    metrics = {}
    next_commands = []
    if active_wu:
        metrics = get_wu_metrics(active_wu.get("id", ""))
        next_commands = get_next_commands(active_wu.get("status", ""))

    active_work = None
    if active_wu:
        active_work = {
            "wu_id": active_wu.get("id"),
            "title": active_wu.get("title"),
            "status": active_wu.get("status"),
            "type": "work_unit",
            "metrics": metrics,
            "next_commands": next_commands,
        }
    elif git_reality and git_reality.get("recent_commits"):
        recent_commits = git_reality.get("recent_commits", [])
        latest_commit = recent_commits[0] if recent_commits else None

        if latest_commit:
            parts = latest_commit.split(" ", 1)
            commit_hash = parts[0] if parts else ""
            commit_message = parts[1] if len(parts) > 1 else "Recent activity"

            active_work = {
                "wu_id": None,
                "title": commit_message,
                "status": "IN_PROGRESS",
                "type": "git_activity",
                "commit_hash": commit_hash,
                "commits_ahead": git_reality.get("commits_ahead", 0),
            }

    rag_status = check_rag_health()

    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "active_work": active_work,
        "git_reality": git_reality,
        "system_health": system_health,
        "tech_debt": tech_debt,
        "priority_blockers": priority_blockers,
        "last_session_age": last_session_age,
        "worker_health": worker_health,
        "rag_status": rag_status,
        "rag_knowledge": rag_knowledge or [],
        "action_recommendations": action_recommendations or [],
    }

    print(json.dumps(output, indent=2, default=str))
