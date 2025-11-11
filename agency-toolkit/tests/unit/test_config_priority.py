"""Unit tests for configuration priority chain (WU 9.1)."""

from pathlib import Path

from agency_toolkit.utils import load_config


class TestConfigPriority:
    """Test configuration priority chain."""

    def test_project_config_overrides_user_config(self, tmp_path, monkeypatch):
        """Test that project config.toml overrides user config.toml."""
        # Setup: Create user config directory
        user_config_dir = tmp_path / ".config" / "agency-toolkit"
        user_config_dir.mkdir(parents=True)
        user_config_path = user_config_dir / "config.toml"
        user_config_path.write_text(
            """
[settings]
output_dir = "./user-output"
social_style = "minimal"
social_color = "red"
"""
        )

        # Setup: Create project config in "current directory"
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_config_path = project_dir / "config.toml"
        project_config_path.write_text(
            """
[settings]
output_dir = "./client-renders"
social_color = "blue"
"""
        )

        # Mock HOME and CWD
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.chdir(project_dir)

        # Execute
        config = load_config()

        # Assert: Project config wins for output_dir and social_color
        assert config.output_dir == Path("./client-renders")
        assert config.social_color == "blue"
        # Assert: User config value for social_style is preserved
        assert config.social_style == "minimal"

    def test_config_files_merge_correctly(self, tmp_path, monkeypatch):
        """Test that config files with different keys merge correctly."""
        # Setup: User config with some keys
        user_config_dir = tmp_path / ".config" / "agency-toolkit"
        user_config_dir.mkdir(parents=True)
        user_config_path = user_config_dir / "config.toml"
        user_config_path.write_text(
            """
[settings]
social_style = "bold"

[image]
provider = "replicate"
"""
        )

        # Setup: Project config with different keys
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_config_path = project_dir / "config.toml"
        project_config_path.write_text(
            """
[settings]
output_dir = "./project-output"
social_color = "purple"

[image]
default_width = 800
"""
        )

        # Mock HOME and CWD
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.chdir(project_dir)

        # Execute
        config = load_config()

        # Assert: All values from both configs are present
        assert config.output_dir == Path("./project-output")
        assert config.social_color == "purple"
        assert config.social_style == "bold"
        assert config.image.provider == "replicate"
        assert config.image.default_width == 800

    def test_no_config_files_uses_defaults(self, tmp_path, monkeypatch):
        """Test that application defaults are used when no config files exist."""
        # Setup: Empty directory with no config files
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Mock HOME and CWD to ensure no config files exist
        monkeypatch.setenv("HOME", str(tmp_path / "nonexistent"))
        monkeypatch.chdir(empty_dir)

        # Execute
        config = load_config()

        # Assert: Application defaults are loaded
        assert config.output_dir == Path("./output")
        assert config.social_style == "modern"
        assert config.social_color == "blue"
        assert config.social_format == "square"
        assert config.image.provider == "pollinations"

    def test_user_config_only_no_project_config(self, tmp_path, monkeypatch):
        """Test that user config works when no project config exists."""
        # Setup: User config only
        user_config_dir = tmp_path / ".config" / "agency-toolkit"
        user_config_dir.mkdir(parents=True)
        user_config_path = user_config_dir / "config.toml"
        user_config_path.write_text(
            """
[settings]
social_style = "minimal"
output_dir = "./global-output"
"""
        )

        # Setup: Empty project directory (no config.toml)
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Mock HOME and CWD
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.chdir(project_dir)

        # Execute
        config = load_config()

        # Assert: User config values are applied
        assert config.social_style == "minimal"
        assert config.output_dir == Path("./global-output")

    def test_project_config_only_no_user_config(self, tmp_path, monkeypatch):
        """Test that project config works when no user config exists."""
        # Setup: Project config only
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_config_path = project_dir / "config.toml"
        project_config_path.write_text(
            """
[settings]
output_dir = "./local-output"
social_color = "green"
"""
        )

        # Mock: No user config directory
        monkeypatch.setenv("HOME", str(tmp_path / "nonexistent"))
        monkeypatch.chdir(project_dir)

        # Execute
        config = load_config()

        # Assert: Project config values are applied
        assert config.output_dir == Path("./local-output")
        assert config.social_color == "green"
        # Defaults still work
        assert config.social_style == "modern"
