"""
Collector Registry & Parallel Execution Engine.

Pattern: All collectors are registered and executed in parallel.
Graceful degradation: If one collector fails, others continue.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

from meta_audit.core.models import AnalysisResult

logger = logging.getLogger(__name__)

# Registry of all collectors
_COLLECTORS: Dict[str, Callable] = {}


def register_collector(name: str) -> Callable:
    """Decorator to register a collector function."""

    def decorator(func: Callable) -> Callable:
        _COLLECTORS[name] = func
        return func

    return decorator


# Import and register all collectors
from .complexity import get_complexity_metrics  # noqa: E402, F401
from .security import get_security_vulnerabilities  # noqa: E402, F401
from .ai_slop import get_ai_slop_findings  # noqa: E402, F401
from .god_object import get_god_object_findings  # noqa: E402, F401

# Manually register (alternative to decorator pattern)
_COLLECTORS["complexity"] = get_complexity_metrics
_COLLECTORS["security"] = get_security_vulnerabilities
_COLLECTORS["ai_slop"] = get_ai_slop_findings
_COLLECTORS["god_object"] = get_god_object_findings


def run_all_collectors(path: str, timeout: int = 120) -> Dict[str, Any]:
    """
    Execute all registered collectors in parallel.

    Args:
        path: Root path to analyze
        timeout: Max time for all collectors (seconds)

    Returns:
        Dictionary with results from all collectors:
        {
            "collectors_data": {
                "complexity": [AnalysisResult, ...],
                "security": [AnalysisResult, ...],
                "ai_slop": [AnalysisResult, ...]
            },
            "all_findings": [AnalysisResult, ...],
            "errors": [...],
            "status": "success" | "partial_success"
        }
    """
    results: Dict[str, List[AnalysisResult]] = {}
    errors: List[Dict[str, str]] = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all collector tasks
        futures = {
            executor.submit(collector_func, path): name
            for name, collector_func in _COLLECTORS.items()
        }

        # Collect results as they complete
        for future in as_completed(futures, timeout=timeout):
            collector_name = futures[future]
            try:
                result = future.result()
                results[collector_name] = result
                logger.info(f" Collector '{collector_name}' completed successfully")
            except Exception as e:
                logger.warning(f" Collector '{collector_name}' failed: {e}")
                errors.append(
                    {
                        "collector": collector_name,
                        "error": str(e),
                    }
                )
                # Graceful degradation: return empty list to maintain structure
                results[collector_name] = []

    # Flatten all findings into a single list
    all_findings: List[AnalysisResult] = []
    for collector_name, findings in results.items():
        if isinstance(findings, list):
            all_findings.extend(findings)

    return {
        "collectors_data": results,
        "all_findings": all_findings,
        "errors": errors,
        "status": "success" if not errors else "partial_success",
    }


def get_collector(name: str) -> Callable:
    """Get a specific collector by name."""
    return _COLLECTORS.get(name)


def list_collectors() -> List[str]:
    """Get list of all registered collectors."""
    return list(_COLLECTORS.keys())


__all__ = [
    "run_all_collectors",
    "get_collector",
    "list_collectors",
    "register_collector",
]
