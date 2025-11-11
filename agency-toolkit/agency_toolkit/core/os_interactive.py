"""Interactive workflow prompts for GRAND AGENCY OS.

This module contains the interactive user prompts and UI logic,
extracted from commands/os.py to reduce complexity.
"""

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from agency_toolkit.core.dependency_resolver import resolve_module_dependencies
from agency_toolkit.core.interactive_utils import prompt_for_selection
from agency_toolkit.core.os_executor import (
    build_execution_context,
    build_execution_summary,
    execute_workflow_modules,
)
from agency_toolkit.core.workflow_loader import load_archetypes, load_solutions

console = Console()


def select_archetype() -> dict[str, Any]:
    """Prompt user to select a client archetype.

    Returns:
        Selected archetype dictionary
    """
    console.print("[bold]Step 1:[/bold] Select Client Archetype\n")
    archetypes = load_archetypes()

    selected = prompt_for_selection(
        "Choose the client archetype:",
        choices=archetypes,
        id_key="id",
        name_key="name",
        description_key="description",
    )

    console.print(
        f"\n[green]✓[/green] Selected: {selected['name']} " f"(ID: {selected['id']})\n"
    )

    return selected


def select_solution(archetype_id: str) -> dict[str, Any]:
    """Prompt user to select a solution for the given archetype.

    Args:
        archetype_id: ID of the selected archetype

    Returns:
        Selected solution dictionary

    Raises:
        typer.Exit: If no solutions found for archetype
    """
    console.print("[bold]Step 2:[/bold] Select Solution Template\n")
    solutions = load_solutions()
    filtered_solutions = [s for s in solutions if s["archetype_id"] == archetype_id]

    if not filtered_solutions:
        console.print(f"[red]No solutions found for archetype {archetype_id}[/red]")
        raise typer.Exit(code=1)

    selected = prompt_for_selection(
        "Choose the solution template:",
        choices=filtered_solutions,
        id_key="id",
        name_key="name",
        description_key="description",
    )

    console.print(
        f"\n[green]✓[/green] Selected: {selected['name']} " f"(ID: {selected['id']})\n"
    )

    return selected


def select_module(solution: dict[str, Any]) -> dict[str, Any]:
    """Prompt user to select a module from the solution.

    Args:
        solution: Solution dictionary containing modules

    Returns:
        Selected module dictionary

    Raises:
        typer.Exit: If no modules found in solution
    """
    console.print("[bold]Step 3:[/bold] Select Module to Execute\n")
    modules = solution.get("modules", [])

    if not modules:
        console.print(f"[red]No modules found in solution {solution['id']}[/red]")
        raise typer.Exit(code=1)

    selected = prompt_for_selection(
        "Choose a module to execute:",
        choices=modules,
        id_key="id",
        name_key="title",
        description_key="description",
    )

    console.print(
        f"\n[green]✓[/green] Selected: {selected['title']} " f"(ID: {selected['id']})\n"
    )

    return selected


def resolve_and_display_dependencies(
    module: dict[str, Any], solution: dict[str, Any]
) -> list[dict[str, Any]]:
    """Resolve module dependencies and display them to user.

    Args:
        module: Selected module
        solution: Solution containing the module

    Returns:
        List of modules to execute (including dependencies)

    Raises:
        typer.Exit: If dependency resolution fails
    """
    console.print("[bold]Step 4:[/bold] Resolving Dependencies\n")

    try:
        modules_to_execute = resolve_module_dependencies(module, solution)

        if len(modules_to_execute) > 1:
            console.print(
                f"[yellow]ℹ[/yellow] Module has dependencies. "
                f"Will execute {len(modules_to_execute)} modules in order:"
            )
            for i, mod in enumerate(modules_to_execute, 1):
                console.print(f"  {i}. {mod['title']} ({mod['id']})")
            console.print()
        else:
            console.print(
                "[green]✓[/green] No dependencies. Executing single module.\n"
            )

        return modules_to_execute

    except Exception as e:
        console.print(f"[red]Dependency resolution failed: {e}[/red]")
        raise typer.Exit(code=1)


def display_execution_progress(
    project_name: str, modules_to_execute: list[dict[str, Any]]
) -> None:
    """Display execution progress header.

    Args:
        project_name: Name of the project
        modules_to_execute: List of modules to execute
    """
    console.print("[bold]Step 5:[/bold] Executing Workflow\n")
    console.print(f"[cyan]Project:[/cyan] {project_name}")
    console.print(f"[cyan]Modules:[/cyan] {len(modules_to_execute)}\n")
    console.print("[dim]Starting execution...[/dim]\n")


def display_execution_results(summary: dict[str, Any]) -> None:
    """Display execution results in a formatted table.

    Args:
        summary: Execution summary dictionary
    """
    console.print("\n[bold]Execution Summary:[/bold]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Project", summary["project_name"])
    table.add_row("Modules Executed", str(summary["modules_executed"]))
    table.add_row("Total Tasks", str(summary["tasks_total"]))
    table.add_row("Successful", f"[green]{summary['tasks_success']}[/green]")
    table.add_row("Failed", f"[red]{summary['tasks_failed']}[/red]")

    status = "[green]✓ SUCCESS[/green]" if summary["success"] else "[red]✗ FAILED[/red]"
    table.add_row("Status", status)

    console.print(table)
    console.print()


def run_interactive_workflow(
    project_name: str,
    ai_provider: str | None = None,
    stop_on_error: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute complete interactive workflow with user prompts.

    This orchestrates the entire interactive flow:
    1. Select archetype
    2. Select solution
    3. Select module
    4. Resolve dependencies
    5. Execute workflow (or show plan if dry_run=True)
    6. Display results

    Args:
        project_name: Name of the project
        ai_provider: Optional AI provider override
        stop_on_error: Whether to stop on first error
        dry_run: If True, show execution plan without running tasks

    Returns:
        Execution summary dictionary
    """
    # Step 1: Select archetype
    archetype = select_archetype()

    # Step 2: Select solution
    solution = select_solution(archetype["id"])

    # Step 3: Select module
    module = select_module(solution)

    # Step 4: Resolve dependencies
    modules_to_execute = resolve_and_display_dependencies(module, solution)

    # Dry-run mode: Show plan and exit
    if dry_run:
        display_dry_run_plan(project_name, archetype, solution, modules_to_execute)
        return {
            "project_name": project_name,
            "archetype_id": archetype["id"],
            "solution_id": solution["id"],
            "module_id": module["id"],
            "modules_executed": 0,
            "tasks_total": 0,
            "tasks_success": 0,
            "tasks_failed": 0,
            "success": True,
            "results": [],
            "dry_run": True,
        }

    # Step 5: Execute workflow
    display_execution_progress(project_name, modules_to_execute)

    context = build_execution_context(
        project_name, archetype, solution, ai_provider, stop_on_error
    )
    all_results = execute_workflow_modules(modules_to_execute, context)

    summary = build_execution_summary(
        project_name,
        archetype["id"],
        solution["id"],
        module["id"],
        modules_to_execute,
        all_results,
    )

    # Step 6: Display results
    display_execution_results(summary)

    return summary


def display_dry_run_plan(
    project_name: str,
    archetype: dict[str, Any],
    solution: dict[str, Any],
    modules_to_execute: list[dict[str, Any]],
) -> None:
    """Display execution plan in dry-run mode.

    Args:
        project_name: Name of the project
        archetype: Selected archetype
        solution: Selected solution
        modules_to_execute: List of modules that would be executed
    """
    console.print("\n[bold yellow]🔍 DRY-RUN MODE - Execution Plan[/bold yellow]\n")

    # Project info
    console.print(f"[cyan]Project:[/cyan] {project_name}")
    console.print(f"[cyan]Archetype:[/cyan] {archetype['name']} ({archetype['id']})")
    console.print(f"[cyan]Solution:[/cyan] {solution['name']} ({solution['id']})")
    console.print()

    # Modules and tasks
    console.print(f"[bold]Would execute {len(modules_to_execute)} module(s):[/bold]\n")

    task_count = 0
    for idx, mod in enumerate(modules_to_execute, 1):
        console.print(f"[bold]{idx}. {mod['title']}[/bold] ({mod['id']})")

        # Show tasks for this module
        tasks = mod.get("tasks", [])
        for task in tasks:
            task_count += 1
            tool = task.get("tool", "unknown")
            description = task.get("description", "No description")
            console.print(f"   • [dim]{tool}:[/dim] {description}")

        console.print()

    console.print(
        f"[bold]Total:[/bold] {task_count} task(s) across {len(modules_to_execute)} module(s)\n"
    )

    console.print(
        "[yellow]ℹ  This is a dry-run. No files will be created or modified.[/yellow]"
    )
    console.print("[dim]Run without --dry-run to execute the workflow.[/dim]\n")
