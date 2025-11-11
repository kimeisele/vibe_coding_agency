"""Validation functions for project structure creation."""

from agency_toolkit.exceptions import ConfigurationError


def validate_names(client: str, project: str) -> None:
    """Validate client and project names.

    Args:
        client: Client name
        project: Project name

    Raises:
        ConfigurationError: If names are empty
    """
    if not client.strip() or not project.strip():
        raise ConfigurationError("Client and project names cannot be empty")


def validate_structure_type(structure_type: str) -> str:
    """Validate and normalize structure type.

    Args:
        structure_type: Structure type name

    Returns:
        Validated structure type (defaults to 'web' if unknown)
    """
    valid_types = ["print", "web", "social", "video", "app"]
    if structure_type not in valid_types:
        return "web"
    return structure_type
