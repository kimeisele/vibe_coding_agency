"""AI image generation module using Replicate API.

This module provides a provider-agnostic interface for generating images from
text prompts. Supports multiple providers via plugin architecture.
"""

import hashlib
import logging

import httpx

from agency_toolkit.core.resilience import require_network, with_retry
from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.providers import get_provider, register_provider
from agency_toolkit.providers.pollinations import PollinationsProvider
from agency_toolkit.providers.replicate import ReplicateProvider

logger = logging.getLogger(__name__)

# Register built-in providers
register_provider("replicate", ReplicateProvider)
register_provider("pollinations", PollinationsProvider)


def _generate_seed(prompt: str) -> int:
    """Generate deterministic seed from prompt hash.

    Same prompt always produces the same seed, enabling reproducible image generation.

    Args:
        prompt: Image generation prompt

    Returns:
        Integer seed (0-2147483647)
    """
    hash_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return int(hash_digest[:8], 16) % 2147483647


@with_retry(max_attempts=3, backoff_factor=2.0)
@require_network
def generate_image(
    prompt: str,
    seed: int | None = None,
    width: int = 1024,
    height: int = 1024,
    provider: str = "replicate",
    config=None,
) -> dict:
    """Generate image using specified provider.

    Args:
        prompt: Image generation prompt
        seed: Random seed (None = auto-generate from prompt hash)
        width: Image width in pixels (default: 1024)
        height: Image height in pixels (default: 1024)
        provider: Provider name (default: "replicate")
        config: Config object (required)

    Returns:
        dict: {
            "path": str,       # Full path to saved image
            "cost": float,     # USD estimate
            "seed": int,       # Seed used (auto-generated if None)
            "model": str,      # Model identifier
            "provider": str    # Provider name
        }

    Raises:
        ValueError: If config is None or invalid dimensions
        ImageProviderError: If provider unknown or generation fails
        httpx.HTTPError: If network request fails
    """
    if config is None:
        raise ValueError("config parameter is required")

    if seed is None:
        seed = _generate_seed(prompt)

    try:
        # Get provider class and instantiate
        provider_class = get_provider(provider)
        provider_instance = provider_class()

        # Generate image
        result = provider_instance.generate(prompt, seed, width, height, config)
        logger.info(f"Image generated: {result['path']} (cost: ${result['cost']:.4f})")

        return result

    except httpx.HTTPError as e:
        error_msg = f"Network error during image generation: {e}"
        logger.error(error_msg, exc_info=True)
        raise ImageProviderError(error_msg) from e

    except ImageProviderError:
        # Re-raise provider errors directly
        raise

    except Exception as e:
        error_msg = f"Unexpected error during image generation with {provider}: {e}"
        logger.error(error_msg, exc_info=True)
        raise ImageProviderError(error_msg) from e
