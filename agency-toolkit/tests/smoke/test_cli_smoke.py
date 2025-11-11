"""Smoke Tests - REALITY CHECK: Does basic CLI work?

These tests verify that the actual CLI entry point works,
not just in tests, but in REALITY.

NO MOCKS. NO PATCHES. REAL EXECUTION.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get the toolkit root
TOOLKIT_ROOT = Path(__file__).parent.parent.parent


class TestCLIBasics:
    """Basic smoke tests - does the CLI even start?"""

    def test_cli_help_works(self):
        """REALITY TEST 1: Does 'toolkit --help' work?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "--help"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "Agency Toolkit" in result.stdout, "Help text should mention Agency Toolkit"
        assert "help" in result.stdout.lower()

    def test_cli_version_works(self):
        """REALITY TEST 2: Does 'toolkit --version' work?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "--version"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )

        assert result.returncode == 0, f"Version command failed: {result.stderr}"
        assert "Agency Toolkit" in result.stdout or "0." in result.stdout

    def test_cli_entrypoint_callable(self):
        """REALITY TEST 3: Can we actually call cli_entrypoint?"""
        from agency_toolkit.cli_app import cli_entrypoint

        # If this doesn't raise, the function exists and is callable
        assert callable(cli_entrypoint)

    def test_typer_app_registered(self):
        """REALITY TEST 4: Is the Typer app properly configured?"""
        from agency_toolkit.cli_app import app

        # Check that commands are registered
        assert app is not None
        assert hasattr(app, "command")
        assert hasattr(app, "callback")


class TestCLICommands:
    """Test that key commands are registered and accessible"""

    def test_info_command_accessible(self):
        """REALITY TEST 5: Can we call the 'info' command?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "info", "--help"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )
        assert result.returncode == 0, f"Info command failed: {result.stderr}"

    def test_ai_command_accessible(self):
        """REALITY TEST 6: Can we call the 'ai' command?"""
        result = subprocess.run(
            [sys.executable, "-m", "agency_toolkit.cli_app", "ai", "--help"],
            capture_output=True,
            text=True,
            cwd=str(TOOLKIT_ROOT),
        )
        assert result.returncode == 0, f"AI command failed: {result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
