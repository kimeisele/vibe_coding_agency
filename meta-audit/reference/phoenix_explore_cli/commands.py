"""Explore CLI commands - Click decorators and interface."""

import click

from phoenix_system.cli.error_handler import handle_cli_errors


@click.group()
@handle_cli_errors
def explore():
    """Investigation engine - ask questions about the codebase."""
    pass


@explore.command()
@click.option(
    "--goal", required=True, help="Exploration objective (e.g., 'understand auth flow')"
)
@click.option(
    "--max-iterations",
    default=5,
    type=int,
    help="Maximum exploration steps (default: 5)",
)
@click.option(
    "--json", "output_json", is_flag=True, help="Output JSON instead of markdown"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["default", "clean", "summary"], case_sensitive=False),
    default="default",
    help="Output format: default (markdown), clean (readable), summary (brief)",
)
@click.option(
    "--suggest-next",
    "suggest_next",
    is_flag=True,
    help="Show suggested next actions after exploration",
)
@click.option(
    "--async",
    "async_mode",
    is_flag=True,
    help="Run exploration asynchronously as a background job",
)
@click.option(
    "--llm-provider",
    "llm_provider_name",
    type=str,
    required=False,
    help="LLM provider to use (anthropic, mistral, stub). Defaults to auto-selection.",
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    help="Timeout in seconds for exploration (default: 60s, 0 to disable)",
)
@click.pass_context
@handle_cli_errors
def run(
    ctx,
    goal: str,
    max_iterations: int,
    output_json: bool,
    output_format: str,
    suggest_next: bool,
    async_mode: bool,
    llm_provider_name: str | None,
    timeout: int,
):
    """Run autonomous exploration of the codebase.

    Examples:
      phoenix explore run --goal "understand auth system" --max-iterations 3
      phoenix explore run --goal "find bottlenecks" --format clean
      phoenix explore run --goal "analyze dependencies" --async
    """
    # Check global --json flag as well
    output_json = output_json or getattr(ctx.obj, "json_output", False)

    from .runners import run_exploration

    run_exploration(
        goal=goal,
        max_iterations=max_iterations,
        output_json=output_json,
        output_format=output_format,
        suggest_next=suggest_next,
        async_mode=async_mode,
        llm_provider_name=llm_provider_name,
        timeout=timeout,
    )
