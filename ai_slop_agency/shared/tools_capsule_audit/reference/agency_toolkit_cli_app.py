"""Main CLI application using Typer."""

import logging
from pathlib import Path
from typing import Optional

import typer

from agency_toolkit import __version__
from agency_toolkit.commands import (
    ai_command,
    briefing_command,
    image_command,
    info_command,
    os_command,
    social_command,
    structure_command,
    validate_command,
)
from agency_toolkit.logger import setup_logging
from agency_toolkit.utils import load_config

app = typer.Typer(help="Agency Toolkit - CLI tools for agency workflow automation")

logger = logging.getLogger(__name__)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"Agency Toolkit v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(None, "--version", help="Show version"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", help="Override default output directory"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as machine-readable JSON"
    ),
    offline: bool = typer.Option(
        False, "--offline", help="Offline mode - block network calls"
    ),
) -> None:
    """Agency Toolkit main entry point."""
    if version:
        typer.echo(f"Agency Toolkit v{__version__}")
        raise typer.Exit()

    # Skip config loading if only showing help
    if ctx.invoked_subcommand is None and not version:
        return

    log_level = "DEBUG" if verbose else ("WARNING" if quiet else "INFO")

    # Load and validate config (STAB-3.1: Fail-fast on config errors)
    try:
        config = load_config()
    except ValueError as e:
        typer.secho(str(e), fg="red", err=True)
        raise typer.Exit(code=1)

    if output_dir:
        config.output_dir = output_dir
    config.json_output = json_output

    # Handle offline mode
    if offline:
        from agency_toolkit.core.resilience import OfflineMode

        OfflineMode.enable()

    setup_logging(
        level=log_level,
        log_file=config.output_dir / "toolkit.log",
    )

    logger.debug(f"Output directory: {config.output_dir}")
    ctx.obj = config


app.add_typer(social_command, name="social")
app.add_typer(briefing_command, name="briefing")
app.add_typer(structure_command, name="structure")
app.add_typer(ai_command, name="ai")
app.add_typer(image_command, name="image")
app.add_typer(info_command, name="info")
app.add_typer(validate_command, name="validate")
app.add_typer(os_command, name="os")


if __name__ == "__main__":
    app()


def cli_entrypoint() -> None:
    """Entry point for the CLI."""
    app()
