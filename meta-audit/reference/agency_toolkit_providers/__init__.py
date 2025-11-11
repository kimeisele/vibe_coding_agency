"""Image and text generation provider plugin system."""

from agency_toolkit.providers.base import ImageProvider, TextProvider
from agency_toolkit.providers.provider_loader import (
    get_provider,
    get_text_provider,
    list_providers,
    list_text_providers,
    register_provider,
    register_text_provider,
)

# Auto-register text providers
try:
    from agency_toolkit.providers.mistral_provider import MistralProvider

    register_text_provider("mistral", MistralProvider)
except ImportError:
    pass  # mistralai package not installed

try:
    from agency_toolkit.providers.ollama_provider import OllamaProvider

    register_text_provider("ollama", OllamaProvider)
except ImportError:
    pass  # requests package should be available, but handle gracefully

try:
    from agency_toolkit.providers.google_provider import GoogleProvider

    register_text_provider("google", GoogleProvider)
except ImportError:
    pass  # google-generativeai package not installed

__all__ = [
    "ImageProvider",
    "TextProvider",
    "register_provider",
    "get_provider",
    "list_providers",
    "register_text_provider",
    "get_text_provider",
    "list_text_providers",
]
