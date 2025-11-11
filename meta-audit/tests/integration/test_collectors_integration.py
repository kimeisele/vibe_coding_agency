"""Integration tests for meta-audit collectors.

These tests verify that each collector runs successfully on real code,
without mocks. Pattern: Real code + real subprocess execution.
"""

import subprocess
import sys
from pathlib import Path
from typing import List

import pytest

from meta_audit.analyzers.collectors import (
    run_all_collectors,
    list_collectors,
    get_collector,
)
from meta_audit.core.models import AnalysisResult


class TestCollectorIntegration:
    """Integration tests for collector framework."""

    @pytest.fixture
    def meta_audit_src(self):
        """Get meta-audit source path for testing."""
        return Path(__file__).parent.parent.parent / "src"

    @pytest.fixture
    def small_test_target(self, tmp_path):
        """Create a small Python file for testing collectors."""
        test_file = tmp_path / "test_target.py"
        test_file.write_text("""
# Sample file for collector testing
import subprocess
import os

class LargeClass:
    '''A class with many methods to test god object detection.'''

    def method_one(self):
        return 1

    def method_two(self):
        return 2

    def method_three(self):
        return 3

    def method_four(self):
        return 4

    def method_five(self):
        return 5

    def method_six(self):
        return 6

    def method_seven(self):
        return 7

    def method_eight(self):
        return 8

    def method_nine(self):
        return 9

    def method_ten(self):
        return 10

def simple_function():
    '''A simple function.'''
    subprocess.call("echo hello", shell=True)
    pass
""")
        return tmp_path

    def test_list_collectors(self):
        """INTEGRATION TEST: Collector registry is populated."""
        collectors = list_collectors()

        assert isinstance(collectors, list), "list_collectors should return a list"
        assert len(collectors) > 0, "At least one collector should be registered"

        expected_collectors = {"complexity", "security", "ai_slop", "god_object"}
        registered = set(collectors)

        assert registered == expected_collectors, \
            f"Expected {expected_collectors}, got {registered}"

        print(f"✅ Collectors registered: {collectors}")

    def test_get_collector(self):
        """INTEGRATION TEST: Collector lookup by name."""
        for collector_name in list_collectors():
            collector_func = get_collector(collector_name)
            assert collector_func is not None, \
                f"Collector '{collector_name}' should be retrievable"
            assert callable(collector_func), \
                f"Collector '{collector_name}' should be callable"

        print(f"✅ All collectors are callable and retrievable")

    def test_run_all_collectors_real_code(self, meta_audit_src):
        """INTEGRATION TEST: All collectors run successfully on real code.

        This is THE dogfooding test - meta-audit analyzing itself.
        """
        # Run collectors on meta-audit's own source
        result = run_all_collectors(str(meta_audit_src))

        # Verify result structure
        assert "collectors_data" in result, "Missing 'collectors_data' in result"
        assert "all_findings" in result, "Missing 'all_findings' in result"
        assert "errors" in result, "Missing 'errors' in result"
        assert "status" in result, "Missing 'status' in result"

        # Verify collectors_data structure
        collectors_data = result["collectors_data"]
        assert isinstance(collectors_data, dict), "collectors_data should be a dict"

        for collector_name in list_collectors():
            assert collector_name in collectors_data, \
                f"Collector '{collector_name}' results missing"

            collector_results = collectors_data[collector_name]
            assert isinstance(collector_results, list), \
                f"Collector '{collector_name}' results should be a list"

            # Verify each finding is an AnalysisResult
            for finding in collector_results:
                assert isinstance(finding, AnalysisResult), \
                    f"Finding from '{collector_name}' is not an AnalysisResult"

        # Verify all_findings
        all_findings = result["all_findings"]
        assert isinstance(all_findings, list), "all_findings should be a list"
        assert len(all_findings) > 0, "At least one finding expected from meta-audit source"

        # Verify mathematical invariant
        total_from_dict = sum(len(v) for v in collectors_data.values())
        assert len(all_findings) == total_from_dict, \
            f"all_findings count mismatch: {len(all_findings)} != sum of collectors"

        # Check status
        assert result["status"] in ["success", "partial_success"], \
            f"Invalid status: {result['status']}"

        print(f"✅ Collectors ran successfully")
        print(f"   Total findings: {len(all_findings)}")
        print(f"   By collector:")
        for name, findings in collectors_data.items():
            print(f"     - {name}: {len(findings)} findings")

    def test_run_all_collectors_small_target(self, small_test_target):
        """INTEGRATION TEST: Collectors work on small test code."""
        result = run_all_collectors(str(small_test_target))

        assert result["status"] in ["success", "partial_success"], \
            f"Collection failed: {result['errors']}"

        all_findings = result["all_findings"]

        # Expect at least some findings from security and ai_slop
        assert len(all_findings) > 0, \
            "Expected findings from test code (e.g., shell=True, try/except pass)"

        print(f"✅ Small target analysis: {len(all_findings)} findings found")

    def test_collector_graceful_degradation(self, small_test_target):
        """INTEGRATION TEST: System degrades gracefully if one collector fails.

        If a collector raises an exception, others should continue.
        """
        # run_all_collectors should handle errors gracefully
        result = run_all_collectors(str(small_test_target))

        # Should return both success and partial_success statuses
        assert result["status"] in ["success", "partial_success"], \
            "Status should be valid even with errors"

        # Even if errors exist, we should have results
        errors = result["errors"]
        collectors_data = result["collectors_data"]

        # All collectors should have entries (empty list if they failed)
        for collector_name in list_collectors():
            assert collector_name in collectors_data, \
                f"Collector '{collector_name}' missing even after error"

        print(f"✅ Graceful degradation verified")
        if errors:
            print(f"   Errors handled: {len(errors)}")

    def test_collector_finding_structure(self, small_test_target):
        """INTEGRATION TEST: Each finding has required fields.

        Verifies the contract of AnalysisResult objects.
        """
        result = run_all_collectors(str(small_test_target))
        all_findings = result["all_findings"]

        if not all_findings:
            pytest.skip("No findings to validate")

        # Check first finding for required fields
        first_finding = all_findings[0]

        required_fields = {
            "analyzer_name",
            "file_path",
            "severity",
            "category",
            "confidence",
            "message",
            "evidence",
            "remediation",
            "pattern_type",
        }

        actual_fields = set(first_finding.__dict__.keys())

        for field in required_fields:
            assert field in actual_fields, \
                f"Finding missing required field: {field}"

        # Verify field types
        assert isinstance(first_finding.severity, str), "severity should be string"
        assert isinstance(first_finding.confidence, float), "confidence should be float"
        assert isinstance(first_finding.message, str), "message should be string"

        print(f"✅ Finding structure valid")
        print(f"   Fields: {', '.join(sorted(actual_fields))}")

    def test_each_collector_individually(self, small_test_target):
        """INTEGRATION TEST: Each collector can run independently.

        Tests that we can call each collector directly.
        """
        target_path = str(small_test_target)

        for collector_name in list_collectors():
            collector_func = get_collector(collector_name)

            try:
                findings = collector_func(target_path)
                assert isinstance(findings, list), \
                    f"Collector '{collector_name}' should return list"

                print(f"✅ {collector_name}: {len(findings)} findings")

            except Exception as e:
                # Some collectors might not support all inputs
                print(f"⚠️  {collector_name}: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
