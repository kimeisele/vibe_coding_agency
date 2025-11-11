"""
Report Generator - Converts AnalysisResult findings into structured reports.

Supports:
- JSON output (structured, machine-readable)
- Terminal output (rich formatted table)
- YAML output (planned for Sprint 3)
- CSV output (planned for Sprint 3)
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory

logger = logging.getLogger(__name__)


class Report:
    """Aggregated analysis report with summary statistics."""

    def __init__(
        self,
        findings: List[AnalysisResult],
        execution_time: float = 0.0,
        timestamp: Optional[str] = None,
    ):
        """
        Initialize report with findings.

        Args:
            findings: List of AnalysisResult objects
            execution_time: Total execution time in seconds
            timestamp: ISO format timestamp (auto-generated if not provided)
        """
        self.findings = findings
        self.execution_time = execution_time
        self.timestamp = timestamp or datetime.now().isoformat()
        self._summary = self._calculate_summary()

    def _calculate_summary(self) -> Dict[str, int]:
        """Calculate summary statistics by severity."""
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "TOTAL": len(self.findings),
        }

        for finding in self.findings:
            # Handle both string and enum severity
            severity_str = (
                finding.severity.value
                if isinstance(finding.severity, Severity)
                else str(finding.severity)
            )
            if severity_str in summary:
                summary[severity_str] += 1

        return summary

    @property
    def summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        return self._summary

    def to_json(self) -> str:
        """
        Export report as JSON string.

        Returns:
            JSON string with findings and metadata
        """
        data = {
            "summary": self.summary,
            "findings": [
                {
                    "analyzer": finding.analyzer_name,
                    "file": str(finding.file_path),
                    "line": finding.line_start,
                    "severity": (
                        finding.severity.value
                        if isinstance(finding.severity, Severity)
                        else str(finding.severity)
                    ),
                    "category": (
                        finding.category.value
                        if isinstance(finding.category, AnalysisCategory)
                        else str(finding.category)
                    ),
                    "confidence": finding.confidence,
                    "pattern_type": finding.pattern_type,
                    "message": finding.message,
                    "evidence": finding.evidence,
                    "remediation": finding.remediation,
                }
                for finding in self.findings
            ],
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
        }
        return json.dumps(data, indent=2)

    def to_terminal(self) -> str:
        """
        Export report as Rich-formatted terminal output.

        Returns:
            Formatted string with table and summary
        """
        try:
            from rich.console import Console
            from rich.table import Table

            # Create summary lines
            summary_lines = [
                "Meta-Audit Report",
                "=" * 80,
                f"Critical: {self.summary.get('CRITICAL', 0):3d} | "
                f"High: {self.summary.get('HIGH', 0):3d} | "
                f"Medium: {self.summary.get('MEDIUM', 0):3d} | "
                f"Low: {self.summary.get('LOW', 0):3d} | "
                f"Total: {self.summary.get('TOTAL', 0):3d}",
                f"Execution time: {self.execution_time:.2f}s",
                f"Timestamp: {self.timestamp}",
                "",
            ]

            if not self.findings:
                summary_lines.append("No findings detected! ✓")
                return "\n".join(summary_lines)

            # Create table
            table = Table(title="Findings")
            table.add_column("Severity", style="cyan", width=12)
            table.add_column("Category", style="magenta", width=20)
            table.add_column("Analyzer", style="blue", width=18)
            table.add_column("File", style="green", width=30)
            table.add_column("Line", style="yellow", width=6)
            table.add_column("Message", style="white", width=40)

            # Add rows
            for finding in self.findings:
                # Determine severity styling
                severity_str = (
                    finding.severity.value
                    if isinstance(finding.severity, Severity)
                    else str(finding.severity)
                )
                category_str = (
                    finding.category.value
                    if isinstance(finding.category, AnalysisCategory)
                    else str(finding.category)
                )

                severity_style = {
                    "CRITICAL": "bold red",
                    "HIGH": "red",
                    "MEDIUM": "yellow",
                    "LOW": "blue",
                }.get(severity_str, "white")

                # Truncate message if too long
                message = finding.message
                if len(message) > 40:
                    message = message[:37] + "..."

                table.add_row(
                    f"[{severity_style}]{severity_str}[/{severity_style}]",
                    category_str,
                    finding.analyzer_name,
                    str(finding.file_path),
                    str(finding.line_start or "N/A"),
                    message,
                )

            # Render table to string buffer
            string_io = io.StringIO()
            console = Console(file=string_io, width=200)
            console.print(table)
            table_output = string_io.getvalue()

            return "\n".join(summary_lines) + "\n" + table_output

        except ImportError:
            # Fallback if rich is not available
            logger.warning("Rich library not available, using plain text output")
            return self._to_plain_text()

    def _to_plain_text(self) -> str:
        """
        Fallback plain text output when Rich is not available.

        Returns:
            Plain text formatted report
        """
        lines = [
            "Meta-Audit Report",
            "=" * 80,
            f"Critical: {self.summary.get('CRITICAL', 0)} | "
            f"High: {self.summary.get('HIGH', 0)} | "
            f"Medium: {self.summary.get('MEDIUM', 0)} | "
            f"Low: {self.summary.get('LOW', 0)} | "
            f"Total: {self.summary.get('TOTAL', 0)}",
            f"Execution time: {self.execution_time:.2f}s",
            f"Timestamp: {self.timestamp}",
            "",
        ]

        if not self.findings:
            lines.append("No findings detected!")
            return "\n".join(lines)

        # Simple text table
        lines.append(
            f"{'Severity':<12} {'Category':<20} {'Analyzer':<18} "
            f"{'File':<30} {'Line':<6} {'Message':<40}"
        )
        lines.append("-" * 126)

        for finding in self.findings:
            severity_str = (
                finding.severity.value
                if isinstance(finding.severity, Severity)
                else str(finding.severity)
            )
            category_str = (
                finding.category.value
                if isinstance(finding.category, AnalysisCategory)
                else str(finding.category)
            )

            message = finding.message
            if len(message) > 40:
                message = message[:37] + "..."

            lines.append(
                f"{severity_str:<12} {category_str:<20} {finding.analyzer_name:<18} "
                f"{str(finding.file_path):<30} {str(finding.line_start or 'N/A'):<6} {message:<40}"
            )

        return "\n".join(lines)


def generate_report(
    findings: List[AnalysisResult], execution_time: float = 0.0
) -> Report:
    """
    Generate a report from a list of AnalysisResult findings.

    Args:
        findings: List of AnalysisResult objects from collectors
        execution_time: Total execution time in seconds

    Returns:
        Report instance with summary and export methods
    """
    return Report(findings, execution_time)
