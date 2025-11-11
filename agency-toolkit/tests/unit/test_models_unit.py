"""Unit tests for Pydantic models."""

from datetime import date

import pytest
from pydantic import ValidationError

from agency_toolkit.models import BriefingData, Config

# region: Config Model Tests


def test_config_initializes_with_correct_defaults() -> None:
    """
    Arrange: No special arrangement needed.
    Act: Create a Config instance with default values.
    Assert: The instance attributes match the expected defaults.
    """
    # Act
    config = Config()

    # Assert
    assert config.social_style == "modern"
    assert config.social_format == "square"
    assert config.mistral_model == "mistral-small-latest"


@pytest.mark.parametrize("invalid_style", ["fancy", "classic", "", None])
def test_config_raises_error_for_invalid_social_style(invalid_style) -> None:
    """
    Arrange: Get an invalid style from parametrize.
    Act: Attempt to create a Config instance with the invalid style.
    Assert: A Pydantic ValidationError is raised.
    """
    # Act & Assert
    with pytest.raises(ValidationError):
        Config(social_style=invalid_style)


@pytest.mark.parametrize("valid_style", ["modern", "minimal", "bold"])
def test_config_accepts_valid_social_styles(valid_style) -> None:
    """
    Arrange: Get a valid style from parametrize.
    Act: Create a Config instance with the valid style.
    Assert: The instance is created successfully and the attribute is set.
    """
    # Act
    config = Config(social_style=valid_style)

    # Assert
    assert config.social_style == valid_style


@pytest.mark.parametrize("invalid_format", ["portrait", "banner", "", None])
def test_config_raises_error_for_invalid_social_format(invalid_format) -> None:
    """
    Arrange: Get an invalid format from parametrize.
    Act: Attempt to create a Config instance with the invalid format.
    Assert: A Pydantic ValidationError is raised.
    """
    # Act & Assert
    with pytest.raises(ValidationError):
        Config(social_format=invalid_format)


@pytest.mark.parametrize("valid_format", ["square", "story", "landscape"])
def test_config_accepts_valid_social_formats(valid_format) -> None:
    """
    Arrange: Get a valid format from parametrize.
    Act: Create a Config instance with the valid format.
    Assert: The instance is created successfully and the attribute is set.
    """
    # Act
    config = Config(social_format=valid_format)

    # Assert
    assert config.social_format == valid_format


# endregion

# region: BriefingData Model Tests


def test_briefing_data_initializes_with_valid_required_fields() -> None:
    """
    Arrange: Define valid required data for a briefing.
    Act: Create a BriefingData instance.
    Assert: The instance is created and attributes are set correctly.
    """
    # Arrange
    valid_data = {
        "client_name": "Test Client",
        "project_name": "Test Project",
        "project_type": "Web",
        "deadline": date(2024, 12, 31),
    }

    # Act
    briefing = BriefingData(**valid_data)

    # Assert
    assert briefing.client_name == valid_data["client_name"]
    assert briefing.project_name == valid_data["project_name"]


@pytest.mark.parametrize("invalid_type", ["Invalid", "Desktop", ""])
def test_briefing_data_raises_error_for_invalid_project_type(invalid_type) -> None:
    """
    Arrange: Define briefing data with an invalid project type.
    Act: Attempt to create a BriefingData instance.
    Assert: A ValidationError is raised.
    """
    # Arrange
    invalid_data = {
        "client_name": "Test Client",
        "project_name": "Test Project",
        "project_type": invalid_type,
        "deadline": date(2024, 12, 31),
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        BriefingData(**invalid_data)


def test_briefing_data_accepts_valid_optional_fields() -> None:
    """
    Arrange: Define valid data including optional fields.
    Act: Create a BriefingData instance.
    Assert: The optional field attributes are set correctly.
    """
    # Arrange
    full_data = {
        "client_name": "Test Client",
        "project_name": "Test Project",
        "project_type": "Video",
        "deadline": date(2024, 12, 31),
        "budget": 5000.0,
        "objectives": "Test objectives",
        "deliverables": ["A video", "A script"],
    }

    # Act
    briefing = BriefingData(**full_data)

    # Assert
    assert briefing.budget == 5000.0
    assert briefing.objectives == "Test objectives"
    assert briefing.deliverables == ["A video", "A script"]


# endregion
