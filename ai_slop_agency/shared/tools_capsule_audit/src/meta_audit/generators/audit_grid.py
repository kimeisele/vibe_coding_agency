"""
Audit Grid Generator - Transform findings into structured quality metrics.

Based on Vibe Coding OS Wiki: docs/vibe-coding-os/10-templates/audit-grid.md

Generates CSV/Markdown tables with:
- SRP Violation (YES/NO)
- God Object Indicator (CRITICAL/HIGH/MED/LOW)
- AI Slop Indicator (YES/NO)
- Cognitive Load (1-7)
- Readability (1-5)
- Testability (1-5)
- Qualitative Codes/Themes
- Priority (CRITICAL/HIGH/MED/LOW)
"""

import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional

from meta_audit.core.models import AnalysisResult, Severity

logger = logging.getLogger(__name__)


class FileMetrics:
    """Aggregated metrics for a single file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.findings: List[AnalysisResult] = []
        self.god_object_severity: Optional[Severity] = None
        self.has_ai_slop = False
        self.complexity_scores: List[int] = []
        self.security_issues = 0
        self.themes: set = set()

    def add_finding(self, finding: AnalysisResult):
        """Add a finding and update metrics."""
        self.findings.append(finding)

        # Track God Object
        if finding.analyzer_name == "god_object_detector":
            self.god_object_severity = finding.severity

        # Track AI Slop
        if finding.analyzer_name == "ai_slop_analyzer":
            self.has_ai_slop = True

        # Track complexity
        if finding.analyzer_name == "complexity":
            complexity = finding.evidence.get("complexity", 0)
            if isinstance(complexity, (int, float)):
                self.complexity_scores.append(int(complexity))

        # Track security
        if finding.analyzer_name == "security":
            self.security_issues += 1

        # Collect themes
        if finding.pattern_type:
            self.themes.add(finding.pattern_type)

    @property
    def srp_violation(self) -> str:
        """Determine if file violates Single Responsibility Principle."""
        # Check God Object detector evidence
        for finding in self.findings:
            if finding.analyzer_name == "god_object_detector":
                srp = finding.evidence.get("srp_violation", False)
                return "YES" if srp else "NO"
        return "NO"

    @property
    def god_object_indicator(self) -> str:
        """God Object severity level."""
        if self.god_object_severity == Severity.CRITICAL:
            return "CRITICAL"
        elif self.god_object_severity == Severity.HIGH:
            return "HIGH"
        elif self.god_object_severity == Severity.MEDIUM:
            return "MED"
        return "LOW"

    @property
    def ai_slop_indicator(self) -> str:
        """AI Slop presence."""
        return "YES" if self.has_ai_slop else "NO"

    @property
    def cognitive_load(self) -> int:
        """
        Cognitive Load score (1-7) based on Miller's Law.

        Factors:
        - Complexity
        - God Object size
        - Number of distinct issues
        """
        score = 1

        # Complexity contribution (max +3)
        if self.complexity_scores:
            avg_complexity = sum(self.complexity_scores) / len(self.complexity_scores)
            if avg_complexity > 20:
                score += 3
            elif avg_complexity > 10:
                score += 2
            elif avg_complexity > 5:
                score += 1

        # God Object contribution (max +2)
        if self.god_object_severity == Severity.CRITICAL:
            score += 2
        elif self.god_object_severity == Severity.HIGH:
            score += 1

        # Issue diversity contribution (max +2)
        issue_count = len(self.findings)
        if issue_count > 50:
            score += 2
        elif issue_count > 20:
            score += 1

        return min(score, 7)  # Cap at 7

    @property
    def readability(self) -> int:
        """
        Readability score (1-5).

        Based on:
        - AI Slop presence
        - Complexity
        - Security issues
        """
        score = 5  # Start optimistic

        # AI Slop penalty
        if self.has_ai_slop:
            score -= 1

        # Complexity penalty
        if self.complexity_scores:
            avg_complexity = sum(self.complexity_scores) / len(self.complexity_scores)
            if avg_complexity > 15:
                score -= 2
            elif avg_complexity > 10:
                score -= 1

        # God Object penalty
        if self.god_object_severity in [Severity.CRITICAL, Severity.HIGH]:
            score -= 1

        return max(score, 1)  # Min 1

    @property
    def testability(self) -> int:
        """
        Testability score (1-5).

        God Objects are hard to test.
        High coupling reduces testability.
        """
        score = 5  # Start optimistic

        # God Object penalty (major)
        if self.god_object_severity == Severity.CRITICAL:
            score -= 3
        elif self.god_object_severity == Severity.HIGH:
            score -= 2
        elif self.god_object_severity == Severity.MEDIUM:
            score -= 1

        # Complexity penalty
        if self.complexity_scores:
            avg_complexity = sum(self.complexity_scores) / len(self.complexity_scores)
            if avg_complexity > 15:
                score -= 1

        return max(score, 1)  # Min 1

    @property
    def qualitative_codes(self) -> str:
        """Comma-separated list of themes/patterns."""
        return ", ".join(sorted(self.themes)) if self.themes else "Clean"

    @property
    def priority(self) -> str:
        """
        Priority level based on severity and business impact.

        From prioritization matrix:
        - Business Criticality
        - Change Frequency
        - Risk and Inefficiency
        """
        # Critical if God Object or multiple HIGH issues
        if self.god_object_severity == Severity.CRITICAL:
            return "CRITICAL"

        high_count = sum(1 for f in self.findings if f.severity == Severity.HIGH)
        if high_count >= 3:
            return "CRITICAL"

        # High if God Object HIGH or security issues
        if self.god_object_severity == Severity.HIGH or self.security_issues > 0:
            return "HIGH"

        # Medium if God Object MED or many issues
        if self.god_object_severity == Severity.MEDIUM or len(self.findings) > 20:
            return "MED"

        return "LOW"


def generate_audit_grid(findings: List[AnalysisResult], output_path: Optional[Path] = None) -> str:
    """
    Generate Audit Grid from analysis findings.

    Args:
        findings: List of AnalysisResult objects
        output_path: Optional path to save CSV

    Returns:
        Markdown table representation
    """
    # Group findings by file
    files_dict: Dict[Path, FileMetrics] = defaultdict(lambda: None)

    for finding in findings:
        if finding.file_path:
            if files_dict[finding.file_path] is None:
                files_dict[finding.file_path] = FileMetrics(finding.file_path)
            files_dict[finding.file_path].add_finding(finding)

    if not files_dict:
        return "No files to analyze."

    # Build table rows
    rows = []
    for file_path, metrics in sorted(files_dict.items(), key=lambda x: x[1].priority, reverse=True):
        row = {
            "Module/File": str(file_path),
            "SRP Violation": metrics.srp_violation,
            "God Object": metrics.god_object_indicator,
            "AI Slop": metrics.ai_slop_indicator,
            "Cognitive Load": f"{metrics.cognitive_load}/7",
            "Readability": f"{metrics.readability}/5",
            "Testability": f"{metrics.testability}/5",
            "Themes/Codes": metrics.qualitative_codes,
            "Priority": metrics.priority,
        }
        rows.append(row)

    # Save CSV if requested
    if output_path:
        _save_csv(rows, output_path)

    # Generate markdown
    return _generate_markdown(rows)


def _save_csv(rows: List[Dict[str, Any]], output_path: Path):
    """Save audit grid as CSV."""
    if not rows:
        return

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Audit Grid saved to {output_path}")


def _generate_markdown(rows: List[Dict[str, Any]]) -> str:
    """Generate markdown table."""
    if not rows:
        return "No data."

    lines = ["# Audit Grid", ""]

    # Summary stats
    critical_count = sum(1 for r in rows if r["Priority"] == "CRITICAL")
    high_count = sum(1 for r in rows if r["Priority"] == "HIGH")
    god_objects = sum(1 for r in rows if r["God Object"] in ["CRITICAL", "HIGH"])
    ai_slop_files = sum(1 for r in rows if r["AI Slop"] == "YES")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Files:** {len(rows)}")
    lines.append(f"- **Critical Issues:** {critical_count}")
    lines.append(f"- **High Priority:** {high_count}")
    lines.append(f"- **God Objects:** {god_objects}")
    lines.append(f"- **AI Slop Detected:** {ai_slop_files} files")
    lines.append("")

    # Table header
    headers = list(rows[0].keys())
    lines.append("## Detailed Grid")
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Table rows (top 20 by priority)
    for row in rows[:20]:
        values = [str(row[h]) for h in headers]
        lines.append("| " + " | ".join(values) + " |")

    if len(rows) > 20:
        lines.append("")
        lines.append(f"*({len(rows) - 20} more files omitted)*")

    return "\n".join(lines)


__all__ = ["generate_audit_grid", "FileMetrics"]
