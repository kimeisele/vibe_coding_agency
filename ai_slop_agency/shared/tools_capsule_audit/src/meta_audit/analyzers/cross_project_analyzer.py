"""
Cross-Project Pattern Analysis Framework

Prepares data structures and detection framework for Phase 4/5 implementation.
Phase 3 (MVP) provides framework structure; actual pattern detection logic
will be implemented in Phase 4/5.
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict

from meta_audit.core.models import (
    AnalysisResult,
    CrossProjectPattern,
    Severity,
    AnalysisCategory,
)

logger = logging.getLogger(__name__)


class CrossProjectAnalyzer:
    """
    Framework for detecting cross-project patterns.

    Current status: Phase 3 (MVP) - structure only.
    Implementation: Phase 4/5

    Methods return empty lists until Phase 4/5 pattern detection logic is implemented.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self.patterns: List[CrossProjectPattern] = []

    def detect_duplicate_issues(
        self, findings_by_project: Dict[str, List[AnalysisResult]]
    ) -> List[CrossProjectPattern]:
        """
        Detect duplicate or very similar issues across projects.

        Identifies issues that appear in multiple projects with high similarity,
        indicating systemic problems or shared dependency vulnerabilities.

        Args:
            findings_by_project: Dict mapping project_name → List[AnalysisResult]

        Returns:
            List of CrossProjectPattern objects for duplicate issues.
        """
        patterns: List[CrossProjectPattern] = []

        if not findings_by_project or len(findings_by_project) < 2:
            return patterns

        # Group by pattern_type to find duplicates efficiently
        pattern_groups: Dict[str, List[tuple]] = defaultdict(list)

        for project_name, findings in findings_by_project.items():
            for finding in findings:
                key = finding.pattern_type
                pattern_groups[key].append((project_name, finding))

        # Find patterns appearing in multiple projects
        for pattern_type, occurrences in pattern_groups.items():
            projects_with_pattern = set(proj for proj, _ in occurrences)

            # Only report if appears in 2+ projects
            if len(projects_with_pattern) >= 2:
                findings_list = [finding for _, finding in occurrences]

                # Calculate average severity/confidence
                avg_confidence = sum(f.confidence for f in findings_list) / len(
                    findings_list
                )
                severity = findings_list[0].severity  # Use first finding's severity
                category = findings_list[0].category

                pattern = CrossProjectPattern(
                    pattern_type=pattern_type,
                    severity=severity,
                    category=category,
                    projects_count=len(projects_with_pattern),
                    projects=sorted(list(projects_with_pattern)),
                    message=f"Pattern '{pattern_type}' found in {len(projects_with_pattern)} projects",
                    projects_confidence=avg_confidence,
                    evidence={
                        "occurrence_count": len(findings_list),
                        "projects_affected": list(projects_with_pattern),
                        "example_messages": [f.message for f in findings_list[:3]],
                    },
                )
                patterns.append(pattern)

        logger.info(f"Detected {len(patterns)} duplicate issues across projects")
        return patterns

    def detect_vulnerability_patterns(
        self, findings_by_project: Dict[str, List[AnalysisResult]]
    ) -> List[CrossProjectPattern]:
        """
        Detect security vulnerabilities that appear in multiple projects.

        Identifies common security patterns, shared dependency vulnerabilities,
        or architectural security issues affecting multiple projects.

        Args:
            findings_by_project: Dict mapping project_name → List[AnalysisResult]

        Returns:
            List of CrossProjectPattern objects for vulnerability patterns.
        """
        patterns: List[CrossProjectPattern] = []

        if not findings_by_project or len(findings_by_project) < 2:
            return patterns

        # Filter for SECURITY category findings only
        security_by_project = {}
        for project_name, findings in findings_by_project.items():
            security_findings = [
                f for f in findings if f.category == AnalysisCategory.SECURITY
            ]
            if security_findings:
                security_by_project[project_name] = security_findings

        if len(security_by_project) < 2:
            return patterns  # No cross-project vulnerabilities

        # Group vulnerabilities by pattern_type
        vuln_groups: Dict[str, List[tuple]] = defaultdict(list)
        for project_name, findings in security_by_project.items():
            for finding in findings:
                vuln_groups[finding.pattern_type].append((project_name, finding))

        # Find vulnerabilities appearing in multiple projects
        for pattern_type, occurrences in vuln_groups.items():
            projects_with_vuln = set(proj for proj, _ in occurrences)

            if len(projects_with_vuln) >= 2:
                findings_list = [finding for _, finding in occurrences]

                # Use most severe finding's severity
                max_severity = max(
                    findings_list, key=lambda f: self._severity_rank(f.severity)
                ).severity

                avg_confidence = sum(f.confidence for f in findings_list) / len(
                    findings_list
                )

                pattern = CrossProjectPattern(
                    pattern_type=pattern_type,
                    severity=max_severity,
                    category=AnalysisCategory.SECURITY,
                    projects_count=len(projects_with_vuln),
                    projects=sorted(list(projects_with_vuln)),
                    message=f"Security vulnerability '{pattern_type}' affecting {len(projects_with_vuln)} projects",
                    projects_confidence=avg_confidence,
                    evidence={
                        "vulnerability_type": pattern_type,
                        "projects_affected": list(projects_with_vuln),
                        "total_occurrences": len(findings_list),
                        "severity_distribution": self._severity_distribution(findings_list),
                    },
                )
                patterns.append(pattern)

        logger.info(f"Detected {len(patterns)} security vulnerabilities across projects")
        return patterns

    def detect_code_quality_trends(
        self, findings_by_project: Dict[str, List[AnalysisResult]]
    ) -> List[CrossProjectPattern]:
        """
        Detect code quality trends across the entire project corpus.

        Identifies quality issues that appear systematically across projects,
        such as common architectural violations, maintainability issues,
        and systematic patterns indicating shared architectural problems.

        Args:
            findings_by_project: Dict mapping project_name → List[AnalysisResult]

        Returns:
            List of CrossProjectPattern objects for quality trends.
        """
        patterns: List[CrossProjectPattern] = []

        if not findings_by_project or len(findings_by_project) < 2:
            return patterns

        # Analyze by category distribution and severity
        category_stats: Dict[AnalysisCategory, Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "projects": set()}
        )

        for project_name, findings in findings_by_project.items():
            for finding in findings:
                category_stats[finding.category]["total"] += 1
                category_stats[finding.category]["projects"].add(project_name)

        # Identify systemic quality issues (appearing in 60%+ of projects)
        min_projects = max(2, int(len(findings_by_project) * 0.6))

        for category, stats in category_stats.items():
            affected_projects = stats["projects"]

            if len(affected_projects) >= min_projects:
                # Find most common patterns in this category across projects
                category_findings = []
                for project_name, findings in findings_by_project.items():
                    category_findings.extend(
                        [f for f in findings if f.category == category]
                    )

                if category_findings:
                    # Get representative severity
                    severity_counts = defaultdict(int)
                    for f in category_findings:
                        severity_counts[f.severity] += 1

                    most_common_severity = max(
                        severity_counts.items(), key=lambda x: x[1]
                    )[0]

                    avg_confidence = sum(f.confidence for f in category_findings) / len(
                        category_findings
                    )

                    pattern = CrossProjectPattern(
                        pattern_type=f"quality_trend_{category.value}",
                        severity=most_common_severity,
                        category=category,
                        projects_count=len(affected_projects),
                        projects=sorted(list(affected_projects)),
                        message=f"Systemic {category.value} quality issue affecting {len(affected_projects)} projects",
                        projects_confidence=avg_confidence,
                        evidence={
                            "category": category.value,
                            "affected_projects": list(affected_projects),
                            "total_findings_in_category": len(category_findings),
                            "severity_distribution": dict(severity_counts),
                        },
                    )
                    patterns.append(pattern)

        logger.info(f"Detected {len(patterns)} code quality trends across projects")
        return patterns

    def analyze(
        self, findings_by_project: Dict[str, List[AnalysisResult]]
    ) -> List[CrossProjectPattern]:
        """
        Run all cross-project analysis detections.

        Orchestrates detection of:
        - Duplicate issues across projects
        - Security vulnerability patterns
        - Code quality trends

        Args:
            findings_by_project: Dict mapping project_name → List[AnalysisResult]

        Returns:
            List of all detected CrossProjectPattern objects.
        """
        all_patterns: List[CrossProjectPattern] = []

        if not findings_by_project:
            logger.info("No findings to analyze for cross-project patterns")
            return all_patterns

        logger.info(
            f"Cross-project pattern analysis: {len(findings_by_project)} projects, "
            f"{sum(len(f) for f in findings_by_project.values())} total findings"
        )

        # Phase 4: Run all detections
        all_patterns.extend(self.detect_duplicate_issues(findings_by_project))
        all_patterns.extend(self.detect_vulnerability_patterns(findings_by_project))
        all_patterns.extend(self.detect_code_quality_trends(findings_by_project))

        self.patterns = all_patterns
        logger.info(f"Detected {len(all_patterns)} cross-project patterns")
        return all_patterns

    def get_patterns(self) -> List[CrossProjectPattern]:
        """
        Get detected patterns.

        Returns:
            List of CrossProjectPattern objects.
        """
        return self.patterns

    # ==================
    # Helper Methods
    # ==================

    def _severity_rank(self, severity: Severity) -> int:
        """Map severity to numeric rank for comparison."""
        rank_map = {
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return rank_map.get(severity, 0)

    def _severity_distribution(
        self, findings: List[AnalysisResult]
    ) -> Dict[str, int]:
        """Calculate severity distribution across findings."""
        distribution = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for finding in findings:
            severity_str = (
                finding.severity.value
                if isinstance(finding.severity, Severity)
                else str(finding.severity)
            )
            if severity_str in distribution:
                distribution[severity_str] += 1
        return distribution
