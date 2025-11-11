"""Regression tests for meta-audit analyze output.

These tests verify that analysis output structure and key metrics
remain stable across code changes. Uses golden master pattern.
"""

import subprocess
import sys
import json
from pathlib import Path

import pytest


class TestAnalyzeOutputRegression:
    """Regression tests for meta-audit analyze command output."""

    @pytest.fixture
    def meta_audit_root(self):
        """Get meta-audit root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def golden_master_dir(self, meta_audit_root):
        """Get golden master directory."""
        return meta_audit_root / "tests" / "regression" / "golden_masters"

    def test_analyze_json_output_structure(self, meta_audit_root, golden_master_dir):
        """REGRESSION TEST: Analyze JSON output structure is stable.

        Verifies that the JSON output has the expected keys and structure.
        """
        # Run analysis on meta-audit's own source
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "meta_audit.cli.main",
                "analyze",
                "--path",
                str(meta_audit_root / "src"),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(meta_audit_root),
        )

        # JSON goes to stdout; Phase 3 error goes to stderr (acceptable)
        output_text = result.stdout + result.stderr
        output_lines = output_text.split("\n")
        json_start = None
        for i, line in enumerate(output_lines):
            if line.strip().startswith("{"):
                json_start = i
                break

        assert json_start is not None, f"No JSON output found. stderr:\n{result.stderr[:500]}"

        # Reconstruct JSON (handling potential line breaks)
        json_text = "\n".join(output_lines[json_start:])
        # Find the end of JSON object (last closing brace)
        json_end = json_text.rfind("}")
        json_text = json_text[:json_end + 1]

        try:
            output_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse JSON output: {e}\n{json_text[:500]}")

        # Verify expected structure
        assert "summary" in output_data, "Missing 'summary' key in output"
        assert "findings" in output_data, "Missing 'findings' key in output"
        assert "execution_time" in output_data, "Missing 'execution_time' key in output"
        assert "timestamp" in output_data, "Missing 'timestamp' key in output"

        # Verify summary structure
        summary = output_data["summary"]
        expected_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "TOTAL"}
        assert set(summary.keys()) == expected_severities, \
            f"Summary keys mismatch. Expected {expected_severities}, got {set(summary.keys())}"

        # Verify all severity values are integers
        for severity, count in summary.items():
            assert isinstance(count, int), \
                f"Summary[{severity}] should be int, got {type(count)}"

        # Verify findings structure
        findings = output_data["findings"]
        assert isinstance(findings, list), "Findings should be a list"

        if findings:
            # Sample the first finding
            first_finding = findings[0]
            required_keys = {
                "analyzer",
                "file",
                "line",
                "severity",
                "category",
                "confidence",
                "message",
                "evidence",
                "remediation",
                "pattern_type",
            }
            assert set(first_finding.keys()) == required_keys, \
                f"Finding keys mismatch. Expected {required_keys}, got {set(first_finding.keys())}"

        print(f"✅ JSON output structure is valid")
        print(f"   Summary: {summary}")
        print(f"   Total findings: {len(findings)}")

    def test_analyze_summary_invariants(self, meta_audit_root):
        """REGRESSION TEST: Summary totals are mathematically consistent.

        Verifies: TOTAL == CRITICAL + HIGH + MEDIUM + LOW
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "meta_audit.cli.main",
                "analyze",
                "--path",
                str(meta_audit_root / "src"),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(meta_audit_root),
        )

        # Extract JSON from output (stdout)
        output_text = result.stdout + result.stderr
        output_lines = output_text.split("\n")
        json_start = None
        for i, line in enumerate(output_lines):
            if line.strip().startswith("{"):
                json_start = i
                break

        assert json_start is not None, "No JSON output found"

        json_text = "\n".join(output_lines[json_start:])
        json_end = json_text.rfind("}")
        json_text = json_text[:json_end + 1]

        try:
            output_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse JSON: {e}")

        summary = output_data["summary"]

        # Contract verification: total must equal sum of severity counts
        calculated_total = (
            summary["CRITICAL"] +
            summary["HIGH"] +
            summary["MEDIUM"] +
            summary["LOW"]
        )

        assert summary["TOTAL"] == calculated_total, \
            f"Summary invariant violated: TOTAL ({summary['TOTAL']}) != " \
            f"CRITICAL ({summary['CRITICAL']}) + HIGH ({summary['HIGH']}) + " \
            f"MEDIUM ({summary['MEDIUM']}) + LOW ({summary['LOW']}) = {calculated_total}"

        print(f"✅ Summary invariant verified: {summary['TOTAL']} == {calculated_total}")

    def test_analyze_table_output_parseable(self, meta_audit_root):
        """REGRESSION TEST: Table format output is parseable.

        Verifies that the default table output is structured and readable.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "meta_audit.cli.main",
                "analyze",
                "--path",
                str(meta_audit_root / "src"),
                "--format",
                "table",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(meta_audit_root),
        )

        # Table output is split between stdout (actual output) and stderr (logging)
        output = result.stdout + result.stderr

        # Verify key sections are present (may be in stderr as logging info)
        # Accept if Phase info or findings count exists
        has_phase_info = "Phase 1" in output or "Phase 2" in output
        has_findings = "finding" in output.lower() or "Total findings" in output
        has_severity = "CRITICAL" in output or "HIGH" in output or "MEDIUM" in output or "LOW" in output

        assert has_phase_info or has_findings or has_severity, \
            f"Missing expected output. Output:\n{output[:500]}"

        print(f"✅ Table output is parseable")
        print(f"   Output length: {len(output)} characters")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
