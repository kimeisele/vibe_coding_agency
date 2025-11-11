"""CLI integration test fixtures and utilities.

These tests run the actual CLI as a subprocess to catch entry point issues.
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def cli_runner(tmp_path):
    """Fixture to run CLI commands in isolated temp directory.

    Usage:
        def test_something(cli_runner):
            result = cli_runner("social", "generate", "Test", "--dry-run")
            assert result.returncode == 0
    """
    # Get the project root (where agency_toolkit package is)
    project_root = Path(__file__).parent.parent.parent

    def run_cli(*args, cwd=None, env=None):
        """Run CLI command and return CompletedProcess.

        Note: Always runs command from project root to ensure module imports work,
        but may execute in different cwd for file operations (via --output option).
        """
        cmd = ["python", "-m", "agency_toolkit.cli_app", *args]
        # ALWAYS run from project_root to ensure imports work
        # If tests need to verify files in tmp_path, they should use --output option
        return subprocess.run(
            cmd,
            cwd=project_root,  # ALWAYS project root for module resolution
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

    return run_cli


@pytest.fixture
def output_dir(tmp_path):
    """Fixture providing clean output directory for tests."""
    output = tmp_path / "output"
    output.mkdir(parents=True, exist_ok=True)
    return output


@pytest.fixture
def sample_config_file(tmp_path):
    """Fixture creating a sample config.toml for testing."""
    config_content = """
[output]
dir = "./output"

[social]
style = "modern"
color = "blue"
format = "square"

[briefing]
type = "default"

[mistral]
model = "mistral-small-latest"
temperature = 0.7
max_tokens = 1000
"""
    config_path = tmp_path / "config.toml"
    config_path.write_text(config_content)
    return config_path
