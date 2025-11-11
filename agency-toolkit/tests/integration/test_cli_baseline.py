"""Baseline CLI integration tests.

These tests verify the CLI works as a user would invoke it (subprocess).
Created as part of WU-1.3 to establish baseline before refactoring.
"""

import pytest


def test_cli_help_shows_commands(cli_runner):
    """Test that --help shows available commands."""
    result = cli_runner("--help")

    assert result.returncode == 0
    assert "social" in result.stdout
    assert "briefing" in result.stdout
    assert "structure" in result.stdout
    assert "image" in result.stdout
    assert "ai" in result.stdout


def test_social_dry_run_does_not_create_file(cli_runner, tmp_path):
    """Test social generate with --dry-run doesn't create files."""
    result = cli_runner(
        "social", "generate", "Test", "--dry-run", "--output", str(tmp_path)
    )

    assert result.returncode == 0
    assert "[DRY RUN]" in result.stdout

    # Verify no output directory created
    output_dir = tmp_path / "social"
    assert not output_dir.exists() or len(list(output_dir.glob("*.png"))) == 0


@pytest.mark.skip(reason="Font loading hangs - known issue, to be fixed in refactoring")
def test_social_generate_creates_png(cli_runner, tmp_path):
    """Test social generate creates actual PNG file."""
    result = cli_runner("social", "generate", "Test Post", cwd=tmp_path)

    assert result.returncode == 0

    output_dir = tmp_path / "output" / "social"
    pngs = list(output_dir.glob("*.png"))
    assert len(pngs) == 1
    assert pngs[0].stat().st_size > 0


def test_social_with_invalid_style_shows_error(cli_runner, tmp_path):
    """Test social generate with invalid style shows user-friendly error."""
    result = cli_runner(
        "social",
        "generate",
        "Test",
        "--style",
        "invalid_style",
        "--dry-run",
        "--output",
        str(tmp_path),
    )

    # Should fail with non-zero exit code
    assert result.returncode != 0
    # Error message should mention the invalid style
    assert "invalid_style" in result.stderr or "invalid_style" in result.stdout


def test_structure_dry_run_does_not_create_folders(cli_runner, tmp_path):
    """Test structure command with --dry-run doesn't create folders."""
    result = cli_runner(
        "structure",
        "create",
        "Test Client",
        "Test Project",
        "--dry-run",
        "--base-path",
        str(tmp_path),
    )

    assert result.returncode == 0
    assert "[DRY RUN]" in result.stdout or "Would create" in result.stdout

    # Verify no project directory created
    project_dir = tmp_path / "test-client-test-project"
    assert not project_dir.exists()


# Placeholder tests for Epic 4 (full CLI integration suite)
@pytest.mark.skip(reason="To be implemented in Epic 4 - WU-4.2")
def test_briefing_creates_markdown_file(cli_runner, tmp_path):
    """TODO: Epic 4 - Test briefing command creates MD file."""
    pass


@pytest.mark.skip(reason="To be implemented in Epic 4 - WU-4.2")
def test_image_with_invalid_provider_shows_error(cli_runner, tmp_path):
    """TODO: Epic 4 - Test image command with invalid provider."""
    pass


@pytest.mark.skip(reason="To be implemented in Epic 4 - WU-4.2")
def test_ai_without_api_key_shows_error(cli_runner, tmp_path):
    """TODO: Epic 4 - Test ai command without API key."""
    pass
