"""Integration tests for the social media post generation workflow."""

from pathlib import Path

import pytest

from agency_toolkit.core.social import generate as generate_social_post


# A sample config object for tests
# In a real scenario, this might be a more complex fixture
@pytest.fixture
def mock_config() -> None:
    class MockConfig:
        def __init__(self) -> None:
            self.social_style = "modern"
            self.social_color = "blue"
            self.social_format = "square"
            self.json_output = False

    return MockConfig()


def test_generate_social_post_creates_png_file_successfully(
    tmp_path, mock_config
) -> None:
    """
    Arrange: Set up a temporary output directory and a mock config.
    Act: Call generate_social_post with valid text.
    Assert: A dictionary with a valid path to a PNG file is returned, and the
    file exists.
    """
    # Arrange
    output_dir = tmp_path

    # Act
    result = generate_social_post(
        text="This is a test post for an integration test.",
        style=mock_config.social_style,
        color=mock_config.social_color,
        format_name=mock_config.social_format,
        output_dir=output_dir,
    )

    # Assert
    assert isinstance(result, dict)
    assert "path" in result

    image_path = Path(result["path"])
    assert image_path.parent == output_dir
    assert image_path.name.startswith("social_")
    assert image_path.suffix == ".png"
    assert image_path.exists()
    assert image_path.stat().st_size > 0  # File is not empty


def test_generate_social_post_with_dry_run_does_not_create_file(
    tmp_path, mock_config
) -> None:
    """
    Arrange: Set up a temporary output directory and a mock config.
    Act: Call generate_social_post with dry_run=True.
    Assert: A dictionary with a path is returned, but the file does not exist.
    """
    # Arrange
    output_dir = tmp_path

    # Act
    result = generate_social_post(
        text="This is a dry run test.",
        style=mock_config.social_style,
        color=mock_config.social_color,
        format_name=mock_config.social_format,
        output_dir=output_dir,
        dry_run=True,
    )

    # Assert
    assert isinstance(result, dict)
    assert result.get("dry_run") is True
    assert "path" in result

    image_path = Path(result["path"])
    assert not image_path.exists()


@pytest.mark.parametrize("empty_text", ["", "   ", "\n"])
def test_generate_social_post_with_empty_text_raises_value_error(
    mock_config, empty_text
) -> None:
    """
    Arrange: Get an empty or whitespace-only text string.
    Act: Call generate_social_post with the empty text.
    Assert: A ValueError is raised.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="Text cannot be empty"):
        generate_social_post(
            text=empty_text,
            style=mock_config.social_style,
            color=mock_config.social_color,
            format_name=mock_config.social_format,
        )


def test_generate_social_post_with_invalid_style_raises_error(mock_config) -> None:
    """
    Arrange: Set an invalid style in the mock config.
    Act: Call generate_social_post.
    Assert: The function raises ValueError with helpful error message.
    """
    # Act - The code now fails loudly with clear error instead of silently falling back
    with pytest.raises(ValueError) as exc_info:
        generate_social_post(
            text="Test with invalid style",
            style="invalid_style",
            color=mock_config.social_color,
            format_name=mock_config.social_format,
            dry_run=True,
        )

    # Assert - Should mention the invalid style and available options
    assert "invalid_style" in str(exc_info.value)
    assert "Available styles" in str(exc_info.value)
