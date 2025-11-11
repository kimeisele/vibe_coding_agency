"""Project structure generator orchestrator."""

import json
import logging
from pathlib import Path

from agency_toolkit.core.structure.templates import get_template
from agency_toolkit.core.structure.validators import (
    validate_names,
    validate_structure_type,
)
from agency_toolkit.core.structure.writer import (
    check_path_exists,
    create_directories,
    create_readme,
)
from agency_toolkit.utils import sanitize_name

logger = logging.getLogger(__name__)


def generate(
    client: str,
    project: str,
    structure_type: str = "web",
    base_path: Path = Path("."),
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Create project folder structure.

    Args:
        client: Client name
        project: Project name
        structure_type: Type of structure (print, web, social, video)
        base_path: Base directory for creation
        dry_run: If True, return preview without creating
        force: If True, overwrite existing structure

    Returns:
        Dict with path and type

    Raises:
        ConfigurationError: If inputs invalid
        OutputPathError: If path exists or creation fails
    """
    # Validate inputs
    validate_names(client, project)

    # Sanitize names
    client_slug = sanitize_name(client)
    project_slug = sanitize_name(project)

    # Validate and normalize structure type
    structure_type = validate_structure_type(structure_type)

    # Load template
    template = get_template(structure_type)

    # Determine root path
    root_path = base_path / client_slug / project_slug

    # Check path existence
    check_path_exists(root_path, force)

    # Get folder list
    folder_names = template.get("folders", [])

    # Dry run preview
    if dry_run:
        preview = {
            "root": str(root_path),
            "folders": [str(root_path / f) for f in folder_names],
            "count": len(folder_names),
        }
        logger.info("DRY RUN - Preview:")
        logger.info(json.dumps(preview, indent=2))
        return {"path": str(root_path), "type": structure_type}

    # Create structure
    folders_created = create_directories(root_path, folder_names)

    # Create README
    create_readme(root_path, client, project, structure_type, folder_names)

    logger.info(f"Created folder structure: {root_path}")
    logger.info(f"Folders created: {len(folders_created)}")

    return {"path": str(root_path), "type": structure_type}
