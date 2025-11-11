"""
God Object Detector - Identifies SRP violations and God Object anti-patterns.

Based on Vibe Coding OS Wiki: docs/vibe-coding-os/03-audit/god-object-pattern.md

Detection Heuristics:
- High method count (>20 public, >50 total)
- High line count (>500 lines, >1000 critical)
- Vague class names (Manager, Handler, Processor, Utility)
- Multiple responsibilities

Returns List[AnalysisResult] with strict Pydantic validation.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory

logger = logging.getLogger(__name__)


class GodObjectHeuristics:
    """Detection criteria from Vibe Coding OS Wiki."""

    # Line count thresholds
    LINES_WARNING = 200
    LINES_HIGH = 500
    LINES_CRITICAL = 1000

    # Method count thresholds
    METHODS_WARNING = 10
    METHODS_HIGH = 20
    METHODS_CRITICAL = 50

    # Vague class name indicators (typical of God Objects)
    VAGUE_NAMES = {
        "manager",
        "handler",
        "processor",
        "utility",
        "helper",
        "utils",
        "controller",
        "service",  # Sometimes okay, but often a smell
        "facade",
        "coordinator",
        "orchestrator",
    }


class ClassMetrics:
    """Metrics for a single class."""

    def __init__(self, name: str, lineno: int):
        self.name = name
        self.lineno = lineno
        self.line_end = lineno
        self.methods: List[str] = []
        self.public_methods: List[str] = []
        self.responsibilities: Set[str] = set()

    @property
    def line_count(self) -> int:
        return self.line_end - self.lineno + 1

    @property
    def method_count(self) -> int:
        return len(self.methods)

    @property
    def public_method_count(self) -> int:
        return len(self.public_methods)

    def has_vague_name(self) -> bool:
        """Check if class name matches God Object patterns."""
        name_lower = self.name.lower()
        return any(vague in name_lower for vague in GodObjectHeuristics.VAGUE_NAMES)

    def detect_responsibilities(self) -> Set[str]:
        """Infer responsibilities from method name prefixes."""
        responsibilities = set()
        for method in self.public_methods:
            # Extract verb/noun patterns: create_user, send_email, etc.
            if "_" in method:
                parts = method.split("_")
                if len(parts) >= 2:
                    # Take the second part as the domain (user, order, email, etc.)
                    domain = parts[1] if not parts[0].startswith("_") else parts[0]
                    responsibilities.add(domain.lower())
        return responsibilities

    def calculate_severity(self) -> Severity:
        """Calculate severity based on multiple heuristics."""
        lines = self.line_count
        methods = self.method_count
        public_methods = self.public_method_count

        # Critical: >1000 lines OR >50 methods
        if lines > GodObjectHeuristics.LINES_CRITICAL or methods > GodObjectHeuristics.METHODS_CRITICAL:
            return Severity.CRITICAL

        # High: >500 lines OR >20 methods OR multiple responsibilities
        if lines > GodObjectHeuristics.LINES_HIGH or public_methods > GodObjectHeuristics.METHODS_HIGH:
            return Severity.HIGH

        # Medium: >200 lines OR >10 methods OR vague name
        if lines > GodObjectHeuristics.LINES_WARNING or methods > GodObjectHeuristics.METHODS_WARNING:
            return Severity.MEDIUM

        return Severity.LOW


def get_god_object_findings(path: str) -> List[AnalysisResult]:
    """
    Detect God Object anti-patterns in Python code.

    Based on heuristics from Vibe Coding OS Wiki:
    - Line count
    - Method count
    - Vague naming
    - Multiple responsibilities

    Args:
        path: Root path to analyze

    Returns:
        List[AnalysisResult] - Each result represents a God Object finding.
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

                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()

                rel_path = py_file.relative_to(project_path)

                # Parse AST
                try:
                    tree = ast.parse(code_content)
                except SyntaxError:
                    logger.debug(f"Could not parse {py_file}")
                    continue

                # Analyze each class
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        metrics = _analyze_class(node)

                        # Calculate severity
                        severity = metrics.calculate_severity()

                        # Only report if at least MEDIUM severity
                        if severity == Severity.LOW:
                            continue

                        # Detect responsibilities
                        responsibilities = metrics.detect_responsibilities()
                        srp_violation = len(responsibilities) > 3  # More than 3 domains = SRP violation

                        # Build evidence
                        evidence = {
                            "class_name": metrics.name,
                            "line_count": metrics.line_count,
                            "method_count": metrics.method_count,
                            "public_method_count": metrics.public_method_count,
                            "has_vague_name": metrics.has_vague_name(),
                            "srp_violation": srp_violation,
                            "detected_responsibilities": sorted(list(responsibilities)),
                        }

                        # Generate message
                        message = _generate_message(metrics, srp_violation, responsibilities)

                        # Generate remediation
                        remediation = _generate_remediation(metrics, srp_violation, responsibilities)

                        result = AnalysisResult(
                            analyzer_name="god_object_detector",
                            file_path=rel_path,
                            line_start=metrics.lineno,
                            line_end=metrics.line_end,
                            pattern_type="god_object" if severity == Severity.CRITICAL else "large_class",
                            severity=severity,
                            category=AnalysisCategory.MAINTAINABILITY,
                            confidence=0.85 if srp_violation else 0.75,
                            message=message,
                            evidence=evidence,
                            remediation=remediation,
                            project_name=None,
                        )
                        results.append(result)

            except (OSError, IOError) as e:
                logger.warning(f"Could not read file {py_file}: {e}")
                continue

        return results

    except Exception as e:
        logger.error(f"God Object detection failed: {e}")
        return []


def _analyze_class(class_node: ast.ClassDef) -> ClassMetrics:
    """Extract metrics from a class AST node."""
    metrics = ClassMetrics(class_node.name, class_node.lineno)

    # Find the last line of the class
    if class_node.body:
        last_node = class_node.body[-1]
        metrics.line_end = getattr(last_node, "end_lineno", last_node.lineno)

    # Count methods
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            metrics.methods.append(item.name)
            # Public methods don't start with underscore
            if not item.name.startswith("_"):
                metrics.public_methods.append(item.name)

    return metrics


def _generate_message(metrics: ClassMetrics, srp_violation: bool, responsibilities: Set[str]) -> str:
    """Generate a human-readable message."""
    parts = [f"Class '{metrics.name}' shows God Object indicators:"]

    if metrics.line_count > GodObjectHeuristics.LINES_CRITICAL:
        parts.append(f"{metrics.line_count} lines (CRITICAL threshold)")
    elif metrics.line_count > GodObjectHeuristics.LINES_HIGH:
        parts.append(f"{metrics.line_count} lines (HIGH threshold)")
    else:
        parts.append(f"{metrics.line_count} lines")

    parts.append(f"{metrics.public_method_count} public methods")

    if srp_violation and responsibilities:
        parts.append(f"Multiple responsibilities: {', '.join(sorted(responsibilities))}")

    if metrics.has_vague_name():
        parts.append(f"Vague class name ('{metrics.name}')")

    return " | ".join(parts)


def _generate_remediation(
    metrics: ClassMetrics, srp_violation: bool, responsibilities: Set[str]
) -> List[str]:
    """Generate actionable remediation steps."""
    steps = []

    if srp_violation and responsibilities:
        steps.append(f"Apply Extract Class refactoring - detected domains: {', '.join(sorted(responsibilities))}")
        for resp in sorted(responsibilities):
            steps.append(f"  → Extract '{resp.capitalize()}Service' or '{resp.capitalize()}Manager'")

    if metrics.method_count > 30:
        steps.append("Break down into smaller, focused classes (Single Responsibility Principle)")

    if metrics.has_vague_name():
        steps.append(f"Rename class to reflect specific responsibility (avoid vague names like '{metrics.name}')")

    steps.append("Run thematic analysis to identify cohesive method groups")
    steps.append("See: docs/vibe-coding-os/03-audit/god-object-pattern.md")

    return steps


# Register collector
__all__ = ["get_god_object_findings"]
