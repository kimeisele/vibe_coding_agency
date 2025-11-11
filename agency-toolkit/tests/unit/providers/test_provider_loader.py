"""Unit tests for provider registry."""

import pytest

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.providers import (
    ImageProvider,
    get_provider,
    list_providers,
    register_provider,
)
from agency_toolkit.providers.provider_loader import clear_registry, unregister_provider


class MockProvider(ImageProvider):
    """Mock provider for testing."""

    def generate(self, prompt, seed, width, height, config):
        return {
            "path": "/fake/path.png",
            "cost": 0.0,
            "seed": seed,
            "model": "mock",
            "provider": "mock",
        }

    def estimate_cost(self):
        return 0.0

    def supports_seed(self):
        return True

    def max_dimensions(self):
        return (1024, 1024)


@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before each test."""
    clear_registry()
    yield
    clear_registry()


def test_register_provider_adds_to_registry():
    """Test that registering a provider makes it available."""
    register_provider("mock", MockProvider)

    assert "mock" in list_providers()
    assert get_provider("mock") == MockProvider


def test_register_duplicate_provider_raises_error():
    """Test that registering duplicate provider name raises error."""
    register_provider("mock", MockProvider)

    with pytest.raises(ValueError, match="already registered"):
        register_provider("mock", MockProvider)


def test_get_unknown_provider_raises_error():
    """Test that getting unknown provider raises ImageProviderError."""
    with pytest.raises(ImageProviderError, match="Unknown provider"):
        get_provider("nonexistent")


def test_get_provider_error_message_shows_available():
    """Test that error message lists available providers."""
    register_provider("test1", MockProvider)
    register_provider("test2", MockProvider)

    with pytest.raises(ImageProviderError, match="test1.*test2"):
        get_provider("invalid")


def test_list_providers_returns_all_registered():
    """Test that list_providers returns all registered names."""
    register_provider("provider1", MockProvider)
    register_provider("provider2", MockProvider)

    providers = list_providers()
    assert len(providers) == 2
    assert "provider1" in providers
    assert "provider2" in providers


def test_unregister_provider_removes_from_registry():
    """Test that unregistering removes provider."""
    register_provider("mock", MockProvider)
    assert "mock" in list_providers()

    unregister_provider("mock")
    assert "mock" not in list_providers()


def test_register_non_provider_class_raises_error():
    """Test that registering non-ImageProvider class raises TypeError."""

    class NotAProvider:
        pass

    with pytest.raises(TypeError, match="must implement ImageProvider"):
        register_provider("invalid", NotAProvider)


def test_provider_base_class_validate_dimensions():
    """Test ImageProvider.validate_dimensions() helper."""
    provider = MockProvider()

    # Should not raise
    provider.validate_dimensions(512, 512)
    provider.validate_dimensions(1024, 1024)

    # Should raise
    with pytest.raises(ValueError, match="exceed provider limit"):
        provider.validate_dimensions(2048, 2048)
