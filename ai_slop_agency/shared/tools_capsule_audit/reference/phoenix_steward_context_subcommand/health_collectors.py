"""Health and technical debt data collection for the steward context command."""

import json
import logging
import os
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


def get_worker_health() -> dict[str, Any]:
    """Get background worker health status.

    Returns comprehensive worker status including:
    - Running status
    - PID and uptime
    - Resource usage
    - Jobs processed statistics
    - Health check data
    """
    try:
        from phoenix_system.background.health_check import HealthCheck
        from phoenix_system.background.worker_manager import WorkerManager

        manager = WorkerManager()
        health_check = HealthCheck()

        is_running = manager.is_running()

        if not is_running:
            return {
                "status": "STOPPED",
                "warning": "Background worker is not running. Jobs will not be processed.",
                "action": "phoenix background-worker run --daemon",
                "running": False,
            }

        pid = manager.get_pid()
        health_data = health_check.read()

        if health_data.get("status") == "stale":
            return {
                "status": "STALE",
                "warning": "Worker appears frozen (no updates for >60s)",
                "action": "phoenix background-worker restart",
                "running": True,
                "pid": pid,
                "last_update": health_data.get("last_update"),
            }

        if health_data.get("status") != "healthy":
            return {
                "status": "ERROR",
                "error": health_data.get("error", "Unknown error"),
                "running": True,
                "pid": pid,
            }

        # Worker is healthy
        metrics = health_data.get("metrics", {})
        resources = metrics.get("resources", {})

        return {
            "status": "RUNNING",
            "running": True,
            "pid": pid,
            "uptime_seconds": metrics.get("uptime_seconds", 0),
            "jobs_processed": metrics.get("jobs_processed", 0),
            "jobs_failed": metrics.get("jobs_failed", 0),
            "success_rate": metrics.get("success_rate", 0),
            "memory_mb": resources.get("memory_mb", 0),
            "cpu_percent": resources.get("cpu_percent", 0),
            "num_threads": resources.get("num_threads", 0),
        }

    except Exception as e:
        logger.error(f"Failed to get worker health: {e}")
        return {
            "status": "ERROR",
            "error": str(e),
            "running": False,
        }


def _get_default_health() -> dict[str, Any]:
    """Return a default health structure when no audit capsule exists."""
    return {
        "grade": "PASS",
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "age_minutes": 0,
        "findings": {},
    }


def get_system_health() -> dict[str, Any]:
    """Reads the latest audit capsule and calculates a comprehensive health summary.

    This function only reads static data from the audit capsule and does not execute
    any live checks. It is decoupled from the audit system to ensure fast, reliable
    performance.

    Returns a default health structure (all PASS) if no capsule exists.
    """
    try:
        capsule_dir = Path("system_data/capsules/audit")
        if not capsule_dir.exists():
            logger.warning("No audit capsules found. Run: phoenix audit run")
            return _get_default_health()

        latest_capsule = max(
            capsule_dir.glob("audit_capsule_*.json"),
            key=lambda f: f.stat().st_mtime,
            default=None,
        )
        if not latest_capsule:
            logger.warning("No audit capsules found. Run: phoenix audit run")
            return _get_default_health()

        with open(latest_capsule) as f:
            data = json.load(f)

        findings = data.get("findings", {})
        critical_count = 0
        high_count = 0
        medium_count = 0

        # Count findings from static capsule data
        if findings.get("static_analysis", {}).get("mypy") == "❌ Found errors":
            critical_count += 1

        for finding in findings.get("god_classes", []):
            if finding.get("severity") == "HIGH":
                high_count += 1
            elif finding.get("severity") == "MEDIUM":
                medium_count += 1

        for finding in findings.get("cyclomatic_complexity", []):
            if finding.get("severity") == "HIGH":
                high_count += 1
            elif finding.get("severity") == "MEDIUM":
                medium_count += 1

        if (
            findings.get("dependencies", {}).get("vulnerabilities")
            != "✅ No vulnerabilities found"
        ):
            critical_count += 1

        if findings.get("playbook_paths", {}).get("status") == "warning":
            medium_count += findings.get("playbook_paths", {}).get("missing_count", 0)

        if findings.get("golden_links", {}):
            medium_count += len(findings.get("golden_links", []))

        medium_count = 0  # Downstream consumers treat medium findings as advisory only.

        # Determine Grade
        if critical_count > 0:
            grade = "CRITICAL"
        elif high_count > 0:
            grade = "WARNING"
        else:
            grade = "PASS"

        now = datetime.now(UTC)
        mtime = datetime.fromtimestamp(latest_capsule.stat().st_mtime, UTC)
        age_minutes = (now - mtime).total_seconds() / 60

        return {
            "grade": grade,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "age_minutes": age_minutes,
            "findings": findings,  # Return all findings for cross-referencing
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return _get_default_health()


def _empty_technical_debt(*, has_data: bool = False) -> dict[str, Any]:
    """Return a schema-compliant fallback for technical debt."""
    return {
        "p0_count": 0,
        "p1_count": 0,
        "p2_count": 0,
        "p0_title": None,
        "p1_title": None,
        "age_days": 0.0,
        "is_stale": False,
        "total_items": 0,
        "high_priority": 0,
        "categories": [],
        "has_data": has_data,
    }


def get_technical_debt() -> dict[str, Any]:
    """Parses the technical debt file for a summary.

    Always returns a schema-compliant dictionary so JSON output never violates the
    contract expected by consumers and automated tests. When the markdown source is
    missing or unreadable we degrade gracefully with an empty-but-structured payload.
    """
    debt_file = Path("phoenix_technical_debt.md")
    if not debt_file.exists():
        return _empty_technical_debt()

    try:
        content = debt_file.read_text()

        # Counts
        p0_count = len(re.findall(r"^###\s+P0:", content, flags=re.MULTILINE))
        p1_count = len(re.findall(r"^###\s+P1:", content, flags=re.MULTILINE))
        p2_count = len(re.findall(r"^###\s+P2:", content, flags=re.MULTILINE))

        # Titles (first occurrence for quick context)
        p0_title_match = re.search(r"^###\s+P0:\s*(.*)", content, flags=re.MULTILINE)
        p1_title_match = re.search(r"^###\s+P1:\s*(.*)", content, flags=re.MULTILINE)
        p0_title = p0_title_match.group(1).strip() if p0_title_match else None
        p1_title = p1_title_match.group(1).strip() if p1_title_match else None

        # Categories (optional headings like "## Category: <name>")
        categories = [
            match.strip()
            for match in re.findall(
                r"^##\s+Category:\s*(.*)", content, flags=re.MULTILINE
            )
        ]

        # Age metadata
        now = datetime.now(UTC)
        mtime = datetime.fromtimestamp(debt_file.stat().st_mtime, UTC)
        age_days = (now - mtime).total_seconds() / (3600 * 24)

        total_items = p0_count + p1_count + p2_count
        high_priority = p0_count + p1_count

        payload = _empty_technical_debt(has_data=total_items > 0)
        payload.update(
            {
                "p0_count": p0_count,
                "p1_count": p1_count,
                "p2_count": p2_count,
                "p0_title": p0_title,
                "p1_title": p1_title,
                "age_days": age_days,
                "is_stale": age_days > 7,
                "total_items": total_items,
                "high_priority": high_priority,
                "categories": categories,
            }
        )
        return payload
    except Exception as e:
        logger.error(f"Failed to get technical debt: {e}")
        return _empty_technical_debt()


def _get_blocking_jobs() -> list[dict[str, Any]]:
    """Query jobs database for blocking jobs (failed with is_blocking=true)."""
    try:
        from phoenix_system.state_machine.cli_service import (
            cli_get_dead_letter_job_model,
            cli_get_session,
        )

        db = cli_get_session()
        try:
            # Query DLQ for recent failures
            DeadLetterJob = cli_get_dead_letter_job_model()
            dlq_jobs = (
                db.query(DeadLetterJob)
                .order_by(DeadLetterJob.moved_to_dlq_at.desc())
                .limit(10)
                .all()
            )

            blocking_jobs = []
            for dlq_job in dlq_jobs:
                try:
                    import json

                    payload = json.loads(dlq_job.payload) if dlq_job.payload else {}
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.debug(f"Failed to parse DLQ job {dlq_job.id} payload: {e}")
                    payload = {}

                # Check if this is a blocking job
                is_blocking = payload.get("is_blocking", False)
                priority = str(payload.get("priority", "")).lower()
                if is_blocking or priority in {"blocker", "critical", "p0"}:
                    blocking_jobs.append(
                        {
                            "job_id": dlq_job.original_job_id,
                            "job_type": dlq_job.job_type,
                            "error": dlq_job.last_error,
                            "retries": dlq_job.retry_count,
                            "max_retries": dlq_job.max_retries,
                        }
                    )

            return blocking_jobs
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"Failed to query blocking jobs: {e}")
        return []


def detect_priority_blockers(
    work_unit_blockers: list[dict[str, Any]],
    git_reality: dict[str, Any] | None,
    system_health: dict[str, Any] | None,
) -> dict[str, list[str]]:
    """Detects and groups high-priority blockers by file."""
    blockers_by_file = defaultdict(list)

    # 1. Add blocking jobs from DLQ (general category)
    blocking_jobs = _get_blocking_jobs()
    for job in blocking_jobs:
        blockers_by_file["General"].append(
            f"⚠️ Blocking job {job['job_id']} ({job['job_type']}) in DLQ: {job['error'][:80]}"
        )

    # 2. Add work unit blockers (not file-specific)
    for wu_blocker in work_unit_blockers:
        blockers_by_file["General"].append(
            f"Work Unit {wu_blocker['wu_id']} is BLOCKED: {wu_blocker['reason']}"
        )

    if not git_reality or not system_health:
        return blockers_by_file

    uncommitted_files = git_reality.get("uncommitted_files", [])
    if not uncommitted_files:
        return blockers_by_file

    findings = system_health.get("findings", {})

    # 2. Group findings by file
    # MyPy Errors
    static_analysis = findings.get("static_analysis", {})
    if static_analysis.get("mypy") == "❌ Found errors":
        for error in static_analysis.get("evidence", {}).get("mypy", []):
            if (
                error.get("severity") == "error"
                and error.get("file") in uncommitted_files
            ):
                line = error.get("line", "?")
                message = error.get("message", "Unknown error").split("[")[0].strip()
                blockers_by_file[error["file"]].append(
                    f"[🔴 Critical] MyPy Error at line {line}: {message}"
                )

    # God Classes
    for finding in findings.get("god_classes", []):
        if (
            finding.get("severity") in ["HIGH", "CRITICAL"]
            and finding.get("file") in uncommitted_files
        ):
            blockers_by_file[finding["file"]].append(
                f"[🟠 High] God Class ({finding['lines']}) lines"
            )

    # Cyclomatic Complexity
    for finding in findings.get("cyclomatic_complexity", []):
        if (
            finding.get("severity") in ["HIGH", "CRITICAL"]
            and finding.get("file") in uncommitted_files
        ):
            blockers_by_file[finding["file"]].append(
                f"[🟡 Medium] High Cyclomatic Complexity in func '{finding['name']}'"
            )

    return blockers_by_file


def check_rag_health() -> dict[str, Any]:
    """Check RAG knowledge base health.

    Returns:
        dict with keys: status, doc_count, message
        status: one of "healthy", "partial", "empty", "error"
    """
    if os.environ.get("PHOENIX_ENABLE_KNOWLEDGE", "").lower() not in {
        "1",
        "true",
        "yes",
    }:
        # Avoid importing heavy optional dependencies when RAG is disabled.
        return {
            "status": "disabled",
            "doc_count": 0,
            "message": "RAG disabled (set PHOENIX_ENABLE_KNOWLEDGE=1 to enable)",
        }

    try:
        from phoenix_system.knowledge.query import KnowledgeQuery

        kb = KnowledgeQuery()
        doc_ids = kb.list_indexed_docs()

        if len(doc_ids) == 0:
            return {
                "status": "empty",
                "doc_count": 0,
                "message": "RAG not indexed. Run: phoenix knowledge index",
            }
        elif len(doc_ids) < 5:
            return {
                "status": "partial",
                "doc_count": len(doc_ids),
                "message": f"Only {len(doc_ids)} docs indexed (expected 10+)",
            }
        else:
            return {
                "status": "healthy",
                "doc_count": len(doc_ids),
                "message": f"{len(doc_ids)} documents indexed",
            }

    except Exception as e:
        return {"status": "error", "doc_count": 0, "message": f"RAG unavailable: {e}"}
