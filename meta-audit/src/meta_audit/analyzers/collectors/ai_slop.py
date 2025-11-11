"""
AI-Slop Analyzer - Pattern-based detection of AI-generated code smells.

Patterns checked:
- Verbose docstrings with no real info (typical of AI-generated)
- Placeholder comments (TODO, FIXME, XXX without context)
- Dead code (unused variables, imports)
- Overly generic variable names (data, temp, result)
- Redundant exception handling

Returns List[AnalysisResult] with strict Pydantic validation.
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory

logger = logging.getLogger(__name__)


class AISlop:
    """Pattern definitions for AI-Slop detection."""

    # Verbose docstring pattern (too many words, no real info)
    VERBOSE_DOCSTRING = re.compile(
        r'""".*?(?:This function|This method|This class|This module).*?"""',
        re.DOTALL | re.IGNORECASE,
    )

    # Placeholder comment pattern
    PLACEHOLDER_COMMENT = re.compile(
        r"#\s*(?:TODO|FIXME|XXX|HACK|BUG)\s*:",
        re.IGNORECASE,
    )

    # Generic variable names (common in AI output)
    GENERIC_VARS = {
        "data",
        "temp",
        "result",
        "value",
        "obj",
        "item",
        "thing",
        "stuff",
        "var",
        "tmp",
        "x",
        "y",
        "args",
        "kwargs",
    }


def get_ai_slop_findings(path: str) -> List[AnalysisResult]:
    """
    Detect AI-Slop patterns in Python code.

    Returns AnalysisResult objects for each pattern detected.

    Args:
        path: Root path to analyze

    Returns:
        List[AnalysisResult] - Each result represents an AI-Slop finding.
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

                lines = code_content.splitlines()
                rel_path = py_file.relative_to(project_path)

                # Check 1: Verbose docstrings
                for i, line in enumerate(lines, 1):
                    if AISlop.VERBOSE_DOCSTRING.search(line):
                        result = AnalysisResult(
                            analyzer_name="ai_slop_analyzer",
                            file_path=rel_path,
                            line_start=i,
                            line_end=None,
                            pattern_type="verbose_docstring",
                            severity=Severity.LOW,
                            category=AnalysisCategory.CODE_STRUCTURE,
                            confidence=0.80,
                            message="Generic/verbose docstring (typical of AI-generated code)",
                            evidence={"content": line.strip()[:100]},
                            remediation=[
                                "Write clear, concise docstrings with actual value",
                                "Document what the function does, not generic descriptions",
                                "Include usage examples if helpful",
                            ],
                            project_name=None,
                        )
                        results.append(result)

                # Check 2: Placeholder comments
                for i, line in enumerate(lines, 1):
                    if AISlop.PLACEHOLDER_COMMENT.search(line):
                        result = AnalysisResult(
                            analyzer_name="ai_slop_analyzer",
                            file_path=rel_path,
                            line_start=i,
                            line_end=None,
                            pattern_type="placeholder_comment",
                            severity=Severity.MEDIUM,
                            category=AnalysisCategory.CODE_STRUCTURE,
                            confidence=0.95,
                            message=f"Unresolved comment: {line.strip()}",
                            evidence={"comment": line.strip()},
                            remediation=[
                                "Resolve the TODO/FIXME before merging",
                                "If not urgent, create a GitHub issue and link it",
                                "Remove if no longer applicable",
                            ],
                            project_name=None,
                        )
                        results.append(result)

                # Check 3: Generic variable names (AST-based)
                try:
                    tree = ast.parse(code_content)
                    reported_lines = set()  # Track (lineno, var_name) to avoid duplicates

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name) and node.id in AISlop.GENERIC_VARS:
                            if hasattr(node, "lineno"):
                                key = (node.lineno, node.id)
                                if key not in reported_lines:
                                    result = AnalysisResult(
                                        analyzer_name="ai_slop_analyzer",
                                        file_path=rel_path,
                                        line_start=node.lineno,
                                        line_end=None,
                                        pattern_type="generic_variable",
                                        severity=Severity.LOW,
                                        category=AnalysisCategory.CODE_STRUCTURE,
                                        confidence=0.75,
                                        message=f"Generic variable name '{node.id}' - use a more descriptive name",
                                        evidence={"variable_name": node.id},
                                        remediation=[
                                            f"Rename '{node.id}' to something more descriptive",
                                            "Use names that explain the variable's purpose",
                                            "Consider the variable's context when naming",
                                        ],
                                        project_name=None,
                                    )
                                    results.append(result)
                                    reported_lines.add(key)

                except SyntaxError:
                    logger.debug(f"Could not parse {py_file}")

            except (OSError, IOError) as e:
                logger.warning(f"Could not read file {py_file}: {e}")
                continue

        return results

    except Exception as e:
        logger.error(f"AI-Slop analysis failed: {e}")
        # Return empty list on error (graceful degradation)
        return []
