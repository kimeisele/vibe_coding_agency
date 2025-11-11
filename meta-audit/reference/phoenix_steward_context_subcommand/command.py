# ARCH-EXEMPT: CLI group needs subprocess for git commands
"""STEWARD context command - Instant agent context overview.

THE command agents need: shows full context in < 3 seconds.
"""

import logging
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel

# PERFORMANCE: Lazy imports - don't load DB until command runs
# from ...db import create_tables, get_steward_session  # Moved to function body


# Make get_steward_session available for tests (will be imported when needed)
def get_steward_session():
    """Placeholder for tests - actual import happens in context function."""
    from ...db import get_steward_session as _get_steward_session

    return _get_steward_session


from .displays import display_context
from .formats import (
    display_compact_context,
    display_filtered_context,
    display_suggested_commands,
    display_summary_context,
)
from .generators import (
    detect_priority_blockers,
    get_active_wu,
    get_blockers,
    get_git_reality,
    get_last_session_age,
    get_system_health,
    get_technical_debt,
)
from .rag_integration import get_action_recommendations, get_context_aware_knowledge
from .utils import output_context_json


from phoenix_system.cli.error_handler import handle_cli_errors


def get_scheduler_status(db_session) -> dict[str, Any] | None:
    """Get scheduler status information."""
    try:
        from sqlalchemy import select

        from phoenix_system.jobs import get_scheduler
        from phoenix_system.state_machine.cli_service import cli_get_scheduled_job_model

        scheduler = get_scheduler()
        stats = scheduler.get_stats(db_session)

        ScheduledJob = cli_get_scheduled_job_model()
        stmt = select(ScheduledJob)
        db_session.execute(stmt).scalars().all()

        return {
            "running": stats.get("running", False),
            "check_interval": stats.get("check_interval", 0),
            "total_schedules": stats.get("total_schedules", 0),
            "enabled_schedules": stats.get("enabled_schedules", 0),
            "disabled_schedules": stats.get("disabled_schedules", 0),
            "schedules_due_now": stats.get("schedules_due_now", 0),
        }
    except Exception as e:
        logger.debug(f"Failed to get scheduler status: {e}")
        return None


console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output full context as JSON (for Knowledge Graph ingestion)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["default", "summary", "compact"], case_sensitive=False),
    default="default",
    help="Output format: default (full), summary (brief), compact (minimal)",
)
@click.option(
    "--filter",
    "filter_view",
    type=click.Choice(["health", "work-units", "git"], case_sensitive=False),
    help="Show only specific section: health, work-units, or git",
)
@click.option(
    "--suggest-commands",
    "suggest_commands",
    is_flag=True,
    help="Show suggested next commands based on context",
)
@click.option(
    "--skip-rag",
    is_flag=True,
    help="Skip RAG knowledge retrieval (faster, less context)",
)
@click.option(
    "--with-blockers",
    "include_blockers",
    is_flag=True,
    help="Include work unit blocker analysis (adds ~7s)",
)
@click.pass_context
@handle_cli_errors
def context(
    ctx: click.Context,
    output_json: bool = False,
    output_format: str = "default",
    filter_view: str | None = None,
    suggest_commands: bool = False,
    skip_rag: bool = False,
    include_blockers: bool = False,
):
    """Show system context overview for agent decision making.

    Examples:
        phoenix steward context                          # Full context
        phoenix steward context --json                   # JSON format
        phoenix steward context --format summary         # Brief summary
        phoenix steward context --filter health          # Health only
        phoenix steward context --suggest-commands       # With suggestions
        phoenix steward context --with-blockers          # Include blockers
    """
    from concurrent.futures import ThreadPoolExecutor

    # PERFORMANCE: Lazy import DB - only load when command runs
    from ...db import create_tables, get_steward_session

    # Check global --json flag as well
    output_json = output_json or getattr(ctx.obj, "json_output", False)

    try:
        create_tables()
        with get_steward_session() as db_session:
            # Parallelize all collectors
            with ThreadPoolExecutor(max_workers=5) as executor:
                git_future = executor.submit(get_git_reality)
                active_wu_future = executor.submit(get_active_wu, db_session)
                health_future = executor.submit(get_system_health)
                tech_debt_future = executor.submit(get_technical_debt)
                session_age_future = executor.submit(get_last_session_age, db_session)
                blockers_future = executor.submit(
                    get_blockers, skip=not include_blockers
                )
                scheduler_future = executor.submit(get_scheduler_status, db_session)

                # Collect results
                git_reality = git_future.result()
                active_wu = active_wu_future.result()
                system_health = health_future.result()
                tech_debt = tech_debt_future.result()
                last_session_age = session_age_future.result()
                work_unit_blockers = blockers_future.result()
                worker_health = scheduler_future.result()

            priority_blockers = detect_priority_blockers(
                work_unit_blockers, git_reality, system_health
            )

            rag_knowledge = None
            action_recommendations = None
            if not skip_rag:
                rag_knowledge = get_context_aware_knowledge(
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    priority_blockers=priority_blockers,
                )
                action_recommendations = get_action_recommendations(
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    priority_blockers=priority_blockers,
                )

            if output_json:
                output_context_json(
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    tech_debt=tech_debt,
                    priority_blockers=priority_blockers,
                    last_session_age=last_session_age,
                    rag_knowledge=rag_knowledge,
                    action_recommendations=action_recommendations,
                    worker_health=worker_health,
                )
            elif filter_view:
                display_filtered_context(
                    filter_view=filter_view,
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    work_unit_blockers=work_unit_blockers,
                    worker_health=worker_health,
                )
            elif output_format == "summary":
                display_summary_context(
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    priority_blockers=priority_blockers,
                    worker_health=worker_health,
                )
            elif output_format == "compact":
                display_compact_context(
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                )
            else:
                display_context(
                    ctx,
                    git_reality=git_reality,
                    active_wu=active_wu,
                    system_health=system_health,
                    tech_debt=tech_debt,
                    priority_blockers=priority_blockers,
                    rag_knowledge=rag_knowledge,
                    action_recommendations=action_recommendations,
                    worker_health=worker_health,
                    work_unit_blockers=work_unit_blockers,
                )

            if suggest_commands:
                display_suggested_commands(
                    action_recommendations=action_recommendations,
                    rag_knowledge=rag_knowledge,
                    active_wu=active_wu,
                )

    except Exception as e:
        console.print(
            Panel(
                f"[red]❌ Error retrieving context: {e}[/red]\n\n"
                f"[dim]Check database connection and try again.[/dim]",
                title="⚠️  Error",
                border_style="red",
            )
        )
        logger.error(f"Context command failed: {e}", exc_info=True)
        raise click.Abort() from e
