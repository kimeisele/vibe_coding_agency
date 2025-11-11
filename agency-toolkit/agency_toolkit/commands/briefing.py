"""Project briefing generation command."""

import json
import logging
from datetime import datetime
from pathlib import Path

import typer

from agency_toolkit.core.briefing import (
    BriefingData,
    collect_interactive,
    generate,
    load_briefing_questions,
    load_from_json,
)

logger = logging.getLogger(__name__)

briefing_command = typer.Typer(help="Generate project briefings")


@briefing_command.command(name="briefing")
def briefing(
    ctx: typer.Context,
    from_json: Path | None = typer.Option(
        None, "--from-json", help="Load briefing from JSON file"
    ),
    briefing_type: str = typer.Option(
        "default", "--type", help="Briefing template type (default, web, video)"
    ),
    format_type: str = typer.Option(
        "pdf", "--format", help="Output format (pdf or md)"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without saving"),
) -> None:
    """Generate project briefing in PDF or Markdown format.

    Examples:
        # Interactive mode with default template
        toolkit briefing

        # Use web-specific template
        toolkit briefing --type web

        # Use video-specific template
        toolkit briefing --type video

        # From JSON file
        toolkit briefing --from-json briefing.json
    """
    config = ctx.obj

    try:
        output_dir = config.output_dir / "briefings"

        if from_json:
            briefing_data = load_from_json(from_json)
        else:
            # Load template and collect interactively
            template = load_briefing_questions(briefing_type)
            collected_data = collect_interactive(template)

            # Parse deadline
            if "deadline" in collected_data:
                deadline_str = collected_data["deadline"]
                try:
                    collected_data["deadline"] = datetime.strptime(
                        deadline_str, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    raise ValueError(
                        f"Invalid deadline format: {deadline_str}. Use YYYY-MM-DD"
                    )

            # Parse budget if present
            if "budget" in collected_data and collected_data["budget"]:
                try:
                    collected_data["budget"] = float(collected_data["budget"])
                except ValueError:
                    collected_data.pop("budget")  # Remove if not a valid number

            # Create BriefingData with collected data
            briefing_data = BriefingData(**collected_data)

        result_data = generate(
            briefing_data=briefing_data,
            format_type=format_type.lower(),
            output_dir=output_dir,
            dry_run=dry_run,
        )

        output_data = {"status": "success", "module": "briefing", **result_data}

        if config.json_output:
            print(json.dumps(output_data))
        else:
            if dry_run:
                typer.echo(f"[DRY RUN] Would create: {result_data['path']}")
            else:
                typer.echo(f"✓ Briefing created: {result_data['path']}")

    except Exception as e:
        output_data = {"status": "error", "module": "briefing", "message": str(e)}
        if not config.json_output:
            typer.secho(f"✗ Error: {e}", fg="red")
        else:
            print(json.dumps(output_data))
        raise typer.Exit(1)
