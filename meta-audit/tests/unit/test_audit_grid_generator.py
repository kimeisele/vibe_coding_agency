"""Unit tests for Audit Grid Generator."""

import pytest
from pathlib import Path
from meta_audit.generators.audit_grid import (
    generate_audit_grid,
    FileMetrics,
)
from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory


class TestFileMetrics:
    """Test FileMetrics aggregation."""

    def test_initialization(self):
        """Test FileMetrics initialization."""
        file_path = Path("test_file.py")
        metrics = FileMetrics(file_path)

        assert metrics.file_path == file_path
        assert metrics.findings == []
        assert metrics.god_object_severity is None
        assert metrics.has_ai_slop is False
        assert metrics.complexity_scores == []
        assert metrics.security_issues == 0

    def test_add_god_object_finding(self):
        """Test adding god object finding."""
        metrics = FileMetrics(Path("test.py"))
        finding = AnalysisResult(
            analyzer_name="god_object_detector",
            pattern_type="god_object",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="God object detected",
            evidence={"srp_violation": True},
        )

        metrics.add_finding(finding)

        assert len(metrics.findings) == 1
        assert metrics.god_object_severity == Severity.HIGH
        assert metrics.srp_violation == "YES"

    def test_add_ai_slop_finding(self):
        """Test adding AI slop finding."""
        metrics = FileMetrics(Path("test.py"))
        finding = AnalysisResult(
            analyzer_name="ai_slop_analyzer",
            pattern_type="ai_slop",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="AI slop detected",
        )

        metrics.add_finding(finding)

        assert metrics.has_ai_slop is True

    def test_add_complexity_finding(self):
        """Test adding complexity finding."""
        metrics = FileMetrics(Path("test.py"))
        finding = AnalysisResult(
            analyzer_name="complexity",
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="High complexity",
            evidence={"complexity": 15},
        )

        metrics.add_finding(finding)

        assert 15 in metrics.complexity_scores

    def test_add_security_finding(self):
        """Test adding security finding."""
        metrics = FileMetrics(Path("test.py"))
        finding = AnalysisResult(
            analyzer_name="security",
            pattern_type="sql_injection",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            message="SQL injection risk",
        )

        metrics.add_finding(finding)

        assert metrics.security_issues == 1

    def test_srp_violation_detection(self):
        """Test SRP violation detection from evidence."""
        metrics = FileMetrics(Path("test.py"))

        # Finding WITHOUT srp_violation evidence
        finding1 = AnalysisResult(
            analyzer_name="god_object_detector",
            pattern_type="god_object",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="God object",
            evidence={"srp_violation": False},
        )
        metrics.add_finding(finding1)
        assert metrics.srp_violation == "NO"

        # Finding WITH srp_violation evidence
        metrics2 = FileMetrics(Path("test2.py"))
        finding2 = AnalysisResult(
            analyzer_name="god_object_detector",
            pattern_type="god_object",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="God object",
            evidence={"srp_violation": True},
        )
        metrics2.add_finding(finding2)
        assert metrics2.srp_violation == "YES"

    def test_god_object_indicator_mapping(self):
        """Test God Object severity to indicator mapping."""
        test_cases = [
            (Severity.CRITICAL, "CRITICAL"),
            (Severity.HIGH, "HIGH"),
            (Severity.MEDIUM, "MED"),  # Implementation uses "MED" for MEDIUM
            (Severity.LOW, "LOW"),
        ]

        for severity, expected_indicator in test_cases:
            metrics = FileMetrics(Path("test.py"))
            metrics.god_object_severity = severity
            assert metrics.god_object_indicator == expected_indicator

    def test_no_god_object_default(self):
        """Test default when no god object found."""
        metrics = FileMetrics(Path("test.py"))
        assert metrics.god_object_indicator == "LOW"


class TestAuditGridGeneratorFunction:
    """Test Audit Grid Generator function."""

    def test_generate_audit_grid_exists(self):
        """Test that generate_audit_grid function exists."""
        assert callable(generate_audit_grid)

    def test_generate_from_findings(self):
        """Test generating audit grid from findings."""
        findings = [
            AnalysisResult(
                analyzer_name="god_object_detector",
                file_path=Path("auth.py"),
                pattern_type="god_object",
                severity=Severity.HIGH,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="God object in auth module",
                evidence={"srp_violation": True, "lines": 600},
            ),
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=Path("auth.py"),
                pattern_type="ai_slop",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="AI slop detected",
            ),
        ]

        # Function should process findings and return markdown
        result = generate_audit_grid(findings)
        assert isinstance(result, str)
        assert len(result) > 0


class TestAuditGridGeneratorIntegration:
    """Integration tests for Audit Grid Generator."""

    def test_metrics_aggregation(self):
        """Test that metrics are properly aggregated by file."""
        metrics = FileMetrics(Path("complex_auth.py"))

        # Add multiple findings
        findings = [
            AnalysisResult(
                analyzer_name="god_object_detector",
                pattern_type="god_object",
                severity=Severity.HIGH,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="God object",
                evidence={"srp_violation": True},
            ),
            AnalysisResult(
                analyzer_name="complexity",
                pattern_type="high_complexity",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="High complexity",
                evidence={"complexity": 12},
            ),
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                pattern_type="ai_slop",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="AI slop",
            ),
            AnalysisResult(
                analyzer_name="security",
                pattern_type="sql_injection",
                severity=Severity.HIGH,
                category=AnalysisCategory.SECURITY,
                message="SQL injection",
            ),
        ]

        for finding in findings:
            metrics.add_finding(finding)

        # Verify aggregation
        assert len(metrics.findings) == 4
        assert metrics.god_object_severity == Severity.HIGH
        assert metrics.has_ai_slop is True
        assert len(metrics.complexity_scores) == 1
        assert metrics.security_issues == 1

    def test_theme_collection(self):
        """Test that themes are collected from findings."""
        metrics = FileMetrics(Path("test.py"))

        themes = [
            "generic_variable",
            "large_class",
            "security_b105",
            "complex_method",
        ]

        for theme in themes:
            finding = AnalysisResult(
                analyzer_name="test",
                pattern_type=theme,
                severity=Severity.LOW,
                category=AnalysisCategory.CODE_STRUCTURE,
                message=f"Found {theme}",
            )
            metrics.add_finding(finding)

        assert len(metrics.themes) == len(themes)
        for theme in themes:
            assert theme in metrics.themes


class TestAuditGridEdgeCases:
    """Test edge cases."""

    def test_file_with_no_findings(self):
        """Test file with no findings."""
        metrics = FileMetrics(Path("clean.py"))
        assert metrics.srp_violation == "NO"
        assert metrics.god_object_indicator == "LOW"
        assert metrics.has_ai_slop is False

    def test_file_with_multiple_god_object_findings(self):
        """Test file with multiple god object findings (last one wins)."""
        metrics = FileMetrics(Path("messy.py"))

        # Add multiple god object findings (shouldn't happen, but test resilience)
        for severity in [Severity.LOW, Severity.HIGH, Severity.CRITICAL]:
            finding = AnalysisResult(
                analyzer_name="god_object_detector",
                pattern_type="god_object",
                severity=severity,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="God object",
                evidence={},
            )
            metrics.add_finding(finding)

        # Last one should be stored
        assert metrics.god_object_severity == Severity.CRITICAL

    def test_complexity_with_invalid_values(self):
        """Test handling of invalid complexity values."""
        metrics = FileMetrics(Path("test.py"))

        # Valid complexity
        finding1 = AnalysisResult(
            analyzer_name="complexity",
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="High complexity",
            evidence={"complexity": 15},
        )
        metrics.add_finding(finding1)

        # Invalid complexity (string instead of int)
        finding2 = AnalysisResult(
            analyzer_name="complexity",
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            message="High complexity",
            evidence={"complexity": "not_a_number"},
        )
        metrics.add_finding(finding2)

        # Should only have the valid one
        assert len(metrics.complexity_scores) == 1
        assert metrics.complexity_scores[0] == 15
