"""Provider registry for dynamic image provider discovery and selection."""

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.providers.base import ImageProvider, TextProvider

# Global registry of available providers
_IMAGE_PROVIDERS: dict[str, type[ImageProvider]] = {}
_TEXT_PROVIDERS: dict[str, type[TextProvider]] = {}


def register_provider(name: str, provider_class: type[ImageProvider]) -> None:
    """Register an image provider.

    Args:
        name: Provider name (e.g., "replicate", "pollinations")
        provider_class: Provider class implementing ImageProvider

    Raises:
        ValueError: If provider name already registered
    """
    if name in _IMAGE_PROVIDERS:
        raise ValueError(f"Provider '{name}' is already registered")

    if not issubclass(provider_class, ImageProvider):
        raise TypeError(
            f"Provider class must implement ImageProvider interface, "
            f"got {provider_class}"
        )

    _IMAGE_PROVIDERS[name] = provider_class


def get_provider(name: str) -> type[ImageProvider]:
    """Get provider class by name.

    Args:
        name: Provider name

    Returns:
        Provider class

    Raises:
        ImageProviderError: If provider not found
    """
    if name not in _IMAGE_PROVIDERS:
        available = ", ".join(_IMAGE_PROVIDERS.keys())
        raise ImageProviderError(
            f"Unknown provider '{name}'. Available: {available or 'none'}"
        )

    return _IMAGE_PROVIDERS[name]


def list_providers() -> list[str]:
    """List all registered provider names.

    Returns:
        List of provider names
    """
    return list(_IMAGE_PROVIDERS.keys())


def unregister_provider(name: str) -> None:
    """Unregister a provider (mainly for testing).

    Args:
        name: Provider name

    Raises:
        KeyError: If provider not found
    """
    del _IMAGE_PROVIDERS[name]


def clear_registry() -> None:
    """Clear all registered providers (for testing)."""
    _IMAGE_PROVIDERS.clear()


# Text provider registry functions
def register_text_provider(name: str, provider_class: type[TextProvider]) -> None:
    """Register a text provider.

    Args:
        name: Provider name (e.g., "mistral", "ollama")
        provider_class: Provider class implementing TextProvider

    Raises:
        ValueError: If provider name already registered
    """
    if name in _TEXT_PROVIDERS:
        raise ValueError(f"Text provider '{name}' is already registered")

    if not issubclass(provider_class, TextProvider):
        raise TypeError(
            f"Provider class must implement TextProvider interface, "
            f"got {provider_class}"
        )

    _TEXT_PROVIDERS[name] = provider_class


def get_text_provider(name: str) -> type[TextProvider]:
    """Get text provider class by name.

    Args:
        name: Provider name

    Returns:
        Provider class

    Raises:
        ValueError: If provider not found
    """
    if name not in _TEXT_PROVIDERS:
        available = ", ".join(_TEXT_PROVIDERS.keys())
        raise ValueError(
            f"Unknown text provider '{name}'. Available: {available or 'none'}"
        )

    return _TEXT_PROVIDERS[name]


def list_text_providers() -> list[str]:
    """List all registered text provider names.

    Returns:
        List of provider names
    """
    return list(_TEXT_PROVIDERS.keys())


def unregister_text_provider(name: str) -> None:
    """Unregister a text provider (mainly for testing).

    Args:
        name: Provider name

    Raises:
        KeyError: If provider not found
    """
    del _TEXT_PROVIDERS[name]


def clear_text_registry() -> None:
    """Clear all registered text providers (for testing)."""
    _TEXT_PROVIDERS.clear()
