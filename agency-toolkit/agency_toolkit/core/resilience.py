"""Resilience and error recovery utilities.

This module provides:
- Provider fallback mechanisms for graceful degradation
- Retry logic with exponential backoff
- Rate limiting for API calls
- Offline mode support
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second: float = 1.0):
        """Initialize rate limiter.

        Args:
            calls_per_second: Maximum calls allowed per second
        """
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self) -> None:
        """Wait if necessary to maintain rate limit."""
        now = time.time()
        elapsed = now - self.last_call

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_call = time.time()


# Global rate limiters
_mistral_limiter = RateLimiter(calls_per_second=1.0)


def with_retry(
    max_attempts: int = 3, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator to retry function calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, backoff_factor=2.0)
        def call_api():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            wait_time = 1.0

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        wait_time *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


def rate_limit_mistral() -> None:
    """Apply rate limiting to Mistral API calls."""
    _mistral_limiter.wait()


def with_fallback(
    fallback_value: Any = None,
    fallback_fn: Callable | None = None,
    log_error: bool = True,
) -> Callable:
    """Decorator for graceful degradation with fallback.

    Args:
        fallback_value: Value to return on failure (if fallback_fn not provided)
        fallback_fn: Function to call on failure to generate fallback value
        log_error: Whether to log the error

    Returns:
        Decorated function with fallback logic

    Example:
        @with_fallback(fallback_value="default.png")
        def generate_image(prompt):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"{func.__name__} failed: {e}. Using fallback.")

                if fallback_fn is not None:
                    return fallback_fn(*args, **kwargs)
                else:
                    return fallback_value

        return wrapper

    return decorator


class FontFallbackHandler:
    """Handle font loading with fallback cascade."""

    DEFAULT_FONTS = [
        "Helvetica",
        "Arial",
        "DejaVuSans",
        "FreeSans",
        "Liberation Sans",
    ]

    @classmethod
    def get_font(cls, preferred_font: str | None = None) -> str:
        """Get available font with fallback cascade.

        Args:
            preferred_font: Preferred font name (optional)

        Returns:
            Name of available font
        """
        fonts_to_try = []

        if preferred_font:
            fonts_to_try.append(preferred_font)

        fonts_to_try.extend(cls.DEFAULT_FONTS)

        # Try to load fonts
        for font_name in fonts_to_try:
            if cls._is_font_available(font_name):
                logger.debug(f"Using font: {font_name}")
                return font_name

        # Last resort
        logger.warning("No preferred fonts available, using default")
        return "Helvetica"

    @staticmethod
    def _is_font_available(font_name: str) -> bool:
        """Check if font is available.

        This is a simplified check. In production, you'd actually
        test font loading with PIL or reportlab.
        """
        # For now, assume all fonts in DEFAULT_FONTS are available
        return font_name in FontFallbackHandler.DEFAULT_FONTS


class OfflineMode:
    """Context manager for offline mode operations."""

    _offline = False

    @classmethod
    def is_offline(cls) -> bool:
        """Check if offline mode is enabled."""
        return cls._offline

    @classmethod
    def enable(cls) -> None:
        """Enable offline mode."""
        cls._offline = True
        logger.info("Offline mode enabled - network calls will be blocked")

    @classmethod
    def disable(cls) -> None:
        """Disable offline mode."""
        cls._offline = False
        logger.info("Offline mode disabled")

    @classmethod
    def check_network_allowed(cls) -> None:
        """Raise exception if network calls are not allowed.

        Raises:
            RuntimeError: If offline mode is enabled
        """
        if cls._offline:
            raise RuntimeError(
                "Network operation not allowed in offline mode. "
                "Disable offline mode or use local-only operations."
            )


def require_network(func: Callable) -> Callable:
    """Decorator to mark functions that require network access.

    Raises:
        RuntimeError: If called in offline mode
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        OfflineMode.check_network_allowed()
        return func(*args, **kwargs)

    return wrapper
