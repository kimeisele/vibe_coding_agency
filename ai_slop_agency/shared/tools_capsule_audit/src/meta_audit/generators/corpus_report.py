"""
Corpus Analysis Report - Aggregates findings from multiple ProjectCapsule analyses.

Provides summary statistics, per-project metrics, and cross-project pattern framework.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory
from meta_audit.generators.report import Report
from meta_audit.analyzers.cross_project_analyzer import CrossProjectAnalyzer

logger = logging.getLogger(__name__)


class CorpusAnalysisReport:
    """Aggregated report for multiple ProjectCapsule analyses."""

    def __init__(
        self,
        project_reports: Dict[str, Report],
        all_findings: List[AnalysisResult],
        execution_time: float = 0.0,
    ):
        """
        Initialize corpus report.

        Args:
            project_reports: Dict mapping project_name → Report object
            all_findings: Flattened list of all AnalysisResult from all projects
            execution_time: Total execution time in seconds
        """
        self.project_reports = project_reports
        self.all_findings = all_findings
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()
        self._summary = self._calculate_summary()

        # Run cross-project analysis framework (Phase 3 MVP)
        findings_by_project = self._organize_findings_by_project()
        analyzer = CrossProjectAnalyzer()
        self.cross_project_patterns = analyzer.analyze(findings_by_project)

    def _organize_findings_by_project(self) -> Dict[str, List[AnalysisResult]]:
        """
        Organize findings by project for cross-project analysis.

        Returns:
            Dict mapping project_name → List[AnalysisResult]
        """
        findings_by_project: Dict[str, List[AnalysisResult]] = {}
        for finding in self.all_findings:
            project_name = finding.project_name or "unknown"
            if project_name not in findings_by_project:
                findings_by_project[project_name] = []
            findings_by_project[project_name].append(finding)
        return findings_by_project

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate aggregated summary statistics."""
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "TOTAL": len(self.all_findings),
            "projects_analyzed": len(self.project_reports),
            "project_summaries": {},
        }

        # Count severities across all findings
        for finding in self.all_findings:
            severity_str = (
                finding.severity.value
                if isinstance(finding.severity, Severity)
                else str(finding.severity)
            )
            if severity_str in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                summary[severity_str] += 1

        # Add per-project summaries
        for project_name, report in self.project_reports.items():
            summary["project_summaries"][project_name] = report.summary

        return summary

    @property
    def summary(self) -> Dict[str, Any]:
        """Get aggregated summary."""
        return self._summary

    def to_json(self) -> str:
        """
        Export corpus report as JSON.

        Returns:
            JSON string with corpus summary, per-project metrics, findings, and patterns
        """
        data = {
            "summary": {
                "CRITICAL": self.summary.get("CRITICAL", 0),
                "HIGH": self.summary.get("HIGH", 0),
                "MEDIUM": self.summary.get("MEDIUM", 0),
                "LOW": self.summary.get("LOW", 0),
                "TOTAL": self.summary.get("TOTAL", 0),
                "projects_analyzed": self.summary.get("projects_analyzed", 0),
            },
            "project_summaries": self.summary.get("project_summaries", {}),
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
                for finding in self.all_findings
            ],
            "cross_project_patterns": [
                p.model_dump(mode="json") for p in self.cross_project_patterns
            ],
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
        }

        return json.dumps(data, indent=2)

    def to_terminal(self) -> str:
        """
        Export corpus report as formatted terminal output.

        Returns:
            Formatted string with corpus summary and per-project breakdown
        """
        lines = [
            "Meta-Audit Corpus Report",
            "=" * 80,
            f"Projects Analyzed: {self.summary.get('projects_analyzed', 0)}",
            f"Total Findings: {self.summary.get('TOTAL', 0)}",
            "",
            "Severity Breakdown (Across All Projects):",
            f"  Critical: {self.summary.get('CRITICAL', 0):3d} | "
            f"High: {self.summary.get('HIGH', 0):3d} | "
            f"Medium: {self.summary.get('MEDIUM', 0):3d} | "
            f"Low: {self.summary.get('LOW', 0):3d}",
            f"Execution Time: {self.execution_time:.2f}s",
            f"Generated: {self.timestamp}",
            "",
        ]

        # Per-project breakdown
        if self.project_reports:
            lines.append("Per-Project Breakdown:")
            lines.append("-" * 80)

            for project_name, report in self.project_reports.items():
                lines.append(f"\n📦 {project_name}")
                summary = report.summary
                lines.append(
                    f"   Findings: {summary.get('TOTAL', 0)} | "
                    f"Critical: {summary.get('CRITICAL', 0)}, "
                    f"High: {summary.get('HIGH', 0)}, "
                    f"Medium: {summary.get('MEDIUM', 0)}, "
                    f"Low: {summary.get('LOW', 0)}"
                )

            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


def generate_corpus_report(
    project_reports: Dict[str, Report],
    all_findings: List[AnalysisResult],
    execution_time: float = 0.0,
) -> CorpusAnalysisReport:
    """
    Generate a corpus report from multiple project reports.

    Args:
        project_reports: Dict mapping project_name → Report
        all_findings: Flattened list of all findings
        execution_time: Total execution time

    Returns:
        CorpusAnalysisReport instance
    """
    return CorpusAnalysisReport(project_reports, all_findings, execution_time)
