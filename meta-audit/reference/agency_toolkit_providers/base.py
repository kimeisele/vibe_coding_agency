"""Abstract base class for image generation providers.

All image providers must implement this interface for plugin architecture.
"""

from abc import ABC, abstractmethod
from typing import Any


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        seed: int | None,
        width: int,
        height: int,
        config: Any,
    ) -> dict[str, Any]:
        """Generate image from prompt.

        Args:
            prompt: Text prompt for image generation
            seed: Random seed for reproducibility (None = random)
            width: Image width in pixels
            height: Image height in pixels
            config: Configuration object (for output_dir, etc.)

        Returns:
            dict: {
                "path": str,          # Full path to saved image
                "cost": float,        # Estimated cost in USD
                "seed": int,          # Seed used (same as input or generated)
                "model": str,         # Model identifier
                "provider": str       # Provider name
            }

        Raises:
            ImageProviderError: If generation fails
        """
        pass

    @abstractmethod
    def estimate_cost(self) -> float:
        """Estimate cost per image in USD.

        Returns:
            float: Cost in USD (0.0 for free providers)
        """
        pass

    @abstractmethod
    def supports_seed(self) -> bool:
        """Check if provider supports deterministic seed.

        Returns:
            bool: True if seed parameter is supported
        """
        pass

    @abstractmethod
    def max_dimensions(self) -> tuple[int, int]:
        """Get maximum supported image dimensions.

        Returns:
            tuple: (max_width, max_height) in pixels
        """
        pass

    def validate_dimensions(self, width: int, height: int) -> None:
        """Validate requested dimensions against provider limits.

        Args:
            width: Requested width
            height: Requested height

        Raises:
            ValueError: If dimensions exceed provider limits
        """
        max_width, max_height = self.max_dimensions()
        if width > max_width or height > max_height:
            raise ValueError(
                f"Dimensions {width}x{height} exceed provider limit "
                f"({max_width}x{max_height})"
            )


class TextProvider(ABC):
    """Abstract base class for text generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate text from prompt.

        Args:
            prompt: Text prompt for generation
            model: Model identifier (provider-specific)
            temperature: Controls randomness of output (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt for the conversation

        Returns:
            dict: {
                "response": str,      # Generated text
                "model": str,         # Model identifier used
                "temperature": float, # Temperature used
                "max_tokens": int,    # Max tokens used
                "timestamp": str,     # ISO format timestamp
                "provider": str       # Provider name
            }

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, max_tokens: int) -> float:
        """Estimate cost for a text generation request.

        Args:
            prompt_tokens: Estimated number of input tokens
            max_tokens: Maximum output tokens

        Returns:
            float: Estimated cost in USD (0.0 for free providers)
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            list: Model identifiers
        """
        pass
