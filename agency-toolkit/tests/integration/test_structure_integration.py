"""Integration tests for the folder structure creation module."""

from pathlib import Path

import pytest

from agency_toolkit.core.structure import generate as create_folder_structure

STRUCTURE_TYPES = ["default", "print", "web", "social", "video"]


@pytest.mark.parametrize("structure_type", STRUCTURE_TYPES)
def test_create_folder_structure_creates_correct_directory_and_readme(
    tmp_path, structure_type
) -> None:
    """
    Arrange: Define client, project, and base path using tmp_path.
    Act: Call create_folder_structure with a specific type.
    Assert: The main project directory and a README.md file are created successfully.
    """
    # Arrange
    client = "Test Client"
    project = f"Test Project {structure_type}"
    base_path = tmp_path

    # Act
    result = create_folder_structure(
        client=client,
        project=project,
        structure_type=structure_type,
        base_path=base_path,
    )

    # Assert
    project_path = Path(result["path"])
    assert project_path.exists()
    assert project_path.is_dir()
    assert project_path.name == f"test-project-{structure_type}"
    assert project_path.parent.name == "test-client"

    readme_path = project_path / "README.md"
    assert readme_path.exists()
    assert readme_path.is_file()
    assert project in readme_path.read_text()


def test_create_folder_structure_with_dry_run_does_not_create_files(tmp_path) -> None:
    """
    Arrange: Define client, project, and base path.
    Act: Call create_folder_structure with dry_run=True.
    Assert: The returned path does not exist on the filesystem.
    """
    # Arrange
    base_path = tmp_path

    # Act
    result = create_folder_structure(
        client="DryRun Client",
        project="DryRun Project",
        base_path=base_path,
        dry_run=True,
    )

    # Assert
    project_path = Path(result["path"])
    assert not project_path.exists()


@pytest.mark.parametrize("empty_name", ["", "   "])
def test_create_folder_structure_with_empty_client_or_project_raises_value_error(
    tmp_path, empty_name
) -> None:
    """
    Arrange: Use an empty string for the client name.
    Act: Call create_folder_structure.
    Assert: A ConfigurationError is raised.
    """
    from agency_toolkit.exceptions import ConfigurationError

    # Act & Assert
    with pytest.raises(
        ConfigurationError, match="Client and project names cannot be empty"
    ):
        create_folder_structure(
            client=empty_name, project="Project", base_path=tmp_path
        )

    with pytest.raises(
        ConfigurationError, match="Client and project names cannot be empty"
    ):
        create_folder_structure(client="Client", project=empty_name, base_path=tmp_path)


def test_create_folder_structure_when_path_exists_raises_error(tmp_path) -> None:
    """
    Arrange: Create a folder structure once.
    Act: Attempt to create the exact same folder structure again without force=True.
    Assert: An OutputPathError is raised because the path already exists.
    """
    from agency_toolkit.exceptions import OutputPathError

    # Arrange
    base_path = tmp_path
    create_folder_structure(client="Client", project="Project", base_path=base_path)

    # Act & Assert
    with pytest.raises(OutputPathError, match="already exists"):
        create_folder_structure(client="Client", project="Project", base_path=base_path)


def test_create_folder_structure_with_force_flag_overwrites_existing(tmp_path) -> None:
    """
    Arrange: Create a folder structure and place a dummy file inside.
    Act: Call create_folder_structure again on the same path with force=True.
    Assert: The function executes without error and the dummy file is gone.
    """
    # Arrange
    base_path = tmp_path
    result = create_folder_structure(
        client="Client", project="Project", base_path=base_path
    )
    project_path = Path(result["path"])
    dummy_file = project_path / "dummy.txt"
    dummy_file.write_text("This should be deleted.")

    # Act
    create_folder_structure(
        client="Client", project="Project", base_path=base_path, force=True
    )

    # Assert
    assert project_path.exists()
    assert not dummy_file.exists()  # The old content is wiped
