"""Display functions for the steward context command."""

from typing import Any, Dict, List

import click
from rich.console import Console
from rich.panel import Panel

from phoenix_system.cli.utils.output.utils import print_guided_footer

from .formatters import (
    format_agent_toolbox,
    format_git_reality,
    format_next_actions,
    format_priority_blockers,
    format_scheduler_status,
    format_system_health,
    format_technical_debt,
)


console = Console()


def _format_status(status: str) -> str:
    """Format work unit status with color."""
    status_colors = {
        "IN_PROGRESS": "[bold green]IN_PROGRESS[/bold green]",
        "REVIEW": "[bold yellow]REVIEW[/bold yellow]",
        "COMPLETED": "[bold blue]COMPLETED[/bold blue]",
        "BLOCKED": "[bold red]BLOCKED[/bold red]",
        "PROPOSED": "[yellow]PROPOSED[/yellow]",
    }
    return status_colors.get(status, status)


def display_context(
    ctx: click.Context,
    git_reality: Dict[str, Any] | None,
    active_wu: Dict[str, Any] | None,
    system_health: Dict[str, Any] | None,
    scheduler_status: Dict[str, Any] | None = None,
    tech_debt: Dict[str, Any] | None = None,
    priority_blockers: Dict[str, List[str]] | None = None,
    last_session_age: str = "",
    work_unit_blockers: List[Dict[str, Any]] | None = None,
    rag_knowledge: List[Dict[str, Any]] | None = None,
    action_recommendations: List[Dict[str, Any]] | None = None,
    worker_health: Dict[str, Any] | None = None,
    rag_status: Dict[str, Any] | None = None,
) -> None:
    """Display the complete context to the terminal."""
    # --- Display Header ---
    header_text = "[bold]PHOENIX STEWARD CONTEXT[/bold]"
    if last_session_age:
        header_text += f"\n[dim]Last session: {last_session_age}[/dim]"

    console.print(
        Panel(
            header_text,
            border_style="cyan",
            expand=False,
        )
    )
    console.print()

    # --- Git Reality ---
    if git_reality:
        lines = format_git_reality(git_reality)
        for line in lines:
            console.print(line)

    # --- Active Work ---
    if active_wu:
        from rich.table import Table

        from .wu_collectors import get_next_commands, get_wu_metrics

        metrics = get_wu_metrics(active_wu.get("id", "UNKNOWN"))
        next_commands = get_next_commands(active_wu.get("status", "UNKNOWN"))

        # Build Active Work table
        wu_table = Table(title="📊 Active Work", show_header=False)
        wu_table.add_column("", style="dim")
        wu_table.add_column("", style="white")

        wu_table.add_row("ID", f"[cyan]{active_wu.get('id', 'N/A')}[/cyan]")
        wu_table.add_row("Title", active_wu.get("title", "N/A"))
        wu_table.add_row("Status", _format_status(active_wu.get("status", "UNKNOWN")))
        wu_table.add_row("Last Update", active_wu.get("last_update", "N/A"))
        wu_table.add_row("", "")  # Spacer

        # Metrics row
        wu_table.add_row("[bold]Metrics[/bold]", "")
        wu_table.add_row("  Tests", f"{metrics['test_count']} total")
        wu_table.add_row(
            "  Complexity",
            f"{metrics['complexity_score']} ({metrics['complexity_level']})",
        )
        wu_table.add_row("  Lines of Code", f"{metrics['lines_of_code']:,}")
        wu_table.add_row("", "")  # Spacer

        # Next commands row
        wu_table.add_row("[bold]💡 Next Commands[/bold]", "")
        for cmd in next_commands:
            wu_table.add_row("  ", f"[yellow]{cmd}[/yellow]")

        console.print(wu_table)
    else:
        console.print(
            Panel(
                "[dim]No active work unit set.\n"
                "Run: [cyan]phoenix work-unit show <WU-ID>[/cyan]\n"
                "Then: [cyan]phoenix steward start[/cyan][/dim]",
                title="📊 Active Work",
                border_style="dim",
            )
        )

    # --- Priority Blockers ---
    lines = format_priority_blockers(priority_blockers)
    for line in lines:
        console.print(line)

    # --- System Health ---
    if system_health:
        lines = format_system_health(system_health)
        for line in lines:
            console.print(line)

    # --- Background Worker Status (NEW!) ---
    if worker_health:
        _display_worker_health(worker_health)

    # --- RAG Status (Health Check) ---
    if rag_status:
        _display_rag_health_warning(rag_status)

    # --- Scheduler Status ---
    if scheduler_status:
        lines = format_scheduler_status(scheduler_status)
        for line in lines:
            console.print(line)

    # --- Technical Debt ---
    if tech_debt:
        lines = format_technical_debt(tech_debt)
        for line in lines:
            console.print(line)

    # --- RAG Knowledge (Context-Aware Knowledge Snippets) ---
    if rag_knowledge:
        _display_rag_knowledge(rag_knowledge)

    # --- Action Recommendations (Proactive Next Steps) ---
    if action_recommendations:
        _display_action_recommendations(action_recommendations)

    # --- Agent Toolbox ---
    lines = format_agent_toolbox()
    for line in lines:
        console.print(line)

    # --- Recommended Actions ---
    format_next_actions(priority_blockers, git_reality, active_wu)

    print_guided_footer(ctx)


def _display_worker_health(worker_health: Dict[str, Any]) -> None:
    """Display background worker health status."""
    status = worker_health.get("status", "UNKNOWN")

    if status == "STOPPED":
        console.print("🔴 [bold red]Background Worker[/bold red]")
        console.print("   ├─ Status: STOPPED")
        console.print("   ├─ ⚠️  [yellow]Jobs will not be processed[/yellow]")
        console.print(
            f"   └─ ▶️  Start with: [cyan]{worker_health.get('action')}[/cyan]"
        )
        console.print()
        return

    if status == "STALE":
        console.print("🟡 [bold yellow]Background Worker[/bold yellow]")
        console.print(f"   ├─ Status: STALE (PID: {worker_health.get('pid')})")
        console.print(f"   ├─ ⚠️  {worker_health.get('warning')}")
        console.print(
            f"   └─ 🔄 Restart with: [cyan]{worker_health.get('action')}[/cyan]"
        )
        console.print()
        return

    if status == "ERROR":
        console.print("🔴 [bold red]Background Worker[/bold red]")
        console.print(
            f"   ├─ Status: ERROR (PID: {worker_health.get('pid', 'unknown')})"
        )
        console.print(f"   └─ ❌ {worker_health.get('error')}")
        console.print()
        return

    if status == "RUNNING":
        uptime = worker_health.get("uptime_seconds", 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        jobs_processed = worker_health.get("jobs_processed", 0)
        jobs_failed = worker_health.get("jobs_failed", 0)
        success_rate = worker_health.get("success_rate", 0)

        console.print("✅ [bold green]Background Worker[/bold green]")
        console.print(f"   ├─ Status: RUNNING (PID: {worker_health.get('pid')})")
        console.print(f"   ├─ Uptime: {hours}h {minutes}m")
        console.print(
            f"   ├─ Jobs: {jobs_processed} processed, {jobs_failed} failed ({success_rate:.1%} success)"
        )
        console.print(f"   ├─ Memory: {worker_health.get('memory_mb', 0):.1f}MB")
        console.print(f"   ├─ CPU: {worker_health.get('cpu_percent', 0):.1f}%")
        console.print(f"   └─ Threads: {worker_health.get('num_threads', 0)}")
        console.print()


def _display_rag_health_warning(rag_health: Dict[str, Any]) -> None:
    """Display RAG health warning if not healthy."""
    status = rag_health.get("status", "unknown")

    if status == "empty":
        console.print("\n[yellow]⚠️  Knowledge Base Empty[/yellow]")
        console.print(f"   └─ {rag_health.get('message')}\n")
    elif status == "partial":
        console.print("\n[yellow]⚠️  Incomplete Index[/yellow]")
        console.print(f"   └─ {rag_health.get('message')}\n")
    elif status == "error":
        console.print("\n[red]❌ RAG Unavailable[/red]")
        console.print(f"   └─ {rag_health.get('message')}\n")


def _display_rag_knowledge(rag_knowledge: List[Dict[str, Any]]) -> None:
    """Display context-aware knowledge snippets from RAG."""
    if not rag_knowledge:
        return

    console.print()
    from rich.table import Table

    knowledge_table = Table(title="📚 Relevant Knowledge (from RAG)", show_header=True)
    knowledge_table.add_column("Section", style="cyan", width=20)
    knowledge_table.add_column("Snippet", width=50)
    knowledge_table.add_column("Score", style="green", width=8)

    for snippet in rag_knowledge[:3]:  # Top 3 snippets
        section = snippet.get("section", "Unknown")
        text = snippet.get("text", "")
        score = snippet.get("score", 0.0)

        # Truncate long text
        if len(text) > 47:
            text = text[:44] + "..."

        # Format score as percentage
        score_pct = f"{score * 100:.0f}%"

        knowledge_table.add_row(section, text, score_pct)

    console.print(knowledge_table)

    # Show source info for each snippet
    console.print("[dim]Sources:[/dim]")
    for i, snippet in enumerate(rag_knowledge[:3], 1):
        file_path = snippet.get("file_path", "unknown")
        doc_id = snippet.get("doc_id", "")
        console.print(f"  [{i}] {file_path}" + (f" ({doc_id})" if doc_id else ""))


def _display_action_recommendations(
    action_recommendations: List[Dict[str, Any]],
) -> None:
    """Display proactive action recommendations from RAG."""
    if not action_recommendations:
        return

    console.print()
    from rich.table import Table

    # Build recommendations table
    recommendations_table = Table(
        title="💡 Recommended Next Actions",
        show_header=True,
    )
    recommendations_table.add_column("Action", style="yellow", width=35)
    recommendations_table.add_column("Command", style="cyan", width=30)
    recommendations_table.add_column("Confidence", style="green", width=12)

    for rec in action_recommendations[:3]:  # Top 3 recommendations
        action = rec.get("action", "")
        command = rec.get("command", "")
        confidence = rec.get("confidence", 0.0)

        # Truncate action if too long
        if len(action) > 33:
            action = action[:30] + "..."

        # Format confidence as percentage
        confidence_pct = f"{confidence * 100:.0f}%"

        # Display command or "(no CLI)" if not available
        command_display = (
            f"[cyan]{command}[/cyan]" if command else "[dim](manual)[/dim]"
        )

        recommendations_table.add_row(action, command_display, confidence_pct)

    console.print(recommendations_table)

    # Show detailed information for each recommendation
    console.print()
    console.print("[bold]Recommendation Details:[/bold]")
    for i, rec in enumerate(action_recommendations[:3], 1):
        action = rec.get("action", "")
        reason = rec.get("reason", "")
        source = rec.get("source", "unknown")
        command = rec.get("command", "")

        # Build recommendation block
        rec_lines = [f"[yellow][{i}][/yellow] {action}"]

        if reason:
            rec_lines.append(f"    [dim]Why:[/dim] {reason}")

        if command:
            rec_lines.append(f"    [dim]Run:[/dim] [cyan]{command}[/cyan]")

        rec_lines.append(f"    [dim]Source:[/dim] {source}")

        for line in rec_lines:
            console.print(line)
