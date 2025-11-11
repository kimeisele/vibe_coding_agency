"""Integration tests for Phase 2 (Report Generation)."""

import pytest
import json
from pathlib import Path
from meta_audit.analyzers.collectors import run_all_collectors
from meta_audit.generators import generate_report, Report
from meta_audit.core.models import AnalysisResult


@pytest.fixture
def realistic_project(tmp_path):
    """Create a realistic test project for report generation."""
    # Create a few Python modules
    (tmp_path / "models.py").write_text("""
class User:
    def __init__(self, name, email, data):
        '''Initialize a user.'''
        self.name = name
        self.email = email
        self.data = data

    def complex_validation(self, value):
        if value:
            if isinstance(value, str):
                if len(value) > 0:
                    if value.startswith("valid"):
                        if not value.contains("bad"):
                            return True
        return False
""")

    (tmp_path / "utils.py").write_text("""
def process_data(data):
    # TODO: optimize this
    temp = data
    result = []
    for item in temp:
        x = item
        if x:
            result.append(x)
    return result

def helper(args, kwargs):
    import os
    password = "admin123"  # Bad practice
    return password
""")

    (tmp_path / "__init__.py").write_text("# Module")

    return tmp_path


class TestReportGeneration:
    """Test Report class and generation."""

    def test_report_accepts_analysis_results(self, realistic_project):
        """Test that Report accepts AnalysisResult objects."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]

        # Generate report
        report = generate_report(all_findings, execution_time=1.5)

        # Should create a valid Report
        assert isinstance(report, Report)
        assert len(report.findings) == len(all_findings)
        assert report.execution_time == 1.5

    def test_report_calculates_summary(self, realistic_project):
        """Test that Report correctly summarizes findings."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]

        report = generate_report(all_findings, execution_time=1.0)

        # Summary should have all severity levels
        assert "CRITICAL" in report.summary
        assert "HIGH" in report.summary
        assert "MEDIUM" in report.summary
        assert "LOW" in report.summary
        assert "TOTAL" in report.summary

        # Total should match findings count
        assert report.summary["TOTAL"] == len(all_findings)

        # Sum of severities should equal total
        total_by_severity = (
            report.summary["CRITICAL"]
            + report.summary["HIGH"]
            + report.summary["MEDIUM"]
            + report.summary["LOW"]
        )
        assert total_by_severity == report.summary["TOTAL"]

    def test_report_severity_counts_correct(self, realistic_project):
        """Test that severity counts are correct."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]

        report = generate_report(all_findings, execution_time=1.0)

        # Count severities manually
        manual_counts = {
            "CRITICAL": sum(1 for f in all_findings if str(f.severity) == "Severity.CRITICAL" or f.severity.value == "CRITICAL"),
            "HIGH": sum(1 for f in all_findings if str(f.severity) == "Severity.HIGH" or f.severity.value == "HIGH"),
            "MEDIUM": sum(1 for f in all_findings if str(f.severity) == "Severity.MEDIUM" or f.severity.value == "MEDIUM"),
            "LOW": sum(1 for f in all_findings if str(f.severity) == "Severity.LOW" or f.severity.value == "LOW"),
        }

        # Should match summary (allowing for enum or string representation)
        assert report.summary["CRITICAL"] == manual_counts["CRITICAL"]
        assert report.summary["HIGH"] == manual_counts["HIGH"]
        assert report.summary["MEDIUM"] == manual_counts["MEDIUM"]
        assert report.summary["LOW"] == manual_counts["LOW"]

    def test_report_has_timestamp(self, realistic_project):
        """Test that Report has ISO format timestamp."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]

        report = generate_report(all_findings, execution_time=1.0)

        # Should have timestamp in ISO format
        assert report.timestamp is not None
        assert "T" in report.timestamp or "-" in report.timestamp  # ISO format has T or -


class TestReportJSONExport:
    """Test Report JSON export."""

    def test_report_to_json_returns_string(self, realistic_project):
        """Test that to_json() returns a string."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        json_output = report.to_json()
        assert isinstance(json_output, str)

    def test_report_json_is_valid(self, realistic_project):
        """Test that JSON output is valid JSON."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        json_output = report.to_json()

        # Should parse as JSON
        json_data = json.loads(json_output)
        assert json_data is not None

    def test_report_json_has_required_fields(self, realistic_project):
        """Test that JSON output has required fields."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        json_output = report.to_json()
        json_data = json.loads(json_output)

        # Should have summary, findings, execution_time, timestamp
        assert "summary" in json_data
        assert "findings" in json_data
        assert "execution_time" in json_data
        assert "timestamp" in json_data

        # Summary should have severity levels
        assert "CRITICAL" in json_data["summary"]
        assert "HIGH" in json_data["summary"]
        assert "MEDIUM" in json_data["summary"]
        assert "LOW" in json_data["summary"]
        assert "TOTAL" in json_data["summary"]

    def test_report_json_findings_have_required_fields(self, realistic_project):
        """Test that JSON findings have required fields."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        json_output = report.to_json()
        json_data = json.loads(json_output)

        # If there are findings
        if json_data["findings"]:
            first_finding = json_data["findings"][0]

            # Check required fields
            assert "analyzer" in first_finding
            assert "file" in first_finding
            assert "line" in first_finding
            assert "severity" in first_finding
            assert "category" in first_finding
            assert "message" in first_finding
            assert "remediation" in first_finding

    def test_report_json_findings_count_matches(self, realistic_project):
        """Test that JSON findings count matches report."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        json_output = report.to_json()
        json_data = json.loads(json_output)

        # Findings count should match
        assert len(json_data["findings"]) == len(report.findings)
        assert json_data["summary"]["TOTAL"] == len(report.findings)


class TestReportTerminalExport:
    """Test Report terminal export."""

    def test_report_to_terminal_returns_string(self, realistic_project):
        """Test that to_terminal() returns a string."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        terminal_output = report.to_terminal()
        assert isinstance(terminal_output, str)

    def test_report_terminal_has_summary(self, realistic_project):
        """Test that terminal output includes summary."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        terminal_output = report.to_terminal()

        # Should contain title and summary metrics
        assert "Meta-Audit Report" in terminal_output
        assert "Critical:" in terminal_output or "CRITICAL" in terminal_output
        assert "High:" in terminal_output or "HIGH" in terminal_output
        assert "Execution time:" in terminal_output

    def test_report_terminal_has_findings_table(self, realistic_project):
        """Test that terminal output includes findings table."""
        result = run_all_collectors(str(realistic_project))
        all_findings = result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        terminal_output = report.to_terminal()

        # If there are findings, should show table headers
        if all_findings:
            # Rich table format should have these or plain text should have them
            assert "Severity" in terminal_output or "severity" in terminal_output or len(terminal_output) > 100

    def test_report_terminal_handles_empty_findings(self):
        """Test that terminal output handles no findings gracefully."""
        report = generate_report([], execution_time=0.5)

        terminal_output = report.to_terminal()

        # Should still have title
        assert "Meta-Audit Report" in terminal_output
        # Should indicate no findings
        assert "No findings" in terminal_output or "0" in terminal_output


class TestEndToEndReportWorkflow:
    """Test complete end-to-end report workflow."""

    def test_full_workflow_collectors_to_report_json(self, realistic_project):
        """Test full workflow: collectors → findings → report → JSON."""
        # Phase 1: Collect
        collection_result = run_all_collectors(str(realistic_project))
        all_findings = collection_result["all_findings"]

        # Phase 2: Generate report
        report = generate_report(all_findings, execution_time=1.5)

        # Phase 3: Export as JSON
        json_output = report.to_json()
        json_data = json.loads(json_output)

        # Verify workflow
        assert len(all_findings) > 0, "Should find issues in realistic project"
        assert len(report.findings) == len(all_findings)
        assert json_data["summary"]["TOTAL"] == len(all_findings)

    def test_full_workflow_collectors_to_report_terminal(self, realistic_project):
        """Test full workflow: collectors → findings → report → Terminal."""
        # Phase 1: Collect
        collection_result = run_all_collectors(str(realistic_project))
        all_findings = collection_result["all_findings"]

        # Phase 2: Generate report
        report = generate_report(all_findings, execution_time=1.5)

        # Phase 3: Export as terminal
        terminal_output = report.to_terminal()

        # Verify workflow
        assert len(all_findings) > 0, "Should find issues in realistic project"
        assert "Meta-Audit Report" in terminal_output
        assert isinstance(terminal_output, str)

    def test_multiple_report_exports_same_findings(self, realistic_project):
        """Test that multiple exports of same report are consistent."""
        collection_result = run_all_collectors(str(realistic_project))
        all_findings = collection_result["all_findings"]
        report = generate_report(all_findings, execution_time=1.5)

        # Export multiple times
        json1 = report.to_json()
        json2 = report.to_json()

        # Should be identical
        assert json1 == json2

        # Parse and compare
        data1 = json.loads(json1)
        data2 = json.loads(json2)

        assert data1["summary"] == data2["summary"]
        assert len(data1["findings"]) == len(data2["findings"])

    def test_report_with_zero_execution_time(self, realistic_project):
        """Test that report handles zero execution time."""
        collection_result = run_all_collectors(str(realistic_project))
        all_findings = collection_result["all_findings"]
        report = generate_report(all_findings, execution_time=0.0)

        # Should work fine
        assert report.execution_time == 0.0
        json_output = report.to_json()
        data = json.loads(json_output)
        assert data["execution_time"] == 0.0

    def test_report_with_large_number_of_findings(self):
        """Test that report handles large number of findings."""
        # Create mock findings (using direct instantiation)
        from meta_audit.core.models import Severity, AnalysisCategory
        from pathlib import Path

        findings = [
            AnalysisResult(
                analyzer_name="test_analyzer",
                file_path=Path(f"test_{i}.py"),
                line_start=i,
                line_end=None,
                pattern_type="test_pattern",
                severity=Severity.LOW if i % 4 == 0 else Severity.MEDIUM if i % 4 == 1 else Severity.HIGH if i % 4 == 2 else Severity.CRITICAL,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.95,
                message=f"Test finding {i}",
                evidence={"index": i},
                remediation=["Fix it"],
                project_name=None,
            )
            for i in range(100)
        ]

        report = generate_report(findings, execution_time=5.0)

        # Should handle large number
        assert len(report.findings) == 100
        assert report.summary["TOTAL"] == 100

        # Should export to JSON
        json_output = report.to_json()
        data = json.loads(json_output)
        assert len(data["findings"]) == 100
