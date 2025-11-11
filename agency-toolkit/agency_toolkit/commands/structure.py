"""Project folder structure creation command."""

import json
import logging
from pathlib import Path

import typer

from agency_toolkit.core.structure import generate

logger = logging.getLogger(__name__)

structure_command = typer.Typer(help="Create project folder structures")


@structure_command.command(name="create")
def structure(
    ctx: typer.Context,
    client: str = typer.Argument(..., help="Client name"),
    project: str = typer.Argument(..., help="Project name"),
    type_name: str = typer.Option("web", "--type", help="Structure type"),
    base_path: Path | None = typer.Option(None, "--base-path", help="Base directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without creating"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing"),
) -> None:
    """Create project folder structure."""
    config = ctx.obj

    try:
        base = base_path or config.output_dir

        result_data = generate(
            client=client,
            project=project,
            structure_type=type_name,
            base_path=base,
            dry_run=dry_run,
            force=force,
        )

        output_data = {"status": "success", "module": "structure", **result_data}

        if config.json_output:
            print(json.dumps(output_data))
        else:
            if dry_run:
                typer.echo(f"[DRY RUN] Would create: {result_data['path']}")
            else:
                typer.echo(f"✓ Folder structure created: {result_data['path']}")

    except Exception as e:
        output_data = {"status": "error", "module": "structure", "message": str(e)}
        if not config.json_output:
            typer.secho(f"✗ Error: {e}", fg="red")
        else:
            print(json.dumps(output_data))
        raise typer.Exit(1)
