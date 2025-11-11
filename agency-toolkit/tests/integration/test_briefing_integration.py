"""Integration tests for the briefing generation module."""

import json
from datetime import date
from pathlib import Path

import pytest

from agency_toolkit.core.briefing import (
    BriefingData,
    generate,
    load_briefing_questions,
    load_from_json,
)


@pytest.fixture
def sample_briefing_data() -> None:
    """Provides a valid BriefingData object for tests."""
    return BriefingData(
        client_name="Test Client",
        project_name="Test Project",
        project_type="Web",
        deadline=date(2024, 12, 31),
        deliverables=["Final Report"],
    )


# --- Briefing Generation Tests ---


@pytest.mark.parametrize("format_type", ["md", "pdf"])
def test_generate_creates_file_successfully(
    sample_briefing_data, tmp_path, format_type
) -> None:
    """
    Arrange: Get sample data, a temp path, and a format type.
    Act: Call generate.
    Assert: A file with the correct format and content is created.
    """
    # Arrange
    if format_type == "pdf":
        try:
            import fpdf  # noqa: F401
        except ImportError:
            pytest.skip("PDF generation requires fpdf, which is not installed.")

    output_dir = tmp_path

    # Act
    result = generate(
        briefing_data=sample_briefing_data,
        format_type=format_type,
        output_dir=output_dir,
    )

    # Assert
    briefing_path = Path(result["path"])
    assert briefing_path.exists()
    assert briefing_path.suffix == f".{format_type}"
    assert briefing_path.stat().st_size > 0


def test_generate_with_dry_run_does_not_create_file(
    sample_briefing_data, tmp_path
) -> None:
    """
    Arrange: Get sample data and a temp path.
    Act: Call generate with dry_run=True.
    Assert: The returned path does not exist.
    """
    # Act
    result = generate(
        briefing_data=sample_briefing_data,
        format_type="md",
        output_dir=tmp_path,
        dry_run=True,
    )

    # Assert
    assert not Path(result["path"]).exists()


# --- Loading from JSON Tests ---


def test_load_briefing_from_valid_json_returns_briefing_data(tmp_path) -> None:
    """
    Arrange: Create a valid briefing JSON file.
    Act: Call load_from_json.
    Assert: A BriefingData object with correct data is returned.
    """
    # Arrange
    data = {
        "client_name": "JSON Client",
        "project_name": "JSON Project",
        "project_type": "Video",
        "deadline": "2024-11-30",
        "deliverables": ["Raw footage"],
    }
    json_file = tmp_path / "briefing.json"
    json_file.write_text(json.dumps(data))

    # Act
    briefing_data = load_from_json(json_file)

    # Assert
    assert isinstance(briefing_data, BriefingData)
    assert briefing_data.client_name == "JSON Client"
    assert briefing_data.deadline == date(2024, 11, 30)


def test_load_briefing_from_missing_file_raises_file_not_found_error() -> None:
    """
    Arrange: Define a path to a non-existent file.
    Act: Call load_from_json.
    Assert: FileNotFoundError is raised.
    """
    # Arrange
    missing_file = Path("/non/existent/file.json")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        load_from_json(missing_file)


def test_load_briefing_from_invalid_json_raises_value_error(tmp_path) -> None:
    """
    Arrange: Create a file with invalid JSON content.
    Act: Call load_from_json.
    Assert: A ValueError is raised.
    """
    # Arrange
    json_file = tmp_path / "invalid.json"
    json_file.write_text("this is not json")

    # Act & Assert
    with pytest.raises(ValueError):
        load_from_json(json_file)


# --- Template Loading Tests ---


@pytest.mark.parametrize("template_type", ["default", "web", "video"])
def testload_briefing_questions_for_valid_types_returns_dict(template_type) -> None:
    """
    Arrange: Get a valid template type.
    Act: Call load_briefing_questions.
    Assert: A dictionary with 'required' and 'optional' keys is returned.
    """
    # Act
    template = load_briefing_questions(template_type)

    # Assert
    assert isinstance(template, dict)
    assert "required" in template
    assert "optional" in template


def testload_briefing_questions_for_invalid_type_raises_file_not_found_error() -> None:
    """
    Arrange: Define an invalid template type.
    Act: Call load_briefing_questions.
    Assert: FileNotFoundError is raised.
    """
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        load_briefing_questions("nonexistent_template")
