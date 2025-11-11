"""Pollinations.ai image generation provider."""

import logging
from urllib.parse import quote

import requests

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.providers.base import ImageProvider

logger = logging.getLogger(__name__)

# Pollinations API constants
API_BASE = "https://image.pollinations.ai"
DEFAULT_MODEL = "flux"
MAX_DIMENSION = 2048


class PollinationsProvider(ImageProvider):
    """Pollinations.ai FREE image generation provider.

    No authentication required. Direct image download.
    """

    def __init__(self, model: str | None = None):
        """Initialize Pollinations provider.

        Args:
            model: Model name (default: "flux")
        """
        self.model = model or DEFAULT_MODEL

    def generate(self, prompt, seed, width, height, config):
        """Generate image via Pollinations.ai API.

        Args:
            prompt: Image generation prompt
            seed: Random seed for reproducibility
            width: Image width in pixels
            height: Image height in pixels
            config: Config object (for output_dir)

        Returns:
            dict with path, cost, seed, model, provider

        Raises:
            ImageProviderError: If API call fails
        """
        # Validate dimensions
        self.validate_dimensions(width, height)

        # URL-encode prompt
        encoded_prompt = quote(prompt)

        # Build URL
        url = f"{API_BASE}/prompt/{encoded_prompt}"
        params = {
            "width": width,
            "height": height,
            "model": self.model,
        }
        if seed is not None:
            params["seed"] = seed

        try:
            # Make request
            logger.debug(f"Calling Pollinations API with prompt: {prompt}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Determine output directory
            output_dir = config.output_dir / "images"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save image
            image_filename = f"image_{seed}.jpg"
            image_path = output_dir / image_filename
            image_path.write_bytes(response.content)

            logger.info(f"Image saved: {image_path}")

            return {
                "path": str(image_path),
                "cost": 0.0,  # FREE!
                "seed": seed,
                "model": self.model,
                "provider": "pollinations",
            }

        except requests.RequestException as e:
            raise ImageProviderError(f"Pollinations API failed: {str(e)}") from e

    def estimate_cost(self):
        """Estimate cost per image.

        Returns:
            float: 0.0 (FREE!)
        """
        return 0.0

    def supports_seed(self):
        """Check if provider supports deterministic seed.

        Returns:
            bool: True (Pollinations supports seed)
        """
        return True

    def max_dimensions(self):
        """Get maximum supported dimensions.

        Returns:
            tuple: (max_width, max_height) - 2048x2048 estimated
        """
        return (MAX_DIMENSION, MAX_DIMENSION)
