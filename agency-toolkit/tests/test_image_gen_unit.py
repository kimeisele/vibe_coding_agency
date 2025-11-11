"""Tests for image generation module.

Note: These are limited unit tests for the seed generation function.
Most image generation testing should be done via CLI integration tests
to verify actual provider functionality.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from agency_toolkit import image_gen
from agency_toolkit.exceptions import ImageProviderError


class TestGenerateSeed:
    """Test deterministic seed generation.

    This is one of the few internal functions worth unit testing
    since it's used by multiple providers.
    """

    def test_generate_seed_is_deterministic(self) -> None:
        """Same prompt should produce same seed."""
        prompt = "modern office"
        seed1 = image_gen._generate_seed(prompt)
        seed2 = image_gen._generate_seed(prompt)
        assert seed1 == seed2
        assert isinstance(seed1, int)
        assert 0 <= seed1 <= 2147483647

    def test_generate_seed_different_prompts_different_seeds(self) -> None:
        """Different prompts should produce different seeds."""
        seed1 = image_gen._generate_seed("office")
        seed2 = image_gen._generate_seed("beach")
        assert seed1 != seed2

    def test_generate_seed_handles_unicode(self) -> None:
        """Should handle Unicode characters in prompts."""
        seed1 = image_gen._generate_seed("café ☕")
        seed2 = image_gen._generate_seed("café ☕")
        assert seed1 == seed2
        assert isinstance(seed1, int)

    def test_generate_seed_long_prompt(self) -> None:
        """Should handle very long prompts."""
        long_prompt = "a" * 1000
        seed = image_gen._generate_seed(long_prompt)
        assert isinstance(seed, int)
        assert 0 <= seed <= 2147483647


class TestGenerateImageErrorHandling:
    """Test error handling in generate_image function (Epic 1.3.1)."""

    def test_generate_image_raises_value_error_when_config_is_none(self) -> None:
        """Test that generate_image raises ValueError when config is None."""
        with pytest.raises(ValueError, match="config parameter is required"):
            image_gen.generate_image(prompt="test", config=None)

    @patch("agency_toolkit.image_gen.get_provider")
    def test_generate_image_handles_http_error(self, mock_get_provider) -> None:
        """Test that HTTP errors are caught and wrapped in ImageProviderError."""
        mock_provider_class = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        # Simulate HTTP error
        http_error = httpx.HTTPError("Connection failed")
        mock_provider_instance.generate.side_effect = http_error

        mock_config = MagicMock()

        with pytest.raises(
            ImageProviderError, match="Network error during image generation"
        ):
            image_gen.generate_image(
                prompt="test prompt", config=mock_config, provider="test"
            )

    @patch("agency_toolkit.image_gen.get_provider")
    def test_generate_image_reraises_provider_error(self, mock_get_provider) -> None:
        """Test that ImageProviderError is re-raised directly."""
        mock_provider_class = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        # Simulate provider error
        provider_error = ImageProviderError("Provider failed")
        mock_provider_instance.generate.side_effect = provider_error

        mock_config = MagicMock()

        with pytest.raises(ImageProviderError, match="Provider failed"):
            image_gen.generate_image(
                prompt="test prompt", config=mock_config, provider="test"
            )

    @patch("agency_toolkit.image_gen.get_provider")
    def test_generate_image_wraps_unexpected_errors(self, mock_get_provider) -> None:
        """Test that unexpected errors are wrapped in ImageProviderError."""
        mock_provider_class = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        # Simulate unexpected error
        mock_provider_instance.generate.side_effect = RuntimeError("Unexpected issue")

        mock_config = MagicMock()

        with pytest.raises(
            ImageProviderError, match="Unexpected error during image generation"
        ):
            image_gen.generate_image(
                prompt="test prompt", config=mock_config, provider="test"
            )

    @patch("agency_toolkit.image_gen.get_provider")
    def test_generate_image_successful_generation(self, mock_get_provider) -> None:
        """Test successful image generation returns expected result."""
        mock_provider_class = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        expected_result = {
            "path": "/tmp/image.png",
            "cost": 0.002,
            "seed": 12345,
            "model": "flux-schnell",
            "provider": "replicate",
        }
        mock_provider_instance.generate.return_value = expected_result

        mock_config = MagicMock()

        result = image_gen.generate_image(
            prompt="test prompt", config=mock_config, provider="replicate"
        )

        assert result == expected_result
        mock_provider_instance.generate.assert_called_once()
