"""Unit tests for the social media module's utility functions."""

import pytest

from agency_toolkit.core.social.layout import hex_to_rgb
from agency_toolkit.core.social.rendering import wrap_text
from agency_toolkit.core.social.validators import validate_color

# Constants for test cases
VALID_NAMED_COLORS = [
    ("blue", "#2E5EAA"),
    ("red", "#D32F2F"),
    ("green", "#43A047"),
    ("purple", "#8E24AA"),
]

VALID_HEX_COLORS = ["#FFFFFF", "#000000", "#1A2B3C"]

INVALID_COLORS = ["invalid_color", "turquoise", "#123", "FF0000"]

HEX_TO_RGB_CASES = [
    ("#FFFFFF", (255, 255, 255)),
    ("#000000", (0, 0, 0)),
    ("#FF0000", (255, 0, 0)),
    ("#00FF00", (0, 255, 0)),
    ("#0000FF", (0, 0, 255)),
]

TEXT_WRAPPING_CASES = [
    ("Short text", 20, "Short text"),
    (
        "This is a longer line of text that needs to be wrapped.",
        20,
        "This is a longer\nline of text that\nneeds to be wrapped.",
    ),
    ("NoWrap", 100, "NoWrap"),
    ("Exact twenty characters", 20, "Exact twenty\ncharacters"),
]


@pytest.mark.parametrize("color_name, expected_hex", VALID_NAMED_COLORS)
def test_validate_color_with_valid_named_color_returns_hex(
    color_name, expected_hex
) -> None:
    """
    Arrange: Get a valid named color and its expected hex value.
    Act: Call validate_color with the named color.
    Assert: The returned value is the correct hex string.
    """
    assert validate_color(color_name) == expected_hex


@pytest.mark.parametrize("hex_value", VALID_HEX_COLORS)
def test_validate_color_with_valid_hex_color_returns_self(hex_value) -> None:
    """
    Arrange: Get a valid hex color string.
    Act: Call validate_color with the hex string.
    Assert: The returned value is the same hex string.
    """
    assert validate_color(hex_value) == hex_value


@pytest.mark.parametrize("invalid_color", INVALID_COLORS)
def test_validate_color_with_invalid_color_raises_value_error(invalid_color) -> None:
    """
    Arrange: Get an invalid color string.
    Act: Call validate_color with the invalid string.
    Assert: A ValueError is raised.
    """
    with pytest.raises(ValueError):
        validate_color(invalid_color)


@pytest.mark.parametrize("hex_input, expected_rgb", HEX_TO_RGB_CASES)
def test_hex_to_rgb_converts_correctly(hex_input, expected_rgb) -> None:
    """
    Arrange: Get a hex string and its expected RGB tuple.
    Act: Call hex_to_rgb with the hex string.
    Assert: The returned tuple matches the expected RGB values.
    """
    assert hex_to_rgb(hex_input) == expected_rgb


@pytest.mark.parametrize("text, max_chars, expected_output", TEXT_WRAPPING_CASES)
def test_wrap_text_handles_various_scenarios(text, max_chars, expected_output) -> None:
    """
    Arrange: Get text, max characters per line, and the expected wrapped output.
    Act: Call wrap_text with the provided text and max_chars.
    Assert: The output matches the expected wrapped string.
    """
    # Act
    result = wrap_text(text, max_chars)
    # Assert
    assert result == expected_output
