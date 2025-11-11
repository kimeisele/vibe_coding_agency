"""Validation functions for social media post generation."""

import logging

from agency_toolkit.config import COLORS, FORMATS
from agency_toolkit.core.social.constants import HEX_COLOR_LENGTH, TWITTER_MAX_CHARS
from agency_toolkit.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


def validate_text(text: str) -> str:
    """Validate post text content.

    Automatically truncates text that exceeds the maximum character limit.

    Args:
        text: Post text content

    Returns:
        Stripped and potentially truncated text

    Raises:
        ConfigurationError: If text is empty
    """
    if not text.strip():
        raise ConfigurationError("Text cannot be empty")

    stripped_text = text.strip()

    if len(stripped_text) > TWITTER_MAX_CHARS:
        # Log error and truncate
        logger.error(
            f"Text is {len(stripped_text)} chars (max {TWITTER_MAX_CHARS}). "
            f"Truncating to fit platform limits."
        )
        # Truncate to max length and add ellipsis
        truncated = stripped_text[: TWITTER_MAX_CHARS - 3] + "..."
        logger.warning(
            f"Original: {len(stripped_text)} chars → Truncated: {len(truncated)} chars"
        )
        return truncated

    return stripped_text


def validate_color(color: str) -> str:
    """Validate and resolve color value.

    Args:
        color: Color name or hex value

    Returns:
        Hex color string

    Raises:
        ConfigurationError: If color is invalid
    """
    if color.startswith("#"):
        if len(color) != HEX_COLOR_LENGTH or not all(
            c in "0123456789ABCDEFabcdef" for c in color[1:]
        ):
            raise ConfigurationError(f"Invalid hex color: {color}")
        return color
    elif color in COLORS:
        return COLORS[color]
    else:
        raise ConfigurationError(f"Unknown color: {color}")


def validate_format(format_name: str) -> tuple[int, int]:
    """Validate format and return dimensions.

    Args:
        format_name: Image format name (square, story, landscape)

    Returns:
        Tuple of (width, height)

    Raises:
        ConfigurationError: If format is unknown
    """
    if format_name not in FORMATS:
        raise ConfigurationError(f"Unknown format: {format_name}")
    return FORMATS[format_name]
