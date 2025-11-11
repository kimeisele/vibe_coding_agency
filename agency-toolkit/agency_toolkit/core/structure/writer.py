"""File system operations for project structure creation."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from agency_toolkit.exceptions import OutputPathError

logger = logging.getLogger(__name__)


def check_path_exists(root_path: Path, force: bool) -> None:
    """Check if path exists and handle force flag.

    Args:
        root_path: Target root path
        force: If True, remove existing directory

    Raises:
        OutputPathError: If path exists and force=False
    """
    if root_path.exists() and not force:
        raise OutputPathError(
            f"Path already exists: {root_path}\n" "Use --force to overwrite"
        )

    if root_path.exists() and force:
        shutil.rmtree(root_path)
        logger.info(f"Removed existing directory: {root_path}")


def create_directories(root_path: Path, folder_names: list[str]) -> list[Path]:
    """Create directory structure.

    Args:
        root_path: Root path for structure
        folder_names: List of folder names to create

    Returns:
        List of created folder paths

    Raises:
        OutputPathError: If directory creation fails
    """
    folders_created = []

    try:
        for folder_name in folder_names:
            folder_path = root_path / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
            folders_created.append(folder_path)

        return folders_created

    except OSError as e:
        raise OutputPathError(f"Failed to create folder structure: {e}") from e


def create_readme(
    root_path: Path, client: str, project: str, structure_type: str, folders: list[str]
) -> None:
    """Create README.md in project root.

    Args:
        root_path: Project root path
        client: Client name
        project: Project name
        structure_type: Structure type
        folders: List of folder names
    """
    readme_path = root_path / "README.md"

    readme_content = f"""# {project}

**Client:** {client}
**Type:** {structure_type.capitalize()}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Folder Structure

"""
    for folder in folders:
        readme_content += f"- `{folder}/`\n"

    if not readme_path.exists():
        readme_path.write_text(readme_content)
