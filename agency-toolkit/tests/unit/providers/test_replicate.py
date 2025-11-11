"""Unit tests for Replicate provider."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.models import Config
from agency_toolkit.providers.replicate import ReplicateProvider


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Provide test configuration."""
    return Config(output_dir=tmp_path)


@pytest.fixture
def provider() -> ReplicateProvider:
    """Provide Replicate provider instance."""
    return ReplicateProvider()


class TestReplicateProviderInitialization:
    """Test provider initialization."""

    def test_init_without_model(self) -> None:
        """Should allow None model (uses config default)."""
        provider = ReplicateProvider()
        assert provider.model is None

    def test_init_with_custom_model(self) -> None:
        """Should store custom model if specified."""
        provider = ReplicateProvider(model="stability-ai/sdxl")
        assert provider.model == "stability-ai/sdxl"

    def test_init_default_cost_estimate(self) -> None:
        """Should initialize with default cost estimate."""
        provider = ReplicateProvider()
        assert provider.estimate_cost() == 0.003


class TestReplicateProviderGenerate:
    """Test image generation."""

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_generate_succeeds_with_valid_response(
        self, mock_get, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should generate image when API returns success."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

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
        assert result["provider"] == "replicate"
        assert result["seed"] == 42
        assert result["cost"] == 0.003
        assert result["path"].endswith(".png")
        assert Path(result["path"]).exists()

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_raises_if_no_api_token(
        self, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError if REPLICATE_API_TOKEN not set."""
        with pytest.raises(ImageProviderError, match="REPLICATE_API_TOKEN"):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    def test_generate_raises_if_api_returns_empty(
        self, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError if API returns empty output."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = []

        with pytest.raises(ImageProviderError, match="empty output"):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_generate_passes_parameters_to_api(
        self, mock_get, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should pass parameters to Replicate API correctly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        provider.generate(
            prompt="A test",
            seed=123,
            width=512,
            height=768,
            config=config,
        )

        # Verify API was called with correct parameters
        call_args = mock_client.run.call_args
        input_params = call_args[1]["input"]
        assert input_params["prompt"] == "A test"
        assert input_params["seed"] == 123
        assert input_params["width"] == 512
        assert input_params["height"] == 768

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_generate_handles_download_failure(
        self, mock_get, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError on image download failure."""
        import requests

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

        mock_get.side_effect = requests.RequestException("Connection timeout")

        with pytest.raises(ImageProviderError, match="Failed to download"):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    def test_generate_raises_on_api_exception(
        self, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should raise ImageProviderError on API exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.side_effect = Exception("API error")

        with pytest.raises(ImageProviderError, match="Replicate API failed"):
            provider.generate("A test", seed=42, width=1024, height=1024, config=config)

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_generate_uses_config_model_if_not_set(
        self, mock_get, mock_client_class, config: Config
    ) -> None:
        """Should use model from config if not set in provider."""
        provider = ReplicateProvider()  # No model specified

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        provider.generate("A test", seed=42, width=1024, height=1024, config=config)

        # Verify API was called with config model
        call_args = mock_client.run.call_args
        model_arg = call_args[0][0]
        assert model_arg == config.image.replicate_model

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_generate_creates_output_directory(
        self, mock_get, mock_client_class, provider: ReplicateProvider, config: Config
    ) -> None:
        """Should create output directory if not exists."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        output_dir = config.output_dir / "images"
        assert not output_dir.exists()

        provider.generate("A test", seed=42, width=1024, height=1024, config=config)

        assert output_dir.exists()

    def test_generate_validates_dimensions(
        self, provider: ReplicateProvider, config: Config
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


class TestReplicateProviderMethods:
    """Test provider interface methods."""

    def test_estimate_cost_default(self) -> None:
        """Should return default cost estimate."""
        provider = ReplicateProvider()
        assert provider.estimate_cost() == 0.003

    def test_estimate_cost_for_known_model(self) -> None:
        """Should return cost for known model."""
        provider = ReplicateProvider(model="stability-ai/sdxl")
        # Note: Cost is updated during generate(), not at init
        assert provider.estimate_cost() == 0.003

    @patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_token"})
    @patch("agency_toolkit.providers.replicate.replicate.Client")
    @patch("agency_toolkit.providers.replicate.requests.get")
    def test_estimate_cost_updated_after_generate(
        self, mock_get, mock_client_class, config: Config
    ) -> None:
        """Should update cost estimate after generate."""
        provider = ReplicateProvider(model="stability-ai/sdxl")

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run.return_value = ["https://example.com/image.png"]

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        # Cost should be updated during generate
        provider.generate("A test", seed=42, width=1024, height=1024, config=config)
        assert provider.estimate_cost() == 0.003

    def test_supports_seed_returns_true(self) -> None:
        """Should return True (supports seed)."""
        provider = ReplicateProvider()
        assert provider.supports_seed() is True

    def test_max_dimensions_returns_correct_values(self) -> None:
        """Should return max dimensions."""
        provider = ReplicateProvider()
        max_width, max_height = provider.max_dimensions()
        assert max_width == 2048
        assert max_height == 2048

    def test_validate_dimensions_accepts_valid(self) -> None:
        """Should accept dimensions within limits."""
        provider = ReplicateProvider()
        # Should not raise
        provider.validate_dimensions(512, 512)
        provider.validate_dimensions(2048, 2048)

    def test_validate_dimensions_rejects_invalid(self) -> None:
        """Should reject dimensions exceeding limits."""
        provider = ReplicateProvider()
        with pytest.raises(ValueError, match="exceed provider limit"):
            provider.validate_dimensions(4096, 1024)
