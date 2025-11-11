"""Unit tests for Pollinations.ai provider."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.models import Config
from agency_toolkit.providers.pollinations import PollinationsProvider


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Provide test configuration."""
    return Config(output_dir=tmp_path)


@pytest.fixture
def provider() -> PollinationsProvider:
    """Provide Pollinations provider instance."""
    return PollinationsProvider()


class TestPollinationsProviderInitialization:
    """Test provider initialization."""

    def test_init_with_default_model(self) -> None:
        """Should use default model if not specified."""
        provider = PollinationsProvider()
        assert provider.model == "flux"

    def test_init_with_custom_model(self) -> None:
        """Should use custom model if specified."""
        provider = PollinationsProvider(model="custom-model")
        assert provider.model == "custom-model"


class TestPollinationsProviderGenerate:
    """Test image generation."""

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_succeeds_with_valid_response(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should generate image when API returns success."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        # Generate
        result = provider.generate(
            prompt="A sunset",
            seed=42,
            width=1024,
            height=1024,
            config=config,
        )

        # Verify result
        assert result["provider"] == "pollinations"
        assert result["seed"] == 42
        assert result["cost"] == 0.0
        assert result["model"] == "flux"
        assert result["path"].endswith(".jpg")
        assert Path(result["path"]).exists()

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_includes_seed_in_params(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should include seed in API request if provided."""
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        provider.generate("A test", seed=123, width=512, height=512, config=config)

        # Verify API was called with seed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["seed"] == 123

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_includes_dimensions_in_params(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should include width and height in API request."""
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        provider.generate("A test", seed=42, width=512, height=768, config=config)

        # Verify API was called with dimensions
        call_args = mock_get.call_args
        assert call_args[1]["params"]["width"] == 512
        assert call_args[1]["params"]["height"] == 768

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_raises_on_api_error(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError on API failure."""
        import requests

        mock_get.side_effect = requests.RequestException("Connection failed")

        with pytest.raises(ImageProviderError, match="Pollinations API failed"):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_raises_on_http_error(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError on HTTP error response."""
        import requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(ImageProviderError):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_creates_output_directory(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should create output directory if not exists."""
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        output_dir = config.output_dir / "images"
        assert not output_dir.exists()

        provider.generate("A test", seed=42, width=1024, height=1024, config=config)

        assert output_dir.exists()

    @patch("agency_toolkit.providers.pollinations.requests.get")
    def test_generate_with_none_seed(
        self, mock_get, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should handle None seed (not include in params)."""
        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        result = provider.generate(
            prompt="A test", seed=None, width=1024, height=1024, config=config
        )

        # Should still work, seed will be None in result
        assert "path" in result
        assert result["seed"] is None

    def test_generate_validates_dimensions(
        self, provider: PollinationsProvider, config: Config
    ) -> None:
        """Should validate dimensions before API call."""
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.generate(
                prompt="Too big",
                seed=42,
                width=4096,  # Exceeds max
                height=1024,
                config=config,
            )


class TestPollinationsProviderMethods:
    """Test provider interface methods."""

    def test_estimate_cost_returns_zero(self, provider: PollinationsProvider) -> None:
        """Should return 0.0 cost (FREE)."""
        assert provider.estimate_cost() == 0.0

    def test_supports_seed_returns_true(self, provider: PollinationsProvider) -> None:
        """Should return True (supports seed)."""
        assert provider.supports_seed() is True

    def test_max_dimensions_returns_correct_values(
        self, provider: PollinationsProvider
    ) -> None:
        """Should return max dimensions."""
        max_width, max_height = provider.max_dimensions()
        assert max_width == 2048
        assert max_height == 2048

    def test_validate_dimensions_accepts_valid(
        self, provider: PollinationsProvider
    ) -> None:
        """Should accept dimensions within limits."""
        # Should not raise
        provider.validate_dimensions(512, 512)
        provider.validate_dimensions(2048, 2048)

    def test_validate_dimensions_rejects_invalid(
        self, provider: PollinationsProvider
    ) -> None:
        """Should reject dimensions exceeding limits."""
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(4096, 1024)

        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(1024, 4096)
