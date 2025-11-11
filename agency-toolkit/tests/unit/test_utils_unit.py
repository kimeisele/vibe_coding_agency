"""Unit tests for utility functions."""

import pytest

from agency_toolkit.utils import sanitize_name


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        ("Simple Name", "simple-name"),
        ("A--Weird  --Name", "a-weird-name"),
        ("Name with special chars!@#$%", "name-with-special-chars"),
        ("already-valid-slug", "already-valid-slug"),
        ("UPPERCASE NAME", "uppercase-name"),
        ("", ""),
        ("  leading and trailing spaces  ", "leading-and-trailing-spaces"),
    ],
)
def test_sanitize_name_handles_various_inputs_correctly(
    input_name, expected_output
) -> None:
    """
    Arrange: Get the input name and expected output from parametrize.
    Act: Call sanitize_name with the input.
    Assert: The output matches the expected sanitized string.
    """
    # Act
    result = sanitize_name(input_name)

    # Assert
    assert result == expected_output
