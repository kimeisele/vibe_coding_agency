"""Unit tests for info command CLI (WU-7.7)."""

from unittest.mock import patch

from typer.testing import CliRunner

from agency_toolkit.cli_app import app

runner = CliRunner()


class TestInfoCommandCLI:
    """Tests for the info command CLI."""

    def test_info_command_exists(self):
        """Verify info command is registered."""
        result = runner.invoke(app, ["info", "info", "--help"])
        assert result.exit_code == 0
        assert "Display toolkit capabilities" in result.stdout

    def test_info_command_displays_commands(self):
        """Verify info command displays available commands."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        assert "Available Commands" in result.stdout or "Commands" in result.stdout
        assert "toolkit social" in result.stdout
        assert "toolkit briefing" in result.stdout

    def test_info_command_displays_templates(self):
        """Verify info command displays social templates."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        assert "Social Templates" in result.stdout or "Templates" in result.stdout

    def test_info_command_displays_providers(self):
        """Verify info command displays image providers."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        assert "Image Providers" in result.stdout or "Providers" in result.stdout
        assert "pollinations" in result.stdout

    def test_info_command_displays_seeds(self):
        """Verify info command displays seed templates."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        assert "Seed Templates" in result.stdout or "moody" in result.stdout

    def test_info_command_displays_help_section(self):
        """Verify info command displays help/getting started section."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        assert "Get Started" in result.stdout or "Help" in result.stdout


class TestAskCommandCLI:
    """Tests for the ask command CLI."""

    def test_ask_command_exists(self):
        """Verify ask command is registered."""
        result = runner.invoke(app, ["info", "ask", "--help"])
        assert result.exit_code == 0
        assert "Ask Mistral" in result.stdout or "Ask" in result.stdout

    def test_ask_command_requires_query(self):
        """Verify ask command requires a query argument."""
        result = runner.invoke(app, ["info", "ask"])

        # Should fail without query
        assert result.exit_code != 0

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_command_with_valid_query(self, mock_generate):
        """Verify ask command works with valid query."""
        mock_generate.return_value = {"response": "Test answer about toolkit"}

        result = runner.invoke(app, ["info", "ask", "How do I create a social post?"])

        assert result.exit_code == 0
        assert "Answer:" in result.stdout or "Test answer" in result.stdout

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_command_calls_mistral_with_docs(self, mock_generate):
        """Verify ask command passes documentation to Mistral."""
        mock_generate.return_value = {"response": "Test answer"}

        runner.invoke(app, ["info", "ask", "What features exist?"])

        # Verify Mistral was called
        assert mock_generate.called

        # Get the prompt that was passed
        call_args = mock_generate.call_args
        prompt = call_args.kwargs.get("prompt") or call_args[1].get("prompt")

        # Should contain the user question
        assert "What features exist?" in prompt

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_command_handles_mistral_error(self, mock_generate):
        """Verify ask command handles Mistral errors gracefully."""
        mock_generate.side_effect = Exception("Mistral API error")

        result = runner.invoke(app, ["info", "ask", "How do I use templates?"])

        assert result.exit_code != 0
        assert "Failed" in result.stdout or "error" in result.stdout.lower()

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_command_handles_empty_response(self, mock_generate):
        """Verify ask command handles empty responses from Mistral."""
        mock_generate.return_value = {"response": ""}

        result = runner.invoke(app, ["info", "ask", "Test question?"])

        assert result.exit_code != 0

    def test_ask_command_examples_in_help(self):
        """Verify ask command help shows usage examples."""
        result = runner.invoke(app, ["info", "ask", "--help"])

        assert result.exit_code == 0
        # Should have examples
        assert "How do I" in result.stdout or "example" in result.stdout.lower()


class TestInfoCommandOutput:
    """Tests for info command output format."""

    def test_info_output_is_formatted(self):
        """Verify info output is nicely formatted."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0

        # Should have visual formatting elements
        output = result.stdout
        assert "=" in output or "📋" in output or "🎨" in output

    def test_info_output_is_readable(self):
        """Verify info output is human-readable."""
        result = runner.invoke(app, ["info", "info"])

        assert result.exit_code == 0
        output = result.stdout

        # Should be reasonably long (not truncated)
        assert len(output) > 200

        # Should have clear sections
        lines = output.split("\n")
        assert len(lines) > 5


class TestDocsCachingBehavior:
    """Tests for documentation caching in info commands."""

    @patch("agency_toolkit.commands.info.load_toolkit_docs")
    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_docs_are_loaded_once_per_query(self, mock_generate, mock_load_docs):
        """Verify docs are loaded once per ask command."""
        mock_load_docs.return_value = "Documentation content"
        mock_generate.return_value = {"response": "Answer"}

        runner.invoke(app, ["info", "ask", "Question 1?"])

        # Should have loaded docs once
        assert mock_load_docs.call_count == 1

    @patch("agency_toolkit.commands.info.load_toolkit_docs")
    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_separate_queries_load_docs_independently(
        self, mock_generate, mock_load_docs
    ):
        """Verify each query loads docs independently (may use cache)."""
        mock_load_docs.return_value = "Documentation content"
        mock_generate.return_value = {"response": "Answer"}

        # Two separate queries
        runner.invoke(app, ["info", "ask", "Question 1?"])
        runner.invoke(app, ["info", "ask", "Question 2?"])

        # Should have attempted to load docs twice
        # (actual caching is handled by load_toolkit_docs internally)
        assert mock_load_docs.call_count >= 2


class TestAskCommandIntegration:
    """Integration tests for ask command with real-ish data."""

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_about_social_posts(self, mock_generate):
        """Verify ask command can answer social post questions."""
        mock_generate.return_value = {
            "response": "You can generate social posts with: toolkit social 'your text' --style bold"
        }

        result = runner.invoke(app, ["info", "ask", "How do I create a social post?"])

        assert result.exit_code == 0
        assert "social" in result.stdout.lower()

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_about_templates(self, mock_generate):
        """Verify ask command can answer template questions."""
        mock_generate.return_value = {
            "response": "Available templates: modern, bold, minimal"
        }

        result = runner.invoke(app, ["info", "ask", "What templates are available?"])

        assert result.exit_code == 0
        assert "template" in result.stdout.lower()

    @patch("agency_toolkit.providers.mistral_provider.MistralProvider.generate")
    def test_ask_about_features(self, mock_generate):
        """Verify ask command can answer feature questions."""
        mock_generate.return_value = {
            "response": "The toolkit features include image generation, social posts, and briefings"
        }

        result = runner.invoke(
            app, ["info", "ask", "What features does the toolkit have?"]
        )

        assert result.exit_code == 0
        assert (
            "feature" in result.stdout.lower()
            or "image generation" in result.stdout.lower()
        )
