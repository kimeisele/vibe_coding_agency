"""Git data collection for the steward context command."""

import logging
import subprocess  # ARCH-EXEMPT: CLI tooling exception - noqa: S404
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any


logger = logging.getLogger(__name__)


def _get_branch() -> str:
    """Get current git branch (parallel task)."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception as e:
        logger.debug(f"Failed to get branch: {e}")
        return "unknown"


def _get_commits_ahead(branch: str) -> int:
    """Get commits ahead of origin (parallel task)."""
    try:
        if branch == "unknown":
            return 0

        # Try origin/{current_branch} first
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", f"^origin/{branch}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip())

        # Fallback to origin/main
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", "^origin/main"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return (
            int(result.stdout.strip())
            if result.returncode == 0 and result.stdout.strip()
            else 0
        )
    except Exception as e:
        logger.debug(f"Failed to get commits ahead: {e}")
        return 0


def _get_recent_commits() -> list[str]:
    """Get recent commits (parallel task)."""
    try:
        result = subprocess.run(
            ["git", "log", "-n", "3", "--oneline", "--pretty=format:%h %s"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return (
            result.stdout.strip().split("\n")
            if result.returncode == 0 and result.stdout.strip()
            else []
        )
    except Exception as e:
        logger.debug(f"Failed to get recent commits: {e}")
        return []


def _get_uncommitted_summary() -> list[str]:
    """Get uncommitted changes summary (parallel task)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        logger.debug(f"Failed to get uncommitted summary: {e}")
        return []


def _get_uncommitted_files() -> list[str]:
    """Get uncommitted file list (parallel task).

    Optimized: Use 'git status --short' instead of 'git ls-files' (much faster).
    """
    try:
        # git status --short is 10x faster than git ls-files
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse: "M file.py" -> "file.py"
            files = [
                line.split(None, 1)[1] for line in result.stdout.strip().split("\n")
            ]
            return files
        return []
    except Exception as e:
        logger.debug(f"Failed to get uncommitted files: {e}")
        return []


def get_git_reality() -> dict[str, Any] | None:
    """Get git status summary (parallelized).

    Runs all git operations in parallel to maximize throughput.
    """
    try:
        # Run all git operations in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            branch_future = executor.submit(_get_branch)

            # Get branch first, then use it for commits_ahead
            branch = branch_future.result(timeout=5)

            commits_ahead_future = executor.submit(_get_commits_ahead, branch)
            recent_commits_future = executor.submit(_get_recent_commits)
            uncommitted_summary_future = executor.submit(_get_uncommitted_summary)
            uncommitted_files_future = executor.submit(_get_uncommitted_files)

            return {
                "branch": branch,
                "commits_ahead": commits_ahead_future.result(timeout=5),
                "recent_commits": recent_commits_future.result(timeout=5),
                "uncommitted_summary": uncommitted_summary_future.result(timeout=5),
                "uncommitted_files": uncommitted_files_future.result(timeout=5),
            }
    except Exception as e:
        logger.error(f"Git reality check failed: {e}")
        return None
