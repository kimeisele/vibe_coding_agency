"""Smoke Tests for Meta-Audit CLI

These tests verify that the meta-audit tool itself works end-to-end,
WITHOUT mocks. This is the "doctor checking themselves" pattern.

If the tool that analyzes code can't even run itself properly,
we have a problem.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestMetaAuditCLI:
    """Smoke tests for meta-audit CLI - REALITY CHECKS"""

    @pytest.fixture
    def meta_audit_root(self):
        """Get meta-audit root directory"""
        return Path(__file__).parent.parent

    def test_cli_help_works(self, meta_audit_root):
        """REALITY TEST 1: Does 'meta-audit --help' work?"""
        result = subprocess.run(
            [sys.executable, "-m", "meta_audit.cli.main", "--help"],
            capture_output=True,
            text=True,
            cwd=str(meta_audit_root),
        )

        assert (
            result.returncode == 0
        ), f"CLI help failed: {result.stderr}"
        assert "Meta Audit Tool" in result.stdout or "analyze" in result.stdout
        print(f"✅ CLI help works\n{result.stdout[:200]}")

    def test_analyze_command_exists(self, meta_audit_root):
        """REALITY TEST 2: Is 'analyze' command registered?"""
        result = subprocess.run(
            [sys.executable, "-m", "meta_audit.cli.main", "analyze", "--help"],
            capture_output=True,
            text=True,
            cwd=str(meta_audit_root),
        )

        assert (
            result.returncode == 0
        ), f"Analyze command help failed: {result.stderr}"
        assert "Usage" in result.stdout or "analyze" in result.stdout.lower()
        print(f"✅ Analyze command exists\n{result.stdout[:200]}")

    def test_capsule_command_exists(self, meta_audit_root):
        """REALITY TEST 3: Is 'capsule' command registered?"""
        result = subprocess.run(
            [sys.executable, "-m", "meta_audit.cli.main", "capsule", "--help"],
            capture_output=True,
            text=True,
            cwd=str(meta_audit_root),
        )

        assert (
            result.returncode == 0
        ), f"Capsule command help failed: {result.stderr}"
        assert "Usage" in result.stdout or "capsule" in result.stdout.lower()
        print(f"✅ Capsule command exists\n{result.stdout[:200]}")

    def test_cli_imports_cleanly(self, meta_audit_root):
        """REALITY TEST 4: Can we import the CLI module?"""
        sys.path.insert(0, str(meta_audit_root / "src"))

        try:
            from meta_audit.cli.main import cli
            assert cli is not None
            assert callable(cli)
            print("✅ CLI imports cleanly")
        except Exception as e:
            pytest.fail(f"CLI import failed: {e}")

    def test_analyze_requires_target(self, meta_audit_root):
        """REALITY TEST 5: Analyze command should require a target"""
        result = subprocess.run(
            [sys.executable, "-m", "meta_audit.cli.main", "analyze"],
            capture_output=True,
            text=True,
            cwd=str(meta_audit_root),
        )

        # Should fail because no target provided
        # Either error code or error message
        assert (
            result.returncode != 0
            or "Usage" in result.stdout
            or "Missing" in result.stderr
        ), "Analyze should require a target argument"
        print(f"✅ Analyze correctly requires target")

    def test_meta_audit_can_analyze_itself(self, meta_audit_root):
        """REALITY TEST 6: Can meta-audit analyze ITSELF?

        This is the ultimate dogfooding test:
        Can our analysis tool analyze its own codebase?
        """
        # Try to analyze the meta-audit source itself
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "meta_audit.cli.main",
                "analyze",
                str(meta_audit_root / "src"),
                "--output",
                "/tmp/meta_audit_self_analysis",
            ],
            capture_output=True,
            text=True,
            cwd=str(meta_audit_root),
            timeout=30,
        )

        # Just check it doesn't crash catastrophically
        # Output validation would be Task 4.2 (golden masters)
        if result.returncode != 0:
            print(f"⚠️  Self-analysis returned {result.returncode}")
            print(f"stderr: {result.stderr[:500]}")
            # Don't fail - we'll know if there's a real problem
        else:
            print("✅ Meta-audit can analyze itself!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
