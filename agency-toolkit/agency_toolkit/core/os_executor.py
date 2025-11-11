"""Core execution logic for GRAND AGENCY OS workflows.

This module contains the business logic for workflow execution,
extracted from commands/os.py to reduce complexity.
"""

from typing import Any

from agency_toolkit.core.dependency_resolver import resolve_module_dependencies
from agency_toolkit.core.orchestrator import execute_module
from agency_toolkit.core.workflow_loader import (
    load_archetypes,
    load_solutions,
)
from agency_toolkit.utils import load_config


def find_archetype(archetype_id: str) -> dict[str, Any]:
    """Find archetype by ID.

    Args:
        archetype_id: Archetype ID to find

    Returns:
        Archetype dictionary

    Raises:
        ValueError: If archetype not found
    """
    archetypes = load_archetypes()
    archetype = next((a for a in archetypes if a["id"] == archetype_id), None)
    if not archetype:
        available = ", ".join(a["id"] for a in archetypes)
        raise ValueError(
            f"Invalid archetype_id: {archetype_id}. Available: {available}"
        )
    return archetype


def find_solution(solution_id: str, archetype_id: str | None = None) -> dict[str, Any]:
    """Find solution by ID and optionally validate archetype match.

    Args:
        solution_id: Solution ID to find
        archetype_id: Optional archetype ID to validate against

    Returns:
        Solution dictionary

    Raises:
        ValueError: If solution not found or doesn't match archetype
    """
    solutions = load_solutions()
    solution = next((s for s in solutions if s["id"] == solution_id), None)
    if not solution:
        available = ", ".join(s["id"] for s in solutions)
        raise ValueError(f"Invalid solution_id: {solution_id}. Available: {available}")

    # Verify solution matches archetype if provided
    if archetype_id and solution["archetype_id"] != archetype_id:
        raise ValueError(
            f"Solution {solution_id} does not belong to archetype {archetype_id}. "
            f"Expected archetype: {solution['archetype_id']}"
        )

    return solution


def find_module(module_id: str, solution: dict[str, Any]) -> dict[str, Any]:
    """Find module by ID within a solution.

    Args:
        module_id: Module ID to find
        solution: Solution dictionary containing modules

    Returns:
        Module dictionary

    Raises:
        ValueError: If module not found in solution
    """
    modules = solution.get("modules", [])
    module = next((m for m in modules if m["id"] == module_id), None)
    if not module:
        available = ", ".join(m["id"] for m in modules)
        raise ValueError(
            f"Invalid module_id: {module_id}. "
            f"Available in {solution['id']}: {available}"
        )
    return module


def build_execution_context(
    project_name: str,
    archetype: dict[str, Any],
    solution: dict[str, Any],
    ai_provider: str | None = None,
    stop_on_error: bool = True,
) -> dict[str, Any]:
    """Build execution context for workflow.

    Args:
        project_name: Name of the project
        archetype: Archetype dictionary
        solution: Solution dictionary
        ai_provider: Optional AI provider override
        stop_on_error: Whether to stop on first error

    Returns:
        Context dictionary for execution
    """
    config = load_config()
    context = {
        "project_name": project_name,
        "project_name_safe": project_name.replace("_", " "),
        "archetype_id": archetype["id"],
        "archetype_name": archetype["name"],
        "solution_id": solution["id"],
        "solution_name": solution["name"],
        "pain_points": archetype.get("pains", []),
        "goals": archetype.get("goals", []),
        "stop_on_error": stop_on_error,
        "config": config,
    }

    if ai_provider:
        context["ai_provider"] = ai_provider

    return context


def execute_workflow_modules(
    modules_to_execute: list[dict[str, Any]],
    context: dict[str, Any],
) -> list[Any]:
    """Execute workflow modules with context.

    Args:
        modules_to_execute: List of modules to execute
        context: Execution context

    Returns:
        List of execution results
    """
    all_results = []
    stop_on_error = context.get("stop_on_error", True)

    for module_to_exec in modules_to_execute:
        report = execute_module(module_to_exec, context)
        # Extract task results from WorkflowExecutionReport
        all_results.extend(report.task_results)

        # Check if module had failures and stop_on_error is True
        module_failed = report.failed > 0
        if module_failed and stop_on_error:
            break

    return all_results


def build_execution_summary(
    project_name: str,
    archetype_id: str,
    solution_id: str,
    module_id: str,
    modules_to_execute: list[dict[str, Any]],
    all_results: list[Any],
) -> dict[str, Any]:
    """Build execution summary from results.

    Args:
        project_name: Name of the project
        archetype_id: Archetype ID
        solution_id: Solution ID
        module_id: Module ID
        modules_to_execute: List of executed modules
        all_results: All execution results

    Returns:
        Summary dictionary
    """
    success_count = sum(1 for r in all_results if r.success)
    total_count = len(all_results)

    return {
        "project_name": project_name,
        "archetype_id": archetype_id,
        "solution_id": solution_id,
        "module_id": module_id,
        "modules_executed": len(modules_to_execute),
        "tasks_total": total_count,
        "tasks_success": success_count,
        "tasks_failed": total_count - success_count,
        "success": success_count == total_count and total_count > 0,
        "results": all_results,
    }


def execute_project_workflow(
    project_name: str,
    archetype_id: str,
    solution_id: str,
    module_id: str,
    ai_provider: str | None = None,
    stop_on_error: bool = True,
) -> dict[str, Any]:
    """Execute a complete project workflow (orchestrated).

    This is the main entry point that coordinates all workflow steps:
    1. Find and validate archetype, solution, and module
    2. Resolve dependencies
    3. Build execution context
    4. Execute all modules
    5. Build and return summary

    Args:
        project_name: Name of the project
        archetype_id: Client archetype ID
        solution_id: Solution template ID
        module_id: Module to execute
        ai_provider: Optional AI provider override
        stop_on_error: Whether to stop on first error

    Returns:
        Execution summary with results

    Raises:
        ValueError: If IDs are invalid
        Exception: If execution fails critically
    """
    # Step 1: Find and validate
    archetype = find_archetype(archetype_id)
    solution = find_solution(solution_id, archetype_id)
    module = find_module(module_id, solution)

    # Step 2: Resolve dependencies
    modules_to_execute = resolve_module_dependencies(module, solution)

    # Step 3: Build context
    context = build_execution_context(
        project_name, archetype, solution, ai_provider, stop_on_error
    )

    # Step 4: Execute modules
    all_results = execute_workflow_modules(modules_to_execute, context)

    # Step 5: Build summary
    return build_execution_summary(
        project_name,
        archetype_id,
        solution_id,
        module_id,
        modules_to_execute,
        all_results,
    )
