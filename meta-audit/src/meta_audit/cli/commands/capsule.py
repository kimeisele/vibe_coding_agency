"""
CLI commands for managing ProjectCapsule snapshots.

capsule create: Create a snapshot of a project
capsule list:   List available capsules
capsule show:   Inspect capsule contents
"""

import sys
import click
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from meta_audit.core.models import ProjectCapsule, CapsuleFile

logger = logging.getLogger(__name__)


def discover_python_files(project_path: Path) -> List[Path]:
    """
    Find all Python files in a project, excluding virtual environments and git directories.

    Args:
        project_path: Root path of the project

    Returns:
        List of Path objects for all .py files
    """
    skip_dirs = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache"}
    python_files = []

    for py_file in project_path.rglob("*.py"):
        # Skip if any part of the path is in skip_dirs
        if any(part in py_file.parts for part in skip_dirs):
            continue
        python_files.append(py_file)

    return sorted(python_files)


def read_file_content(file_path: Path) -> Optional[str]:
    """
    Read file content with error handling.

    Args:
        file_path: Path to file to read

    Returns:
        File content or None if reading failed
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, IOError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return None


@click.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option(
    "--output-file",
    default=None,
    type=click.Path(),
    help="Output capsule filename (default: <project_name>.capsule.json)",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def create(project_path: str, output_file: Optional[str], verbose: bool):
    """
    Create a ProjectCapsule snapshot of a project.

    Scans the project, collects all .py file contents, and exports as JSON.
    Capsule files can be analyzed offline later without access to the original project.

    Example:
        meta-audit capsule create /path/to/project --output-file my_project.capsule.json
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Convert to Path object
    project_root = Path(project_path).resolve()

    if not project_root.is_dir():
        click.echo(click.style(f"ERROR: Path is not a directory: {project_path}", fg="red"))
        raise click.Abort()

    project_name = project_root.name

    click.echo(f"Creating ProjectCapsule snapshot for: {project_name}")
    click.echo(f"  Project path: {project_root}")

    # Phase 1: Discover Python files
    click.echo("\nPhase 1: Discovering Python files...")
    python_files = discover_python_files(project_root)

    if not python_files:
        click.echo(click.style(f"⚠️  No Python files found in {project_path}", fg="yellow"))
        raise click.Abort()

    click.echo(f"  Found {len(python_files)} Python files")

    # Phase 2: Read file contents and create CapsuleFile objects
    click.echo("\nPhase 2: Reading file contents...")
    capsule_files: List[CapsuleFile] = []
    total_size = 0
    failed_count = 0

    for i, py_file in enumerate(python_files, 1):
        # Show progress
        if i % 10 == 0:
            click.echo(f"  Progress: {i}/{len(python_files)}")

        content = read_file_content(py_file)
        if content is None:
            failed_count += 1
            continue

        file_size = len(content.encode("utf-8"))
        total_size += file_size

        # Store relative path for capsule
        rel_path = py_file.relative_to(project_root)

        capsule_file = CapsuleFile(path=rel_path, size_bytes=file_size, content=content)
        capsule_files.append(capsule_file)

    if failed_count > 0:
        click.echo(
            click.style(f"⚠️  Warning: Failed to read {failed_count} files", fg="yellow")
        )

    click.echo(f"  ✓ Read {len(capsule_files)} files ({total_size / 1024 / 1024:.2f} MB)")

    # Phase 3: Create ProjectCapsule
    click.echo("\nPhase 3: Creating ProjectCapsule...")
    try:
        capsule = ProjectCapsule(
            version=2,
            created_at=datetime.now(),
            python_version="3.11",  # Could detect this dynamically
            project_root=project_root,
            project_name=project_name,
            files_count=len(capsule_files),
            total_size_bytes=total_size,
            files=capsule_files,
        )
        click.echo("  ✓ ProjectCapsule created successfully")
    except Exception as e:
        click.echo(click.style(f"ERROR: Failed to create ProjectCapsule: {e}", fg="red"))
        logger.exception("ProjectCapsule creation failed")
        raise click.Abort()

    # Phase 4: Export to JSON
    click.echo("\nPhase 4: Exporting to JSON...")

    # Determine output filename
    if output_file is None:
        output_file = f"{project_name}.capsule.json"

    output_path = Path(output_file).resolve()

    try:
        # Use Pydantic's model_dump with JSON mode for proper serialization
        capsule_data = capsule.model_dump(mode="json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(capsule_data, f, indent=2)

        file_size = output_path.stat().st_size
        click.echo(f"  ✓ Capsule exported to: {output_path}")
        click.echo(f"  ✓ File size: {file_size / 1024:.2f} KB")

    except Exception as e:
        click.echo(click.style(f"ERROR: Failed to export capsule: {e}", fg="red"))
        logger.exception("JSON export failed")
        raise click.Abort()

    # Success summary
    click.echo("\n" + "=" * 70)
    click.echo("ProjectCapsule Creation Successful!")
    click.echo("=" * 70)
    click.echo(f"Project: {project_name}")
    click.echo(f"Files: {len(capsule_files)}")
    click.echo(f"Total size: {total_size / 1024 / 1024:.2f} MB")
    click.echo(f"Created: {capsule.created_at.isoformat()}")
    click.echo(f"Output: {output_path.absolute()}")
    click.echo(f"\nYou can now analyze this capsule offline:")
    click.echo(f"  meta-audit analyze --capsule {output_file}")


@click.command()
@click.argument("capsule_path", type=click.Path(exists=True))
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def show(capsule_path: str, verbose: bool):
    """
    Inspect the contents of a ProjectCapsule file.

    Shows metadata and list of files in the capsule.

    Example:
        meta-audit capsule show my_project.capsule.json
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    capsule_file = Path(capsule_path)

    if not capsule_file.exists():
        click.echo(click.style(f"ERROR: Capsule file not found: {capsule_path}", fg="red"))
        raise click.Abort()

    try:
        with open(capsule_file, "r", encoding="utf-8") as f:
            capsule_data = json.load(f)

        click.echo("\n" + "=" * 70)
        click.echo("ProjectCapsule Information")
        click.echo("=" * 70)
        click.echo(f"Project: {capsule_data.get('project_name', 'N/A')}")
        click.echo(f"Version: {capsule_data.get('version', 'N/A')}")
        click.echo(f"Created: {capsule_data.get('created_at', 'N/A')}")
        click.echo(f"Python Version: {capsule_data.get('python_version', 'N/A')}")
        click.echo(f"Project Root: {capsule_data.get('project_root', 'N/A')}")
        click.echo(f"Files: {capsule_data.get('files_count', 0)}")
        click.echo(f"Total Size: {capsule_data.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB")

        # Show file list (limited to first 20)
        files = capsule_data.get("files", [])
        if files:
            click.echo(f"\nFirst 20 files:")
            for i, file in enumerate(files[:20], 1):
                size_kb = file.get("size_bytes", 0) / 1024
                click.echo(f"  {i:3d}. {file.get('path', 'N/A')} ({size_kb:.1f} KB)")

            if len(files) > 20:
                click.echo(f"  ... and {len(files) - 20} more files")

        click.echo("=" * 70)

    except Exception as e:
        click.echo(click.style(f"ERROR: Failed to read capsule: {e}", fg="red"))
        logger.exception("Capsule inspection failed")
        raise click.Abort()
