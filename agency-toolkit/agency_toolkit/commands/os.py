"""GRAND AGENCY OS commands (thin CLI layer).

This module provides the Typer CLI interface for GRAND AGENCY OS.
Business logic has been extracted to core/os_executor.py and core/os_interactive.py.
"""

import csv
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agency_toolkit.core.os_executor import execute_project_workflow
from agency_toolkit.core.os_interactive import run_interactive_workflow
from agency_toolkit.core.reporter import get_reporter
from agency_toolkit.core.workflow_loader import validate_registry

app = typer.Typer(help="GRAND AGENCY OS: Orchestrated project workflows")
console = Console()


def _validate_scenario(scenario: dict, idx: int) -> tuple[bool, dict | None]:
    """Validate a single scenario for required fields.

    Args:
        scenario: Scenario dictionary to validate
        idx: Scenario index (for reporting)

    Returns:
        Tuple of (is_valid, error_dict or None)
    """
    required = ["project_name", "archetype_id", "solution_id", "module_id"]
    missing = [f for f in required if f not in scenario or not scenario[f]]

    if missing:
        return False, {
            "scenario": idx,
            "project_name": scenario.get("project_name", "UNKNOWN"),
            "status": "SKIPPED",
            "reason": f"Missing: {', '.join(missing)}",
        }

    return True, None


def _execute_single_scenario(scenario: dict, idx: int) -> dict:
    """Execute a single scenario and return result summary.

    Args:
        scenario: Validated scenario dictionary
        idx: Scenario index

    Returns:
        Result summary dict with status and details
    """
    project_name = scenario["project_name"]
    archetype_id = scenario["archetype_id"]
    solution_id = scenario["solution_id"]
    module_id = scenario["module_id"]
    ai_provider = scenario.get("ai_provider")

    # Display scenario info
    console.print(f"[bold]Project:[/bold] {project_name}")
    console.print(f"[bold]IDs:[/bold] {archetype_id} → {solution_id} → {module_id}")
    if ai_provider:
        console.print(f"[bold]AI Provider:[/bold] {ai_provider}")

    try:
        result = execute_project_workflow(
            project_name=project_name,
            archetype_id=archetype_id,
            solution_id=solution_id,
            module_id=module_id,
            ai_provider=ai_provider,
            stop_on_error=False,
        )

        if result["success"]:
            console.print(
                f"[green]✓ Success:[/green] {result['tasks_success']}/{result['tasks_total']} tasks completed\n"
            )
            return {
                "scenario": idx,
                "project_name": project_name,
                "status": "SUCCESS",
                "tasks": f"{result['tasks_success']}/{result['tasks_total']}",
            }
        else:
            console.print(
                f"[yellow]⚠ Partial:[/yellow] {result['tasks_success']}/{result['tasks_total']} tasks completed\n"
            )
            return {
                "scenario": idx,
                "project_name": project_name,
                "status": "PARTIAL",
                "tasks": f"{result['tasks_success']}/{result['tasks_total']}",
            }

    except ValueError as e:
        console.print(f"[red]✗ Validation Error:[/red] {e}\n")
        return {
            "scenario": idx,
            "project_name": project_name,
            "status": "ERROR",
            "reason": str(e),
        }

    except Exception as e:
        console.print(f"[red]✗ Execution Error:[/red] {e}\n")
        return {
            "scenario": idx,
            "project_name": project_name,
            "status": "FAILED",
            "reason": str(e),
        }


def _display_batch_summary(results_summary: list[dict], reporter=None) -> None:
    """Display batch execution summary table and stats.

    Args:
        results_summary: List of result dictionaries
        reporter: Reporter instance for output
    """
    if reporter is None:
        reporter = get_reporter()

    reporter.info("")
    reporter.info("═══ Batch Summary ═══")
    reporter.divider(30)
    reporter.info("")

    # Create summary table using Rich console (maintaining table format)
    summary_table = Table(show_header=True)
    summary_table.add_column("#", style="cyan")
    summary_table.add_column("Project", style="white")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Details", style="dim")

    for result in results_summary:
        status = result["status"]
        color = {
            "SUCCESS": "green",
            "PARTIAL": "yellow",
            "SKIPPED": "dim",
            "ERROR": "red",
            "FAILED": "red",
        }.get(status, "white")

        details = result.get("tasks", result.get("reason", ""))

        summary_table.add_row(
            str(result["scenario"]),
            result["project_name"],
            f"[{color}]{status}[/{color}]",
            details,
        )

    console.print(summary_table)
    console.print()

    # Final stats using Reporter
    success = sum(1 for r in results_summary if r["status"] == "SUCCESS")
    partial = sum(1 for r in results_summary if r["status"] == "PARTIAL")
    failed = sum(
        1 for r in results_summary if r["status"] in ["ERROR", "FAILED", "SKIPPED"]
    )

    reporter.success(f"✓ Success: {success}")
    reporter.warning(f"⚠ Partial: {partial}")
    reporter.error(f"✗ Failed: {failed}", exit_code=0)
    reporter.info("")


@app.command("init")
def os_init(
    ctx: typer.Context,
    name: str | None = typer.Option(
        None, "--name", "-n", help="Project name (for single execution)"
    ),
    from_csv: Path | None = typer.Option(
        None, "--from-csv", help="Batch process from CSV file"
    ),
    from_json: Path | None = typer.Option(
        None, "--from-json", help="Batch process from JSON file"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show execution plan without running tasks"
    ),
) -> None:
    """Initialize GRAND AGENCY project(s) with guided or batch workflow.

    Modes:
        Interactive (default): Guided workflow with prompts
        Single: Provide --name with flags (future)
        Batch CSV: Process multiple projects from CSV
        Batch JSON: Process multiple projects from JSON

    CSV Format:
        project_name,archetype_id,solution_id,module_id,ai_provider

    JSON Format:
        [{"project_name": "...", "archetype_id": "...", ...}, ...]

    Examples:
        # Interactive mode
        toolkit os init

        # Batch from CSV
        toolkit os init --from-csv scenarios.csv

        # Batch from JSON
        toolkit os init --from-json scenarios.json
    """
    config = ctx.obj
    reporter = get_reporter(config.json_output)

    reporter.info("")
    reporter.info("GRAND AGENCY OS - Project Initialization")
    reporter.divider(60)
    reporter.info("")

    # Validate registry before proceeding
    try:
        validate_registry()
    except Exception as e:
        reporter.error(f"Registry validation failed: {e}")
        raise typer.Exit(code=1)

    # Determine mode
    if from_csv:
        _batch_process_csv(from_csv, reporter)
    elif from_json:
        _batch_process_json(from_json, reporter)
    else:
        # Interactive mode
        if not name:
            name = typer.prompt("Enter project name")

        if dry_run:
            reporter.warning("ℹ  Running in DRY-RUN mode")
            reporter.info("")

        run_interactive_workflow(name, dry_run=dry_run)


def _batch_process_csv(csv_path: Path, reporter=None) -> None:
    """Process multiple projects from CSV file.

    CSV Format:
        project_name,archetype_id,solution_id,module_id,ai_provider

    Args:
        csv_path: Path to CSV file
        reporter: Reporter instance for output
    """
    if reporter is None:
        reporter = get_reporter()

    if not csv_path.exists():
        reporter.error(f"CSV file not found: {csv_path}")
        raise typer.Exit(code=1)

    reporter.info(f"Processing batch from: {csv_path}")
    reporter.info("")

    scenarios = []
    try:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            scenarios = list(reader)
    except Exception as e:
        reporter.error(f"Failed to read CSV: {e}")
        raise typer.Exit(code=1)

    if not scenarios:
        reporter.warning("No scenarios found in CSV")
        return

    _execute_batch(scenarios, reporter)


def _batch_process_json(json_path: Path, reporter=None) -> None:
    """Process multiple projects from JSON file.

    JSON Format:
        [
            {
                "project_name": "Test1",
                "archetype_id": "archetype-i",
                "solution_id": "solution-a1",
                "module_id": "mod-a1-4-recruiting",
                "ai_provider": "google"  // optional
            }
        ]

    Args:
        json_path: Path to JSON file
        reporter: Reporter instance for output
    """
    if reporter is None:
        reporter = get_reporter()

    if not json_path.exists():
        reporter.error(f"JSON file not found: {json_path}")
        raise typer.Exit(code=1)

    reporter.info(f"Processing batch from: {json_path}")
    reporter.info("")

    try:
        scenarios = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        reporter.error(f"Failed to read JSON: {e}")
        raise typer.Exit(code=1)

    if not isinstance(scenarios, list):
        reporter.error("JSON must contain an array of scenarios")
        raise typer.Exit(code=1)

    _execute_batch(scenarios, reporter)


def _process_batch_scenario(
    scenario: dict, idx: int, total: int, reporter=None
) -> dict:
    """Process a single scenario in batch mode.

    Args:
        scenario: Scenario dictionary to process
        idx: Scenario index (for reporting)
        total: Total number of scenarios
        reporter: Reporter instance for output

    Returns:
        Result dictionary
    """
    if reporter is None:
        reporter = get_reporter()

    reporter.info(f"Scenario {idx}/{total}")
    reporter.divider(30)

    # Validate scenario
    is_valid, error_result = _validate_scenario(scenario, idx)
    if not is_valid:
        reporter.error(f"✗ Skipping: Missing required fields: {error_result['reason']}")
        reporter.info("")  # Empty line for spacing
        return error_result

    # Execute scenario
    result = _execute_single_scenario(scenario, idx)
    return result


def _execute_batch(scenarios: list[dict], reporter=None) -> None:
    """Execute batch of scenarios (orchestrator function).

    Args:
        scenarios: List of scenario dictionaries
        reporter: Reporter instance for output
    """
    if reporter is None:
        reporter = get_reporter()

    total = len(scenarios)
    reporter.info(f"Found {total} scenario(s) to process")
    reporter.info("")

    results_summary = []

    for idx, scenario in enumerate(scenarios, 1):
        result = _process_batch_scenario(scenario, idx, total, reporter)
        results_summary.append(result)

    # Display summary
    _display_batch_summary(results_summary, reporter)
