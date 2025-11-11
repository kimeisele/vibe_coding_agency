"""
Complexity Analyzer - Uses Radon to analyze code complexity metrics.

Analyzes:
- Cyclomatic Complexity (CC) - how complex a function is
- Maintainability Index (MI) - how maintainable the code is
- Lines of Code (LOC)
- Function-level metrics

Returns List[AnalysisResult] with strict Pydantic validation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from radon.complexity import cc_visit
from radon.metrics import mi_visit

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory

logger = logging.getLogger(__name__)


def get_complexity_metrics(path: str, threshold_cc: int = 10) -> List[AnalysisResult]:
    """
    Analyze complexity metrics for a project using Radon.

    Returns AnalysisResult objects for functions exceeding CC threshold.

    Args:
        path: Root path to analyze
        threshold_cc: Cyclomatic complexity threshold to flag as HIGH (default: 10)

    Returns:
        List[AnalysisResult] - Each result represents a high-complexity finding.
    """
    results: List[AnalysisResult] = []

    try:
        project_path = Path(path)
        python_files = list(project_path.rglob("*.py"))

        if not python_files:
            logger.warning(f"No Python files found in {path}")
            return results

        for py_file in python_files:
            try:
                # Skip common non-source directories
                if any(
                    part in py_file.parts
                    for part in [".venv", "venv", ".git", "__pycache__", "node_modules"]
                ):
                    continue

                with open(
                    py_file, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    code_content = f.read()

                rel_file_path = py_file.relative_to(project_path)

                # Get cyclomatic complexity
                try:
                    cc_results = cc_visit(code_content)
                    for block in cc_results:
                        # Only report functions/methods with high CC
                        if block.complexity >= threshold_cc:
                            # Determine severity based on CC level
                            if block.complexity >= 15:
                                severity = Severity.HIGH
                            else:
                                severity = Severity.MEDIUM

                            # Calculate line range
                            loc = (
                                block.end_lineno - block.lineno + 1
                                if block.end_lineno
                                else 0
                            )

                            # Create AnalysisResult with strict validation
                            result = AnalysisResult(
                                analyzer_name="complexity_analyzer",
                                file_path=rel_file_path,
                                line_start=block.lineno,
                                line_end=block.end_lineno,
                                pattern_type="high_cyclomatic_complexity",
                                severity=severity,
                                category=AnalysisCategory.CODE_STRUCTURE,
                                confidence=0.95,
                                message=f"Function/Method '{block.name}' has cyclomatic complexity of {block.complexity} (threshold: {threshold_cc})",
                                evidence={
                                    "cc": block.complexity,
                                    "loc": loc,
                                    "function_name": block.name,
                                    "block_type": block.__class__.__name__,
                                },
                                remediation=[
                                    "Break function into smaller, single-purpose functions",
                                    "Extract complex conditional logic into helper functions",
                                    "Consider using design patterns to reduce branching",
                                    "Use loops or list comprehensions instead of nested conditionals",
                                ],
                                project_name=None,
                            )
                            results.append(result)

                except Exception as e:
                    logger.debug(f"Radon CC analysis failed for {py_file}: {e}")

            except (OSError, IOError) as e:
                logger.warning(f"Could not read file {py_file}: {e}")
                continue

        return results

    except Exception as e:
        logger.error(f"Complexity analysis failed: {e}")
        # Return empty list on error (graceful degradation)
        return []
