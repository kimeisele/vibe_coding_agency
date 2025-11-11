"""Unit tests for the configuration constants."""

import pytest

from agency_toolkit.config import COLORS, FORMATS

# A list of expected color names.
# This makes the test more explicit and easier to update.
EXPECTED_COLORS = ["blue", "red", "green", "purple"]

# A list of expected format names.
EXPECTED_FORMATS = ["square", "story", "landscape"]


@pytest.mark.parametrize("color_name", EXPECTED_COLORS)
def test_colors_contain_expected_named_colors(color_name) -> None:
    """
    Arrange: The COLORS dictionary is imported.
    Act: Check for the presence of a color name.
    Assert: The expected color name is a key in the COLORS dictionary.
    """
    assert color_name in COLORS


@pytest.mark.parametrize("format_name", EXPECTED_FORMATS)
def test_formats_contain_expected_named_formats(format_name) -> None:
    """
    Arrange: The FORMATS dictionary is imported.
    Act: Check for the presence of a format name.
    Assert: The expected format name is a key in the FORMATS dictionary.
    """
    assert format_name in FORMATS


@pytest.mark.parametrize("color_name", EXPECTED_COLORS)
def test_color_value_is_valid_hex_string(color_name) -> None:
    """
    Arrange: The COLORS dictionary is imported.
    Act: Retrieve the hex value for a given color name.
    Assert: The value is a valid 7-character hex string starting with '#'.
    """
    # Arrange
    hex_value = COLORS[color_name]

    # Act & Assert
    assert isinstance(hex_value, str)
    assert hex_value.startswith("#")
    assert len(hex_value) == 7


@pytest.mark.parametrize("format_name", EXPECTED_FORMATS)
def test_format_dimensions_are_valid_size_tuples(format_name) -> None:
    """
    Arrange: The FORMATS dictionary is imported.
    Act: Retrieve the dimensions for a given format name.
    Assert: The dimensions are a tuple of two positive integers.
    """
    # Arrange
    dimensions = FORMATS[format_name]

    # Act & Assert
    assert isinstance(dimensions, tuple)
    assert len(dimensions) == 2
    assert isinstance(dimensions[0], int)
    assert isinstance(dimensions[1], int)
    assert dimensions[0] > 0
    assert dimensions[1] > 0
