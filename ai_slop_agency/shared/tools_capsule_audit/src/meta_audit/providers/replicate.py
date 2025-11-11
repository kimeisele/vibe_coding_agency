"""Replicate image generation provider."""

import logging
import os

import replicate
import requests

from agency_toolkit.exceptions import ImageProviderError
from agency_toolkit.providers.base import ImageProvider

logger = logging.getLogger(__name__)

# Cost estimates (USD per image)
MODEL_COSTS = {
    "stability-ai/sdxl": 0.003,
    "stability-ai/sdxl:7762fd07cf82c948538e41f63f32eda9fe3ce3f3f7e09cbb364b19d94585d809": 0.003,
    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf": 0.003,
}


class ReplicateProvider(ImageProvider):
    """Replicate API image generation provider.

    Requires REPLICATE_API_TOKEN environment variable.
    """

    def __init__(self, model: str | None = None):
        """Initialize Replicate provider.

        Args:
            model: Replicate model identifier (e.g., "stability-ai/sdxl")
                   If None, uses default from config
        """
        self.model = model
        self._cost_estimate = 0.003  # Default cost

    def generate(self, prompt, seed, width, height, config):
        """Generate image via Replicate API.

        Args:
            prompt: Image generation prompt
            seed: Random seed for reproducibility
            width: Image width in pixels
            height: Image height in pixels
            config: Config object (for output_dir, model)

        Returns:
            dict with path, cost, seed, model, provider

        Raises:
            ImageProviderError: If API token missing or API call fails
        """
        # Validate dimensions
        self.validate_dimensions(width, height)

        # Get API token
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        if not api_token:
            error_msg = """
REPLICATE_API_TOKEN not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export REPLICATE_API_TOKEN='your-token-here'

  # Or add to your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export REPLICATE_API_TOKEN="your-token"' >> ~/.zshrc
  source ~/.zshrc

Get your token at: https://replicate.com/account
            """.strip()
            raise ImageProviderError(error_msg)

        # Get model from config if not set
        model = self.model or config.image.replicate_model
        self._cost_estimate = MODEL_COSTS.get(model, 0.003)

        try:
            # Create Replicate client
            client = replicate.Client(api_token=api_token)

            # Call API
            logger.debug(f"Calling Replicate API with prompt: {prompt}")
            output = client.run(
                model,
                input={
                    "prompt": prompt,
                    "seed": seed,
                    "width": width,
                    "height": height,
                },
            )

            if not output:
                raise ImageProviderError("Replicate API returned empty output")

            # Get first image URL (output is a list)
            image_url = output[0] if isinstance(output, list) else output
            logger.debug(f"Generated image URL: {image_url}")

            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Determine output directory
            output_dir = config.output_dir / "images"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save image
            image_filename = f"image_{seed}.png"
            image_path = output_dir / image_filename
            image_path.write_bytes(response.content)

            logger.info(f"Image saved: {image_path}")

            return {
                "path": str(image_path),
                "cost": self._cost_estimate,
                "seed": seed,
                "model": model,
                "provider": "replicate",
            }

        except requests.RequestException as e:
            raise ImageProviderError(f"Failed to download image: {str(e)}") from e
        except Exception as e:
            raise ImageProviderError(f"Replicate API failed: {str(e)}") from e

    def estimate_cost(self):
        """Estimate cost per image.

        Returns:
            float: Cost in USD (default ~$0.003)
        """
        return self._cost_estimate

    def supports_seed(self):
        """Check if provider supports deterministic seed.

        Returns:
            bool: True (Replicate supports seed)
        """
        return True

    def max_dimensions(self):
        """Get maximum supported dimensions.

        Returns:
            tuple: (max_width, max_height) - 2048x2048 for SDXL
        """
        return (2048, 2048)
