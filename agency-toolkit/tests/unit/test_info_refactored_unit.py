"""Unit tests for refactored info.py functions."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from agency_toolkit.commands.info import (
    _calculate_provider_counts,
    _check_image_provider_status,
    _check_text_provider_status,
    _create_providers_table,
    _display_commands_section,
    _display_help_section,
    _display_image_providers_section,
    _display_providers_header,
    _display_providers_summary,
    _display_providers_table,
    _display_seed_templates_section,
    _display_social_templates_section,
    _get_image_providers,
    _get_text_providers,
    get_available_providers,
    get_available_seed_templates,
    get_available_social_templates,
    load_toolkit_docs,
)
from agency_toolkit.core.reporter import Reporter


class TestGetAvailableFunctions:
    """Test functions that retrieve available resources."""

    def test_get_available_social_templates(self):
        """Test retrieving available social templates."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create mock template directory
            template_dir = Path(tmp_dir) / "templates" / "social"
            template_dir.mkdir(parents=True)

            # Create test templates
            template1 = template_dir / "modern.json"
            template2 = template_dir / "bold.json"
            template1.write_text(json.dumps({"description": "Modern style"}))
            template2.write_text(json.dumps({"description": "Bold style"}))

            # Mock __file__ to point to our temp directory structure
            mock_file = str(Path(tmp_dir) / "agency_toolkit" / "commands" / "info.py")
            with patch("agency_toolkit.commands.info.__file__", mock_file):
                templates = get_available_social_templates()

                assert len(templates) == 2
                assert "modern" in templates
                assert "bold" in templates
                assert templates["modern"] == "Modern style"
                assert templates["bold"] == "Bold style"

    def test_get_available_seed_templates(self):
        """Test retrieving available seed templates."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create mock registry directory structure
            registry_dir = Path(tmp_dir) / "registry" / "seeds"
            registry_dir.mkdir(parents=True)

            seed_path = registry_dir / "templates.json"
            seed_data = {
                "templates": {
                    "template1": {"description": "Seed template 1"},
                    "template2": {"description": "Seed template 2"},
                }
            }
            seed_path.write_text(json.dumps(seed_data))

            # Mock __file__ to point to our temp directory structure
            mock_file = str(Path(tmp_dir) / "agency_toolkit" / "commands" / "info.py")
            with patch("agency_toolkit.commands.info.__file__", mock_file):
                seeds = get_available_seed_templates()

                assert len(seeds) == 2
                assert "template1" in seeds
                assert "template2" in seeds
                assert seeds["template1"] == "Seed template 1"

    def test_get_available_providers(self):
        """Test retrieving available providers."""
        providers = get_available_providers()

        assert "pollinations" in providers
        assert "replicate" in providers
        assert (
            providers["pollinations"]["description"]
            == "Free AI image generation (default)"
        )
        assert providers["pollinations"]["status"] == "✅ Default"
        assert (
            providers["replicate"]["description"]
            == "Replicate API (optional, requires API key)"
        )


class TestLoadToolkitDocs:
    """Test documentation loading functionality."""

    def test_load_toolkit_docs_with_cache(self):
        """Test loading docs from cache."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir) / ".cache" / "agency-toolkit"
            cache_file = cache_dir / "docs_context.txt"
            cache_dir.mkdir(parents=True)

            # Create cached file
            cache_file.write_text("cached content")

            with patch("agency_toolkit.commands.info.Path") as mock_path:
                mock_path.home.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = cache_file

                content = load_toolkit_docs()
                assert content == "cached content"

    def test_load_toolkit_docs_build_cache(self):
        """Test building docs cache from source files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir) / ".cache" / "agency-toolkit"
            docs_dir = Path(tmp_dir) / "docs"
            cache_file = cache_dir / "docs_context.txt"

            # Create source files
            docs_dir.mkdir()
            (docs_dir / "BLUEPRINT.yaml").write_text("blueprint content")
            (docs_dir / "IMPLEMENTATION.yaml").write_text("implementation content")
            (docs_dir / "ROADMAP.md").write_text("roadmap content")

            # Mock __file__ to point to our temp directory structure
            mock_file = str(Path(tmp_dir) / "agency_toolkit" / "commands" / "info.py")

            with patch("agency_toolkit.commands.info.__file__", mock_file):
                with patch("agency_toolkit.commands.info.Path.home") as mock_home:
                    mock_home.return_value = Path(tmp_dir)

                    content = load_toolkit_docs()

                    assert "blueprint content" in content
                    assert "implementation content" in content
                    assert "roadmap content" in content
                    assert cache_file.exists()


class TestProviderStatusFunctions:
    """Test provider status checking functions."""

    def test_get_text_providers(self):
        """Test getting text providers list."""
        providers = _get_text_providers()

        assert len(providers) == 2
        assert ("Mistral", "MISTRAL_API_KEY") in providers
        assert ("Google GenAI", "GOOGLE_API_KEY") in providers

    def test_get_image_providers(self):
        """Test getting image providers list."""
        providers = _get_image_providers()

        assert len(providers) == 2
        assert ("Pollinations", None, "No API key needed") in providers
        assert (
            "Replicate",
            "REPLICATE_API_TOKEN",
            "Set for better quality",
        ) in providers

    @patch.dict("os.environ", {"MISTRAL_API_KEY": "test_key_123"})
    def test_check_text_provider_status_configured(self):
        """Test text provider status when configured."""
        status, details = _check_text_provider_status("Mistral", "MISTRAL_API_KEY")

        assert "[green]✓ Ready[/green]" in status
        assert "API key set (12 chars)" in details

    @patch.dict("os.environ", {}, clear=True)
    def test_check_text_provider_status_not_configured(self):
        """Test text provider status when not configured."""
        status, details = _check_text_provider_status("Mistral", "MISTRAL_API_KEY")

        assert "[red]✗ Not configured[/red]" in status
        assert "Set MISTRAL_API_KEY environment variable" in details

    @patch.dict("os.environ", {}, clear=True)
    def test_check_image_provider_status_no_key_needed(self):
        """Test image provider status when no key needed."""
        status, details = _check_image_provider_status(
            "Pollinations", None, "No API key needed"
        )

        assert "[green]✓ Ready[/green]" in status
        assert details == "No API key needed"

    @patch.dict("os.environ", {"REPLICATE_API_TOKEN": "test_token"})
    def test_check_image_provider_status_configured(self):
        """Test image provider status when configured."""
        status, details = _check_image_provider_status(
            "Replicate", "REPLICATE_API_TOKEN", "Set for better quality"
        )

        assert "[green]✓ Ready[/green]" in status
        assert "API key set (10 chars)" in details

    @patch.dict("os.environ", {}, clear=True)
    def test_check_image_provider_status_optional(self):
        """Test image provider status when optional but not configured."""
        status, details = _check_image_provider_status(
            "Replicate", "REPLICATE_API_TOKEN", "Set for better quality"
        )

        assert "[yellow]⚠ Optional[/yellow]" in status
        assert "Set REPLICATE_API_TOKEN for better quality" in details

    @patch.dict("os.environ", {"MISTRAL_API_KEY": "test_key"}, clear=True)
    def test_calculate_provider_counts(self):
        """Test calculating provider configuration counts."""
        configured, total = _calculate_provider_counts()

        # Should count 1 configured (Mistral) out of 3 total providers
        # 2 text providers + 1 image provider with env_var (Replicate)
        assert configured == 1
        assert total == 3  # 2 text providers + 1 image provider (Replicate)

    def test_create_providers_table(self):
        """Test creating providers status table."""
        table = _create_providers_table()

        assert table is not None
        # Table should have rows for all providers
        assert len(table.rows) == 4  # 2 text + 2 image providers


class TestDisplayFunctions:
    """Test display functions with Reporter integration."""

    def test_display_providers_header(self):
        """Test displaying providers header."""
        mock_reporter = Mock(spec=Reporter)

        _display_providers_header(mock_reporter)

        mock_reporter.info.assert_any_call("")
        mock_reporter.info.assert_any_call("Provider Configuration Status")
        mock_reporter.divider.assert_called_once()

    def test_display_providers_table(self):
        """Test displaying providers table."""
        mock_reporter = Mock(spec=Reporter)

        with patch("rich.console.Console") as mock_console_class:
            mock_console = Mock()
            mock_console_class.return_value = mock_console

            _display_providers_table(mock_reporter)

            mock_console.print.assert_called()
            # Should print table and empty line
            assert mock_console.print.call_count == 2

    @patch.dict("os.environ", {}, clear=True)
    def test_display_providers_summary_no_configured(self):
        """Test displaying summary when no providers configured."""
        mock_reporter = Mock(spec=Reporter)

        _display_providers_summary(mock_reporter)

        mock_reporter.warning.assert_called_once()
        mock_reporter.info.assert_any_call("Quick setup:")
        mock_reporter.info.assert_any_call("  export MISTRAL_API_KEY='your-key'")

    @patch.dict(
        "os.environ",
        {
            "MISTRAL_API_KEY": "test_key",
            "GOOGLE_API_KEY": "test_key",
            "REPLICATE_API_TOKEN": "test_token",
        },
    )
    def test_display_providers_summary_all_configured(self):
        """Test displaying summary when all providers configured."""
        mock_reporter = Mock(spec=Reporter)

        _display_providers_summary(mock_reporter)

        mock_reporter.success.assert_called_once()
        assert "All 3 providers configured!" in mock_reporter.success.call_args[0][0]

    def test_display_commands_section(self):
        """Test displaying commands section."""
        mock_reporter = Mock(spec=Reporter)

        _display_commands_section(mock_reporter)

        mock_reporter.info.assert_any_call("📋 Available Commands:")
        # Should display all commands
        info_calls = [call[0][0] for call in mock_reporter.info.call_args_list]
        assert any("toolkit social" in call for call in info_calls)
        assert any("toolkit briefing" in call for call in info_calls)

    @patch("agency_toolkit.commands.info.get_available_social_templates")
    def test_display_social_templates_section(self, mock_get_templates):
        """Test displaying social templates section."""
        mock_get_templates.return_value = {
            "modern": "Modern style",
            "bold": "Bold style",
        }
        mock_reporter = Mock(spec=Reporter)

        _display_social_templates_section(mock_reporter)

        mock_reporter.info.assert_any_call("🎨 Social Templates:")
        mock_reporter.info.assert_any_call("  - modern          Modern style")
        mock_reporter.info.assert_any_call("  - bold            Bold style")

    @patch("agency_toolkit.commands.info.get_available_social_templates")
    def test_display_social_templates_section_empty(self, mock_get_templates):
        """Test displaying social templates section when empty."""
        mock_get_templates.return_value = {}
        mock_reporter = Mock(spec=Reporter)

        _display_social_templates_section(mock_reporter)

        mock_reporter.info.assert_any_call("🎨 Social Templates:")
        mock_reporter.info.assert_any_call("  (no templates found)")

    @patch("agency_toolkit.commands.info.get_available_providers")
    def test_display_image_providers_section(self, mock_get_providers):
        """Test displaying image providers section."""
        mock_get_providers.return_value = {
            "pollinations": {"description": "Free AI images", "status": "✅ Default"}
        }
        mock_reporter = Mock(spec=Reporter)

        _display_image_providers_section(mock_reporter)

        mock_reporter.info.assert_any_call("🖼️ Image Providers:")
        mock_reporter.info.assert_any_call(
            "  - pollinations    Free AI images ✅ Default"
        )

    @patch("agency_toolkit.commands.info.get_available_seed_templates")
    def test_display_seed_templates_section(self, mock_get_seeds):
        """Test displaying seed templates section."""
        mock_get_seeds.return_value = {"template1": "Seed template 1"}
        mock_reporter = Mock(spec=Reporter)

        _display_seed_templates_section(mock_reporter)

        mock_reporter.info.assert_any_call("🎭 Seed Templates:")
        mock_reporter.info.assert_any_call("  - template1       Seed template 1")

    def test_display_help_section(self):
        """Test displaying help section."""
        mock_reporter = Mock(spec=Reporter)

        _display_help_section(mock_reporter)

        mock_reporter.info.assert_any_call("💡 Get Started:")
        info_calls = [call[0][0] for call in mock_reporter.info.call_args_list]
        assert any("toolkit social --help" in call for call in info_calls)
        assert any("toolkit ask" in call for call in info_calls)


class TestIntegration:
    """Test integration scenarios."""

    @patch.dict("os.environ", {"MISTRAL_API_KEY": "test_key"})
    def test_providers_status_integration(self):
        """Test complete providers status flow."""
        mock_reporter = Mock(spec=Reporter)

        # Test all display functions work together
        _display_providers_header(mock_reporter)
        _display_providers_table(mock_reporter)
        _display_providers_summary(mock_reporter)

        # Verify all functions were called
        assert mock_reporter.info.call_count > 0
        assert mock_reporter.divider.call_count > 0

    @patch("agency_toolkit.commands.info.get_available_social_templates")
    @patch("agency_toolkit.commands.info.get_available_providers")
    @patch("agency_toolkit.commands.info.get_available_seed_templates")
    def test_info_command_integration(self, mock_seeds, mock_providers, mock_templates):
        """Test complete info command flow."""
        mock_templates.return_value = {"modern": "Modern style"}
        mock_providers.return_value = {
            "pollinations": {"description": "Free AI images", "status": "✅"}
        }
        mock_seeds.return_value = {"template1": "Seed template 1"}

        mock_reporter = Mock(spec=Reporter)

        # Test all sections display
        _display_commands_section(mock_reporter)
        _display_social_templates_section(mock_reporter)
        _display_image_providers_section(mock_reporter)
        _display_seed_templates_section(mock_reporter)
        _display_help_section(mock_reporter)

        # Verify all sections were displayed
        assert mock_reporter.info.call_count >= 10  # At least headers + content
