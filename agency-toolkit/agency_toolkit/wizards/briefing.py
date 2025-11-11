"""Briefing Generation Wizard (WU-7.3)."""

from pathlib import Path

import typer

from agency_toolkit.core.briefing import (
    BriefingData,
    generate,
)
from agency_toolkit.core.reporter import get_reporter

from .helpers import (
    confirm_proceed,
    prompt_choice,
    prompt_path,
    prompt_text,
    prompt_yes_no,
    show_header,
    show_summary,
)


def briefing_wizard(config) -> None:
    """Interactive wizard for briefing generation."""
    show_header("📄 Briefing Generator Wizard")

    # Step 1: Project name
    typer.echo("Step 1: What's your project?")
    typer.echo("   Example: 'Q4 Marketing Campaign'\n")
    project_name = prompt_text("Project name", required=True)

    # Step 2: Add description
    has_description = prompt_yes_no("\nStep 2: Add description?", default=True)
    description = None
    if has_description:
        description = prompt_text("Project description")

    # Step 3: Briefing type
    briefing_type_choices = [
        ("project", "Comprehensive project brief"),
        ("campaign", "Marketing campaign brief"),
        ("proposal", "Business proposal"),
        ("other", "Custom content"),
    ]
    briefing_type = prompt_choice(
        "\nStep 3: What type of briefing?", briefing_type_choices, default="project"
    )

    # Step 4: Export format
    export_choices = [
        ("markdown", "Quick, readable"),
        ("pdf", "Professional, shareable"),
        ("both", "Markdown + PDF"),
    ]
    export_format = prompt_choice(
        "\nStep 4: Export format?", export_choices, default="both"
    )

    # Step 5: Team members
    add_team = prompt_yes_no("\nStep 5: Add team members?", default=False)
    team_members = []
    if add_team:
        typer.echo("   Enter names separated by commas")
        team_input = prompt_text("Team members")
        team_members = [m.strip() for m in team_input.split(",") if m.strip()]

    # Step 6: Output directory
    default_output = Path("./output/briefing")
    output_dir = prompt_path("\nStep 6: Output directory", default_output)

    # Summary
    data = {
        "project_name": project_name,
        "description": description or "None",
        "briefing_type": briefing_type,
        "export_format": export_format,
        "team_members": ", ".join(team_members) if team_members else "None",
        "output_directory": str(output_dir),
    }
    show_summary(data)

    if not confirm_proceed("Ready to generate briefing?"):
        typer.secho("✋ Cancelled. No briefing generated.", fg="yellow")
        return

    # Generate briefing
    _generate_briefing(
        config,
        project_name,
        description,
        briefing_type,
        export_format,
        team_members,
        output_dir,
    )


def _generate_briefing(
    config,
    project_name: str,
    description: str | None,
    briefing_type: str,
    export_format: str,
    team_members: list[str],
    output_dir: Path,
) -> None:
    """Generate briefing based on wizard selections."""
    reporter = get_reporter(config.json_output)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo("\n✨ Generating briefing...")

    try:
        # Create briefing data from wizard inputs
        briefing_data = BriefingData(
            project=project_name,
            description=description or "",
            briefing_type=briefing_type,
            team_members=team_members,
        )

        # Generate briefing using the core function
        result = generate(
            briefing_data=briefing_data,
            format_type=export_format.lower().replace("+", ","),
            output_dir=output_dir,
            dry_run=False,
        )

        # Display results
        typer.secho("\n" + "=" * 50, fg="cyan")
        typer.secho("✅ Briefing generated successfully!", fg="green")
        typer.secho(f"   📄 Path: {Path(result['path']).name}", fg="cyan")
        typer.secho(f"   📁 Location: {output_dir}", fg="cyan")
        typer.secho("=" * 50 + "\n", fg="cyan")

    except Exception as e:
        reporter.error(f"Briefing generation failed: {e}")
        typer.secho(f"❌ Error: {e}", fg="red")
