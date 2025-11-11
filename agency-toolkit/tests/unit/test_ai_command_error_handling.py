"""Unit tests for AI command error handling (Epic 1.3.2)."""

from unittest.mock import MagicMock, patch

import httpx
from typer.testing import CliRunner

from agency_toolkit.cli_app import app
from agency_toolkit.exceptions import AIProviderError, ValidationError

runner = CliRunner()


class TestAICommandErrorHandling:
    """Test error handling in the ai command."""

    def test_ai_command_handles_validation_error(self):
        """Test that ValidationError is caught and displayed properly."""
        with patch("agency_toolkit.commands.ai._load_prompt") as mock_load_prompt:
            mock_load_prompt.side_effect = ValidationError("Invalid prompt format")

            result = runner.invoke(app, ["ai", "--prompt", "test"])

            assert result.exit_code == 1
            assert "Validation Error" in result.stdout

    def test_ai_command_handles_file_not_found_error(self):
        """Test that FileNotFoundError is caught and displayed properly."""
        result = runner.invoke(app, ["ai", "--prompt-file", "/nonexistent/file.txt"])

        assert result.exit_code == 1
        assert "File not found" in result.stdout

    def test_ai_command_handles_ai_provider_error(self):
        """Test that AIProviderError is caught with helpful message."""
        with patch("agency_toolkit.commands.ai.get_text_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Simulate provider error
            mock_provider_instance.get_available_models.return_value = ["model1"]
            mock_provider_instance.generate.side_effect = AIProviderError(
                "API key invalid"
            )

            result = runner.invoke(app, ["ai", "--prompt", "test"])

            assert result.exit_code == 1
            assert "AI Provider Error" in result.stdout
            assert (
                "API credentials" in result.stdout
                or "network connection" in result.stdout
            )

    def test_ai_command_handles_http_error(self):
        """Test that HTTP errors are caught with network hint."""
        with patch("agency_toolkit.commands.ai.get_text_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Simulate HTTP error
            mock_provider_instance.get_available_models.return_value = ["model1"]
            mock_provider_instance.generate.side_effect = httpx.HTTPError(
                "Connection timeout"
            )

            result = runner.invoke(app, ["ai", "--prompt", "test"])

            assert result.exit_code == 1
            assert "Network Error" in result.stdout
            assert "internet connection" in result.stdout

    def test_ai_command_handles_unexpected_error(self):
        """Test that unexpected errors show debug hint."""
        with patch("agency_toolkit.commands.ai.get_text_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Simulate unexpected error
            mock_provider_instance.get_available_models.return_value = ["model1"]
            mock_provider_instance.generate.side_effect = RuntimeError(
                "Unexpected issue"
            )

            result = runner.invoke(app, ["ai", "--prompt", "test"])

            assert result.exit_code == 1
            assert "Unexpected Error" in result.stdout
            assert "--debug" in result.stdout

    def test_ai_command_json_output_on_error(self):
        """Test that JSON output is provided on error when --json flag is used."""
        with patch("agency_toolkit.commands.ai._load_prompt") as mock_load_prompt:
            mock_load_prompt.side_effect = ValidationError("Invalid format")

            result = runner.invoke(app, ["--json", "ai", "--prompt", "test"])

            assert result.exit_code == 1
            # Should have JSON output with status: error
            assert (
                '"status": "error"' in result.stdout
                or '"status":"error"' in result.stdout
            )
            assert '"message"' in result.stdout

    def test_ai_command_successful_generation(self):
        """Test successful AI generation with proper output."""
        with patch("agency_toolkit.commands.ai.get_text_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Simulate successful response
            mock_provider_instance.get_available_models.return_value = ["model1"]
            mock_provider_instance.generate.return_value = {
                "response": "Test AI response",
                "model": "model1",
                "provider": "test",
            }

            result = runner.invoke(app, ["ai", "--prompt", "test query"])

            assert result.exit_code == 0
            assert "Test AI response" in result.stdout
