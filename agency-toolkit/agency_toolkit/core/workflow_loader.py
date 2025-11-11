"""GRAND AGENCY OS Registry Module.

This module provides registry validation and loading functionality for
client archetypes and solution templates.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema

from agency_toolkit.exceptions import ValidationError


def get_registry_path() -> Path:
    """Get the path to the registry seeds directory.

    Returns:
        Path to registry/seeds directory
    """
    # Get the project root (where agency_toolkit package is located)
    toolkit_path = Path(__file__).parent.parent
    registry_path = toolkit_path.parent / "registry" / "seeds"
    return registry_path


def get_workflow_schema() -> dict[str, Any]:
    """Load the workflow schema for validation.

    Returns:
        Workflow schema dictionary

    Raises:
        ValidationError: If schema file cannot be loaded
    """
    toolkit_path = Path(__file__).parent.parent
    schema_file = toolkit_path.parent / "registry" / "workflow_schema.json"

    if not schema_file.exists():
        raise ValidationError(f"Workflow schema not found at {schema_file}")

    try:
        with open(schema_file) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in workflow_schema.json: {e}")


def validate_workflow_json(data: Any, schema: dict[str, Any] | None = None) -> None:
    """Validate workflow JSON data against the schema.

    Args:
        data: JSON data to validate (archetypes or solutions)
        schema: Optional schema to use for validation (defaults to workflow_schema.json)

    Raises:
        ValidationError: If validation fails with detailed error information
    """
    if schema is None:
        schema = get_workflow_schema()

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        # Build a detailed error message
        path = ".".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Invalid workflow JSON at {path}: {e.message}"
        if hasattr(e, "validator_value"):
            error_msg += f" (expected: {e.validator_value})"
        raise ValidationError(error_msg)
    except jsonschema.SchemaError as e:
        raise ValidationError(f"Schema validation error: {e.message}")


def load_archetypes() -> list[dict[str, Any]]:
    """Load archetypes from registry.

    Returns:
        List of archetype definitions

    Raises:
        ValidationError: If archetypes file cannot be loaded or schema validation fails
    """
    registry_path = get_registry_path()
    archetypes_file = registry_path / "archetypes.json"

    if not archetypes_file.exists():
        raise ValidationError(f"Archetypes registry not found at {archetypes_file}")

    try:
        with open(archetypes_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in archetypes.json: {e}")

    # Validate against schema
    validate_workflow_json(data)

    return data


def load_solutions() -> list[dict[str, Any]]:
    """Load solution templates from registry.

    Returns:
        List of solution template definitions

    Raises:
        ValidationError: If solutions file cannot be loaded or schema validation fails
    """
    registry_path = get_registry_path()
    solutions_file = registry_path / "solutions.json"

    if not solutions_file.exists():
        raise ValidationError(f"Solutions registry not found at {solutions_file}")

    try:
        with open(solutions_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in solutions.json: {e}")

    # Validate against schema
    validate_workflow_json(data)

    return data


def validate_registry() -> None:
    """Validate the GRAND AGENCY registry for consistency.

    Performs cross-referential validation:
    - Archetypes must reference existing solution template IDs
    - Solution templates must reference existing archetype IDs
    - Module dependencies must reference existing module IDs

    Raises:
        ValidationError: If validation fails with specific error details
    """
    archetypes = load_archetypes()
    solutions = load_solutions()

    # Build lookup sets
    archetype_ids = {arch["id"] for arch in archetypes}
    solution_ids = {sol["id"] for sol in solutions}
    module_ids = {mod["id"] for sol in solutions for mod in sol.get("modules", [])}

    # Validate archetype -> solution references
    for archetype in archetypes:
        arch_id = archetype["id"]
        for solution_id in archetype.get("solution_template_ids", []):
            if solution_id not in solution_ids:
                raise ValueError(
                    f"Archetype '{arch_id}' references non-existent solution "
                    f"template '{solution_id}'"
                )

    # Validate solution -> archetype references
    for solution in solutions:
        sol_id = solution["id"]
        arch_id = solution.get("archetype_id")
        if arch_id and arch_id not in archetype_ids:
            raise ValueError(
                f"Solution template '{sol_id}' references non-existent "
                f"archetype '{arch_id}'"
            )

        # Validate module dependencies
        for module in solution.get("modules", []):
            mod_id = module["id"]
            for dep_id in module.get("dependencies", []):
                if dep_id not in module_ids:
                    raise ValueError(
                        f"Module '{mod_id}' in solution '{sol_id}' has "
                        f"dependency on non-existent module '{dep_id}'"
                    )
