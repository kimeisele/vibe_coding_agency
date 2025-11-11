"""GRAND AGENCY OS Orchestrator.

This module provides robust task execution for solution modules,
with comprehensive error handling, result tracking, and observability features.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

from rich.progress import Progress, SpinnerColumn, TextColumn

from agency_toolkit.tasks import get_task_handler
from agency_toolkit.tasks.base import TaskContext

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Standardized result structure for task execution.

    Attributes:
        tool: Name of the tool/command executed
        success: Whether the task completed successfully
        output: Task output data (can be any type)
        error: Error message if task failed (empty string if success)
    """

    tool: str
    success: bool
    output: Any
    error: str = ""


@dataclass
class WorkflowExecutionReport:
    """Comprehensive report of workflow execution results.

    Provides statistics on task execution including success/failure/skip counts
    and a detailed list of errors encountered during execution.

    Attributes:
        module_id: ID of the executed module
        total_tasks: Total number of tasks in the module
        successful: Number of successfully completed tasks
        failed: Number of failed tasks
        skipped: Number of skipped tasks
        errors: List of error messages encountered
        task_results: List of TaskResult objects for all executed tasks
    """

    module_id: str
    total_tasks: int
    successful: int
    failed: int
    skipped: int
    errors: list[str]
    task_results: list[TaskResult]


def execute_module(
    module: dict[str, Any], context: dict[str, Any], show_progress: bool = True
) -> WorkflowExecutionReport:
    """Execute all tasks in a solution module with inter-task context passing.

    This function loops through each task in the module and executes it,
    calling the appropriate internal core functions. It maintains a step_context
    that allows tasks to reference outputs from previous tasks.

    HYBRID CONTEXT SYSTEM:
    The dual-context design enables both template substitution and structured data passing:

    1. STEP CONTEXT (Formatted for Templates):
       - All values converted to strings for safe template substitution
       - Lists automatically become comma-separated strings: ["a", "b"] → "a, b"
       - Used for {placeholder} substitution in task params
       - Example: params["text"] = "{tagline}" gets "Amazing Solutions" injected
       - Access in handlers: context.get("key")

    2. RAW CONTEXT (Typed for Structured Data):
       - Original data types preserved (lists, dicts, objects)
       - Used when handlers need to iterate or inspect structured data
       - Example: raw_context["taglines"] = ["Amazing", "Innovative", "Professional"]
       - Access in handlers: context.get_raw("key")

    KEY INSIGHT: When a task outputs a list and stores it with output_key="items":
    - step_context["items"] = "Amazing, Innovative, Professional" (string for templates)
    - raw_context["items"] = ["Amazing", "Innovative", "Professional"] (original list)

    WHY THIS MATTERS:
    - Task 1 outputs: ["tag1", "tag2", "tag3"]
    - Task 2 param: "text": "{items}" → Receives "tag1, tag2, tag3" (automatically stringified)
    - Task 3 custom handler needs original list → Use context.get_raw("items")

    OBSERVABILITY:
    - Structured logging for module_started, task_executing, task_completed
    - Rich progress bar showing task execution progress
    - Detailed timing and error information

    ERROR HANDLING:
    - Task-level on_error mode: "stop" (default) or "continue"
    - "stop": Halt workflow on error (used for critical tasks)
    - "continue": Log error, skip task, continue workflow (used for optional tasks)
    - Legacy stop_on_error parameter still supported for backward compatibility

    Args:
        module: Module definition containing tasks to execute
        context: Execution context with variables and configuration
        show_progress: Whether to display progress bar (default: True)

    Returns:
        WorkflowExecutionReport with statistics and detailed results

    Example:
        >>> module = {
        ...     "id": "A1_M4",
        ...     "title": "Social Recruiting",
        ...     "tasks": [
        ...         {
        ...             "tool": "ai",
        ...             "output_key": "taglines",
        ...             "on_error": "continue",
        ...             "params": {"prompt": "Generate 3 taglines as JSON array"}
        ...         },
        ...         {
        ...             "tool": "social",
        ...             "on_error": "stop",
        ...             "params": {"text": "{taglines}"}
        ...         }
        ...     ]
        ... }
        >>> context = {"project_name": "Acme Corp"}
        >>> report = execute_module(module, context)
        >>> print(report.successful, report.failed, report.errors)
    """
    results: list[TaskResult] = []
    errors: list[str] = []
    stop_on_error = context.get("stop_on_error", False)

    # DUAL CONTEXT SYSTEM INITIALIZATION
    # ===================================
    # Step context: accumulates FORMATTED outputs from previous tasks (all stringified)
    # - Used for {placeholder} substitution in subsequent task params
    # - Lists are converted to comma-separated strings for safe template injection
    # - Example: output ["tag1", "tag2"] becomes "tag1, tag2" in step_context
    step_context: dict[str, Any] = {}

    # Raw context: accumulates UNFORMATTED outputs (original types preserved)
    # - Used when handlers need structured data (lists, dicts, etc.)
    # - Lists remain as lists, dicts remain as dicts
    # - Custom handlers access via context.get_raw("key") to get original type
    # - Example: output ["tag1", "tag2"] stays as list in raw_context
    raw_context: dict[str, Any] = {}

    tasks = module.get("tasks", [])
    module_id = module.get("id", "unknown")
    module_title = module.get("title", module_id)

    # Log module start
    logger.info(
        "module_started",
        extra={
            "module_id": module_id,
            "module_title": module_title,
            "task_count": len(tasks),
        },
    )

    # Execute with optional progress bar
    progress_context = (
        Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        if show_progress
        else None
    )

    try:
        if progress_context:
            progress_context.__enter__()
            progress_task = progress_context.add_task(
                f"Executing module {module_id}", total=len(tasks)
            )

        for idx, task in enumerate(tasks):
            tool_name = task.get("tool", "unknown")
            output_key = task.get("output_key")  # Optional: key to store output
            on_error_mode = task.get("on_error", "stop")  # Task-level error handling

            task_start_time = time.time()

            try:
                # Log task execution start
                logger.info(
                    "task_executing",
                    extra={
                        "module_id": module_id,
                        "tool": tool_name,
                        "output_key": output_key,
                        "task_index": idx + 1,
                        "task_count": len(tasks),
                    },
                )

                # Merge contexts into enriched_context for this task
                # This allows {tagline}, {generated_text}, etc. to be resolved
                enriched_context = {**context, **step_context}

                output = _execute_task(tool_name, task, enriched_context, raw_context)
                result = TaskResult(
                    tool=tool_name,
                    success=True,
                    output=output,
                    error="",
                )
                results.append(result)

                task_duration_ms = int((time.time() - task_start_time) * 1000)

                # Log task completion
                logger.info(
                    "task_completed",
                    extra={
                        "module_id": module_id,
                        "tool": tool_name,
                        "output_key": output_key,
                        "duration_ms": task_duration_ms,
                        "success": True,
                    },
                )

                # DUAL CONTEXT STORAGE
                # Store output in both step_context and raw_context if output_key is specified
                if output_key:
                    # Raw context: preserve original type (lists stay lists, etc.)
                    # Used by handlers that call context.get_raw(output_key)
                    raw_context[output_key] = output

                    # Step context: convert to string for template substitution
                    # This makes the output safe to inject into {placeholder} patterns
                    if isinstance(output, list):
                        # Convert lists to comma-separated strings
                        # Example: ["tag1", "tag2", "tag3"] → "tag1, tag2, tag3"
                        # This allows templates like "text": "{output_key}" to work safely
                        step_context[output_key] = ", ".join(str(v) for v in output)
                    else:
                        # Keep non-list types as stringified versions
                        step_context[output_key] = str(output)

                    logger.debug(
                        f"Stored task output: {output_key} = {output} "
                        f"(formatted: {step_context[output_key]})"
                    )

            except Exception as e:
                task_duration_ms = int((time.time() - task_start_time) * 1000)

                # Robust error handling: capture and log the error
                error_msg = f"Error executing {tool_name}: {str(e)}"
                errors.append(error_msg)

                # Determine if we should continue based on:
                # 1. Task-level on_error mode (takes precedence if specified)
                # 2. Legacy stop_on_error context parameter (for backward compatibility)
                should_continue = (on_error_mode == "continue") or (
                    on_error_mode == "stop" and not stop_on_error
                )

                # Log task failure with appropriate level based on error mode
                if should_continue:
                    logger.warning(
                        "task_failed_continuing",
                        extra={
                            "module_id": module_id,
                            "tool": tool_name,
                            "duration_ms": task_duration_ms,
                            "error": error_msg,
                            "on_error_mode": "continue",
                        },
                    )
                else:
                    logger.error(
                        "task_failed",
                        extra={
                            "module_id": module_id,
                            "tool": tool_name,
                            "duration_ms": task_duration_ms,
                            "error": error_msg,
                            "on_error_mode": "stop",
                        },
                        exc_info=True,
                    )

                result = TaskResult(
                    tool=tool_name, success=False, output=None, error=error_msg
                )
                results.append(result)

                # Stop execution if we should stop based on error handling logic
                if not should_continue:
                    break

            # Update progress bar
            if progress_context:
                progress_context.update(progress_task, advance=1)

    finally:
        if progress_context:
            progress_context.__exit__(None, None, None)

    # Calculate final statistics
    success_count = sum(1 for r in results if r.success)
    failed_count = sum(1 for r in results if not r.success)
    skipped_count = len(tasks) - len(results)  # Tasks that weren't executed

    # Log module completion
    logger.info(
        "module_completed",
        extra={
            "module_id": module_id,
            "task_count": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "success": success_count == len(results) and len(results) > 0,
        },
    )

    # Return comprehensive execution report
    return WorkflowExecutionReport(
        module_id=module_id,
        total_tasks=len(tasks),
        successful=success_count,
        failed=failed_count,
        skipped=skipped_count,
        errors=errors,
        task_results=results,
    )


def _format_task_params(
    params: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Format task parameters with dynamic context values.

    This function replaces template placeholders (e.g. {archetype_name}) in
    parameter values with actual context values. Validates that all referenced
    placeholders exist in context before formatting (fail-fast).

    Args:
        params: Task parameters that may contain placeholders
        context: Context dictionary with dynamic values

    Returns:
        New params dict with formatted values

    Raises:
        ValueError: If a placeholder is referenced but not found in context

    Example:
        >>> params = {"text": "Post for {archetype_name}"}
        >>> context = {"archetype_name": "Local Craftsman"}
        >>> result = _format_task_params(params, context)
        >>> result["text"]
        'Post for Local Craftsman'
    """
    import string

    # Extract all placeholders from parameters
    formatter = string.Formatter()
    referenced_placeholders = set()

    def collect_placeholders(value):
        """Recursively collect all placeholders in a value."""
        if isinstance(value, str):
            for _, field_name, _, _ in formatter.parse(value):
                if field_name:
                    # Get base field name (ignore nested attributes)
                    base_field = field_name.split(".")[0].split("[")[0]
                    if base_field:
                        referenced_placeholders.add(base_field)
        elif isinstance(value, list):
            for item in value:
                collect_placeholders(item)
        elif isinstance(value, dict):
            for v in value.values():
                collect_placeholders(v)

    # Collect all placeholders from params
    for value in params.values():
        collect_placeholders(value)

    # Validate all referenced placeholders exist in context (fail-fast)
    available_keys = set(context.keys())
    missing_placeholders = referenced_placeholders - available_keys
    if missing_placeholders:
        raise ValueError(
            f"Task references undefined placeholders: {', '.join(sorted(missing_placeholders))}. "
            f"Available context: {', '.join(sorted(available_keys))}"
        )

    # Create safe context with string representations
    safe_context = {}
    for key, value in context.items():
        if isinstance(value, list):
            # Convert lists to comma-separated strings
            safe_context[key] = ", ".join(str(v) for v in value)
        else:
            safe_context[key] = str(value)

    # Format each parameter value
    formatted_params = {}
    for key, value in params.items():
        if isinstance(value, str):
            try:
                # Use format_map with safe_context for safe formatting
                formatted_params[key] = value.format_map(safe_context)
            except (KeyError, ValueError):
                # If formatting fails, keep original value
                formatted_params[key] = value
        elif isinstance(value, list):
            # Format list items
            formatted_params[key] = [
                item.format_map(safe_context) if isinstance(item, str) else item
                for item in value
            ]
        else:
            # Keep non-string values as-is
            formatted_params[key] = value

    return formatted_params


def _execute_task(
    tool_name: str,
    task: dict[str, Any],
    context: dict[str, Any],
    raw_context: dict[str, Any],
) -> Any:
    """Execute a single task by delegating to the appropriate handler.

    Uses the task handler registry to dynamically dispatch tasks to their handlers.
    This eliminates the if/elif bottleneck and makes adding new tools trivial.

    Args:
        tool_name: Name of the tool to execute
        task: Task definition with params
        context: Execution context (dict with config, step_context, etc.)
        raw_context: Unformatted context with original types (lists, dicts)

    Returns:
        Task execution result (format depends on tool)

    Raises:
        ValueError: If tool_name is not registered or params are invalid
    """
    # Get handler from registry (raises ValueError if not found)
    handler = get_task_handler(tool_name)

    # Apply dynamic prompt formatting if params exist
    params = task.get("params", {})
    params = _format_task_params(params, context)

    # Create typed TaskContext with both formatted and raw contexts
    task_context = TaskContext(
        config=context.get("config"),
        step_context=context,  # Full context for get() method (backwards compatible, stringified)
        raw_context=raw_context,  # Unformatted context for get_raw() method (typed data)
        archetype_id=context.get("archetype_id"),
        solution_id=context.get("solution_id"),
        project_name=context.get("project_name"),
        ai_provider=context.get("ai_provider"),
    )

    # Validate and execute
    logger.debug(
        f"Executing {tool_name} task with handler: {handler.__class__.__name__}"
    )
    handler.validate_params(params)
    return handler.execute(params=params, context=task_context)
