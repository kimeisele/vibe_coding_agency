"""Dependency resolution for GRAND AGENCY OS modules.

This module provides functionality to resolve module dependencies
and create ordered execution lists.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""

    pass


def resolve_module_dependencies(
    selected_module: dict[str, Any], solution: dict[str, Any]
) -> list[dict[str, Any]]:
    """Resolve module dependencies and return ordered execution list.

    This function performs a topological sort on module dependencies to determine
    the correct execution order. If module C depends on A and B, the returned
    list will be [A, B, C].

    Args:
        selected_module: The module selected by the user
        solution: The complete solution containing all modules

    Returns:
        List of modules in execution order (dependencies first)

    Raises:
        CircularDependencyError: If circular dependencies are detected
        ValueError: If a dependency references a non-existent module

    Example:
        >>> solution = {
        ...     "modules": [
        ...         {"id": "M1", "dependencies": []},
        ...         {"id": "M2", "dependencies": ["M1"]},
        ...         {"id": "M3", "dependencies": ["M1", "M2"]}
        ...     ]
        ... }
        >>> selected = solution["modules"][2]  # M3
        >>> result = resolve_module_dependencies(selected, solution)
        >>> [m["id"] for m in result]
        ['M1', 'M2', 'M3']
    """
    # Build module lookup dictionary
    modules_by_id = {mod["id"]: mod for mod in solution.get("modules", [])}

    # Track visited modules to detect circular dependencies
    visited = set()
    visiting = set()
    result = []

    def visit(module_id: str) -> None:
        """Recursively visit module and its dependencies (DFS).

        Args:
            module_id: ID of the module to visit

        Raises:
            CircularDependencyError: If circular dependency detected
            ValueError: If module ID not found
        """
        if module_id in visiting:
            raise CircularDependencyError(
                f"Circular dependency detected involving module {module_id}"
            )

        if module_id in visited:
            return

        if module_id not in modules_by_id:
            raise ValueError(
                f"Module {module_id} not found in solution {solution.get('id', 'unknown')}"
            )

        visiting.add(module_id)
        module = modules_by_id[module_id]

        # Visit all dependencies first
        for dep_id in module.get("dependencies", []):
            visit(dep_id)

        visiting.remove(module_id)
        visited.add(module_id)
        result.append(module)

    # Start resolution from selected module
    selected_id = selected_module["id"]
    visit(selected_id)

    logger.info(
        f"Resolved dependencies for {selected_id}: " f"{[m['id'] for m in result]}"
    )

    return result
