import pytest
from typer.testing import CliRunner

from agency_toolkit.cli_app import app

runner = CliRunner()


@pytest.mark.integration
def test_image_command_with_real_config() -> None:
    """Test image command loads correct config with .image attribute."""
    from unittest.mock import patch

    with patch("agency_toolkit.image_gen.generate_image") as mock_generate_image:
        # Configure the mock to return a specific value
        mock_generate_image.return_value = {
            "path": "https://example.com/generated_image.png",
            "cost": 0.003,
            "seed": 12345,
            "model": "test-model",
            "provider": "replicate",
        }
        # Invoke the CLI command
        result = runner.invoke(app, ["image", "generate", "a test prompt"])

        # Assert the command exited successfully
        assert result.exit_code == 0

        # Assert that the mocked function was called with the correct arguments
        mock_generate_image.assert_called_once()

        # Assert that the output contains the expected URL
        assert "https://example.com/generated_image.png" in result.stdout
