"""Regression Tests - Output Snapshot Testing

These tests verify that OUTPUT doesn't change unexpectedly.
If the info command output changes, the test will FAIL - alerting us immediately.

This is the "Golden Master" pattern: store correct output, compare against it.
"""

import subprocess
import sys
from pathlib import Path

import pytest

TOOLKIT_ROOT = Path(__file__).parent.parent.parent
GOLDEN_MASTERS_DIR = Path(__file__).parent / "golden_masters"


class TestOutputRegression:
    """Output regression tests using golden master pattern"""

    @classmethod
    def setup_class(cls):
        """Create golden masters directory if needed."""
        GOLDEN_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    def test_info_info_output_stable(self):
        """REGRESSION TEST: Does 'toolkit info info' output stay the same?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "info", "info"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        actual_output = result.stdout

        golden_master_file = GOLDEN_MASTERS_DIR / "info_info_output.txt"

        if not golden_master_file.exists():
            # First run - save it
            golden_master_file.write_text(actual_output)
            print(f"Created golden master: {golden_master_file}")
        else:
            # Compare
            expected_output = golden_master_file.read_text()
            assert (
                actual_output == expected_output
            ), f"Output changed! Diff:\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"

    def test_cli_help_output_stable(self):
        """REGRESSION TEST: Does main help output stay the same?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "--help"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        actual_output = result.stdout

        golden_master_file = GOLDEN_MASTERS_DIR / "cli_help_output.txt"

        if not golden_master_file.exists():
            # First run - save it
            golden_master_file.write_text(actual_output)
            print(f"Created golden master: {golden_master_file}")
        else:
            # Compare
            expected_output = golden_master_file.read_text()
            assert (
                actual_output == expected_output
            ), f"Help output changed! This indicates API changes.\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
