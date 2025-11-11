"""CLI argument validators for Agency Toolkit commands.

This module provides reusable validation functions for CLI arguments,
including file path validation, enum choices, and numerical ranges.
"""

from pathlib import Path
from typing import Any

import typer

from agency_toolkit.core.reporter import Reporter, get_reporter


class ValidationError(Exception):
    """Raised when CLI argument validation fails."""

    pass


def validate_file_exists(file_path: Path | None, name: str = "file") -> None:
    """Validate that a file path exists and is readable.

    Args:
        file_path: Path to validate (None is allowed)
        name: Name of the argument for error messages

    Raises:
        ValidationError: If file doesn't exist or is not readable

    Example:
        >>> validate_file_exists(Path("config.json"), "config")
    """
    if file_path is None:
        return

    if not file_path.exists():
        raise ValidationError(f"{name} not found: {file_path}")

    if not file_path.is_file():
        raise ValidationError(f"{name} is not a file: {file_path}")

    try:
        with open(file_path):
            pass
    except PermissionError:
        raise ValidationError(f"No read permission for {name}: {file_path}")
    except Exception as e:
        raise ValidationError(f"Cannot read {name}: {file_path} - {e}")


def validate_directory_exists(dir_path: Path | None, name: str = "directory") -> None:
    """Validate that a directory path exists and is accessible.

    Args:
        dir_path: Path to validate (None is allowed)
        name: Name of the argument for error messages

    Raises:
        ValidationError: If directory doesn't exist or is not accessible

    Example:
        >>> validate_directory_exists(Path("output"), "output_dir")
    """
    if dir_path is None:
        return

    if not dir_path.exists():
        raise ValidationError(f"{name} not found: {dir_path}")

    if not dir_path.is_dir():
        raise ValidationError(f"{name} is not a directory: {dir_path}")

    try:
        list(dir_path.iterdir())
    except PermissionError:
        raise ValidationError(f"No read permission for {name}: {dir_path}")
    except Exception as e:
        raise ValidationError(f"Cannot access {name}: {dir_path} - {e}")


def validate_file_extension(
    file_path: Path, allowed_extensions: set[str], name: str = "file"
) -> None:
    """Validate that a file has one of the allowed extensions.

    Args:
        file_path: Path to validate
        allowed_extensions: Set of allowed extensions (e.g., {'.json', '.csv'})
        name: Name of the argument for error messages

    Raises:
        ValidationError: If file extension is not allowed

    Example:
        >>> validate_file_extension(
        ...     Path("data.csv"),
        ...     {'.csv', '.json'},
        ...     "data file"
        ... )
    """
    ext = file_path.suffix.lower()
    if ext not in allowed_extensions:
        allowed_str = ", ".join(sorted(allowed_extensions))
        raise ValidationError(
            f"{name} must have extension in [{allowed_str}], got: {ext}"
        )


def validate_enum_choice(
    value: str, allowed_values: set[str], name: str = "choice"
) -> None:
    """Validate that a value is in the set of allowed choices.

    Args:
        value: Value to validate
        allowed_values: Set of allowed values
        name: Name of the argument for error messages

    Raises:
        ValidationError: If value is not in allowed set

    Example:
        >>> validate_enum_choice("bold", {"bold", "modern", "minimal"}, "style")
    """
    if value not in allowed_values:
        allowed_str = ", ".join(sorted(allowed_values))
        raise ValidationError(f"{name} must be one of [{allowed_str}], got: {value}")


def validate_numerical_range(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    name: str = "value",
) -> None:
    """Validate that a numerical value is within a valid range.

    Args:
        value: Numerical value to validate
        min_value: Minimum allowed value (None = no minimum)
        max_value: Maximum allowed value (None = no maximum)
        name: Name of the argument for error messages

    Raises:
        ValidationError: If value is outside valid range

    Example:
        >>> validate_numerical_range(0.5, min_value=0.0, max_value=2.0, "temperature")
    """
    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be >= {min_value}, got: {value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be <= {max_value}, got: {value}")


def validate_mutually_exclusive(
    *args: Any, arg_names: list[str], name: str = "arguments"
) -> None:
    """Validate that at most one of the provided arguments is non-None.

    Args:
        *args: Arguments to validate
        arg_names: Names of the arguments for error messages
        name: General name for error message

    Raises:
        ValidationError: If more than one argument is provided

    Example:
        >>> validate_mutually_exclusive(
        ...     from_csv, from_json, from_file,
        ...     arg_names=["--from-csv", "--from-json", "--from-file"],
        ...     name="input sources"
        ... )
    """
    provided = sum(1 for arg in args if arg is not None)
    if provided > 1:
        provided_names = [name for name, arg in zip(arg_names, args) if arg is not None]
        raise ValidationError(
            f"Only one of [{', '.join(provided_names)}] can be provided. "
            f"Got: {', '.join(provided_names)}"
        )


def validate_at_least_one(
    *args: Any, arg_names: list[str], name: str = "arguments"
) -> None:
    """Validate that at least one of the provided arguments is non-None.

    Args:
        *args: Arguments to validate
        arg_names: Names of the arguments for error messages
        name: General name for error message

    Raises:
        ValidationError: If all arguments are None

    Example:
        >>> validate_at_least_one(
        ...     prompt, prompt_file, stdin,
        ...     arg_names=["--prompt", "--prompt-file", "--stdin"],
        ...     name="input"
        ... )
    """
    provided = sum(1 for arg in args if arg is not None)
    if provided == 0:
        options = ", ".join(arg_names)
        raise ValidationError(f"Must provide at least one of: {options}")


def validate_non_empty_string(
    value: str | None, name: str = "value", allow_none: bool = False
) -> None:
    """Validate that a string is not empty.

    Args:
        value: String to validate
        name: Name of the argument for error messages
        allow_none: Whether None is allowed

    Raises:
        ValidationError: If string is empty (or None when not allowed)

    Example:
        >>> validate_non_empty_string("hello", "prompt")
    """
    if value is None:
        if not allow_none:
            raise ValidationError(f"{name} cannot be None")
        return

    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} cannot be empty")


def handle_validation_error(
    error: ValidationError, reporter: Reporter | None = None
) -> None:
    """Handle a validation error by reporting it and exiting.

    Args:
        error: The validation error to handle
        reporter: Optional reporter for JSON output (defaults to get_reporter())
    """
    if reporter is None:
        reporter = get_reporter()

    error_message = str(error)

    # Log non-JSON output
    typer.secho(f"✗ Validation Error: {error_message}", fg="red")

    # Log JSON output if enabled
    if reporter.config.json_output:
        import json

        output = {
            "status": "error",
            "type": "validation_error",
            "message": error_message,
        }
        print(json.dumps(output))

    raise typer.Exit(1)
