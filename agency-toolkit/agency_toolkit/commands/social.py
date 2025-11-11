"""Social media post generation command (refactored to thin CLI layer)."""

import logging
from pathlib import Path

import typer

from agency_toolkit.core.reporter import Reporter, get_reporter
from agency_toolkit.core.social import (
    generate as generate_social_post,
)
from agency_toolkit.core.social import (
    generate_background,
    process_batch_csv,
    process_batch_json,
)
from agency_toolkit.wizards import social_wizard

logger = logging.getLogger(__name__)

social_command = typer.Typer(
    help="Generate social media posts", invoke_without_command=True
)


@social_command.callback()
def social_callback(ctx: typer.Context) -> None:
    """Handle wizard mode when no subcommand is provided."""
    # If no subcommand and no arguments, launch wizard
    if ctx.invoked_subcommand is None:
        config = ctx.obj
        social_wizard(config)
        raise typer.Exit()


def _validate_social_arguments(
    text: str | None, from_csv: Path | None, from_json: Path | None
) -> None:
    """Validate social command arguments for mutual exclusivity."""
    reporter = get_reporter()

    _validate_batch_file_exclusivity(from_csv, from_json, reporter)
    _validate_text_batch_exclusivity(text, from_csv, from_json, reporter)
    _validate_at_least_one_input(text, from_csv, from_json, reporter)


def _validate_batch_file_exclusivity(
    from_csv: Path | None, from_json: Path | None, reporter
) -> None:
    """Validate that only one batch file format is used."""
    if from_csv and from_json:
        reporter.error("Cannot use both --from-csv and --from-json")


def _validate_text_batch_exclusivity(
    text: str | None, from_csv: Path | None, from_json: Path | None, reporter
) -> None:
    """Validate that text is not used with batch files."""
    if (from_csv or from_json) and text:
        reporter.error("Cannot use --text with --from-csv or --from-json")


def _validate_at_least_one_input(
    text: str | None, from_csv: Path | None, from_json: Path | None, reporter
) -> None:
    """Validate that at least one input method is provided."""
    if not text and not from_csv and not from_json:
        reporter.error("Must provide text argument or use --from-csv/--from-json")


def _determine_processing_mode(
    text: str | None, from_csv: Path | None, from_json: Path | None
) -> str:
    """Determine which processing mode to use based on arguments.

    Returns:
        'single', 'csv', or 'json'
    """
    if from_csv:
        return "csv"
    elif from_json:
        return "json"
    else:
        return "single"


def _handle_social_error(config, error: Exception, reporter: Reporter) -> None:
    """Handle and display social command errors."""
    reporter.error(str(error), {"module": "social"})


@social_command.command(name="generate")
def social(
    ctx: typer.Context,
    text: str | None = typer.Argument(None, help="Main text content for the post"),
    style: str = typer.Option("modern", "--style", help="Template style"),
    color: str = typer.Option("blue", "--color", help="Color (or 'custom')"),
    custom_color: str | None = typer.Option(
        None, "--custom-color", help="Hex color if color=custom"
    ),
    format_type: str = typer.Option("square", "--format", help="Image format"),
    bg_concept: str | None = typer.Option(
        None,
        "--bg-concept",
        help="Background concept (e.g., 'moody', 'registry:moody')",
    ),
    bg_seed: int | None = typer.Option(
        None, "--bg-seed", help="Fixed seed for reproducible background"
    ),
    output_path: Path | None = typer.Option(
        None, "--output", help="Custom output path"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without saving"),
    from_csv: Path | None = typer.Option(
        None, "--from-csv", help="Generate posts from CSV file"
    ),
    from_json: Path | None = typer.Option(
        None, "--from-json", help="Generate posts from JSON file"
    ),
) -> None:
    """Generate social media post image with optional AI background.

    Examples:
        toolkit social "Hello!" --style bold
        toolkit social "Check it out" --bg-concept "moody"
        toolkit social "Hello" --bg-concept "registry:corporate"
        toolkit social generate --from-csv campaign.csv
        toolkit social generate --from-json posts.json
    """
    config = ctx.obj

    # Initialize reporter via dependency injection (singleton pattern)
    reporter = get_reporter(config.json_output)

    try:
        # Validate arguments
        _validate_social_arguments(text, from_csv, from_json)

        # Determine processing mode and route accordingly
        mode = _determine_processing_mode(text, from_csv, from_json)

        if mode == "csv":
            _handle_batch_csv(config, from_csv, output_path, dry_run, reporter)
        elif mode == "json":
            _handle_batch_json(config, from_json, output_path, dry_run, reporter)
        else:  # single
            _handle_single_post(
                config,
                text,
                style,
                color,
                custom_color,
                format_type,
                bg_concept,
                bg_seed,
                output_path,
                dry_run,
                reporter,
            )

    except Exception as e:
        _handle_social_error(config, e, reporter)


def _handle_single_post(
    config,
    text,
    style,
    color,
    custom_color,
    format_type,
    bg_concept,
    bg_seed,
    output_path,
    dry_run,
    reporter: Reporter,
):
    """Handle single post generation (thin wrapper)."""
    background_image_path = None
    total_cost = 0.0

    # Generate background if requested
    if bg_concept:
        if not dry_run:
            reporter.processing("📸 Generating background image...")

        try:
            bg_result = generate_background(
                bg_concept=bg_concept,
                bg_seed=bg_seed,
                provider=getattr(config.image, "provider", "pollinations"),
                config=config,
            )
            background_image_path = Path(bg_result["path"])
            total_cost += bg_result.get("cost", 0.0)

            if not dry_run:
                reporter.success("Background created")
        except Exception as e:
            reporter.error(f"Background generation failed: {e}")

    # Generate social post
    output_dir = output_path or (config.output_dir / "social")
    result_data = generate_social_post(
        text=text,
        style=style,
        color=color,
        custom_color=custom_color,
        format_name=format_type,
        output_dir=output_dir,
        dry_run=dry_run,
        background_image_path=background_image_path,
    )

    if dry_run:
        reporter.dry_run(f"Would create: {result_data['path']}")
    else:
        reporter.success(
            f"Social post created: {result_data['path']}",
            {
                "module": "social",
                **result_data,
            },
        )
        if total_cost > 0:
            reporter.cost(total_cost)


def _handle_batch_csv(config, csv_path, output_path, dry_run, reporter: Reporter):
    """Handle CSV batch processing (thin wrapper)."""
    reporter.processing(f"📄 Processing batch from CSV: {csv_path}")

    result = process_batch_csv(
        config=config,
        csv_path=csv_path,
        output_dir=output_path,
        dry_run=dry_run,
    )

    _display_batch_results(config, result, dry_run, reporter)


def _handle_batch_json(config, json_path, output_path, dry_run, reporter: Reporter):
    """Handle JSON batch processing (thin wrapper)."""
    reporter.processing(f"📄 Processing batch from JSON: {json_path}")

    result = process_batch_json(
        config=config,
        json_path=json_path,
        output_dir=output_path,
        dry_run=dry_run,
    )

    _display_batch_results(config, result, dry_run, reporter)


def _display_batch_results(config, result, dry_run, reporter: Reporter):
    """Display batch processing results."""
    reporter.batch_summary(
        total=result["total"],
        successful=result["successful"],
        failed=result.get("failed", 0),
    )
