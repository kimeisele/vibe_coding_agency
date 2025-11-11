"""Steward context rendering functions."""

from typing import Any

from rich.console import Console


console = Console()


def display_summary_context(
    git_reality: dict[str, Any] | None,
    active_wu: dict[str, Any] | None,
    system_health: dict[str, Any] | None,
    priority_blockers: dict[str, list[str]],
    worker_health: dict[str, Any] | None,
) -> None:
    """Display brief summary context."""
    console.print(
        "\n[bold cyan]╔═══════════════════════════════════════════════════════╗[/bold cyan]"
    )
    console.print(
        "[bold cyan]║        PHOENIX STEWARD CONTEXT - SUMMARY             ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]╚═══════════════════════════════════════════════════════╝[/bold cyan]\n"
    )

    health_grade = system_health.get("grade", "UNKNOWN") if system_health else "UNKNOWN"
    health_icon = (
        "✅" if health_grade == "PASS" else "⚠️" if health_grade == "WARN" else "❌"
    )
    console.print(f"{health_icon} [bold]System Health:[/bold] {health_grade}")

    if active_wu:
        console.print(
            f"🎯 [bold]Active Work Unit:[/bold] {active_wu.get('id')} - {active_wu.get('title', 'Untitled')}"
        )
        console.print(f"   Status: {active_wu.get('status', 'UNKNOWN')}")
    else:
        console.print("🎯 [bold]Active Work Unit:[/bold] None")

    if git_reality:
        branch = git_reality.get("current_branch", "unknown")
        commits_ahead = git_reality.get("commits_ahead", 0)
        console.print(f"📦 [bold]Git:[/bold] {branch} ({commits_ahead} commits ahead)")

    blocker_count = sum(len(blockers) for blockers in priority_blockers.values())
    if blocker_count > 0:
        console.print(f"\n⚠️  [bold red]{blocker_count} Priority Blockers[/bold red]")
        for category, blockers in priority_blockers.items():
            if blockers:
                console.print(f"   • {category}: {len(blockers)}")
    else:
        console.print("\n✅ [bold green]No Priority Blockers[/bold green]")

    console.print()


def display_compact_context(
    git_reality: dict[str, Any] | None,
    active_wu: dict[str, Any] | None,
    system_health: dict[str, Any] | None,
) -> None:
    """Display minimal compact context."""
    health_grade = system_health.get("grade", "?") if system_health else "?"
    wu_id = active_wu.get("id") if active_wu else "None"
    branch = git_reality.get("current_branch", "?") if git_reality else "?"

    console.print(f"🔹 Health: {health_grade} | WU: {wu_id} | Branch: {branch}")


def display_filtered_context(
    filter_view: str,
    git_reality: dict[str, Any] | None,
    active_wu: dict[str, Any] | None,
    system_health: dict[str, Any] | None,
    work_unit_blockers: list[Any],
    worker_health: dict[str, Any] | None,
) -> None:
    """Display only the filtered section."""
    console.print()

    if filter_view == "health":
        if system_health:
            console.print("[bold cyan]System Health Details[/bold cyan]")
            for key, value in system_health.items():
                console.print(f"  {key}: {value}")
    elif filter_view == "work-units":
        console.print("[bold cyan]Active Work Unit[/bold cyan]")
        if active_wu:
            for key, value in active_wu.items():
                console.print(f"  {key}: {value}")
        else:
            console.print("  No active work units")
    elif filter_view == "git":
        console.print("[bold cyan]Git Reality[/bold cyan]")
        if git_reality:
            for key, value in git_reality.items():
                console.print(f"  {key}: {value}")
        else:
            console.print("  No git information")

    console.print()


def display_suggested_commands(
    action_recommendations: list[dict[str, Any]] | None,
    rag_knowledge: list[dict[str, Any]] | None,
    active_wu: dict[str, Any] | None,
) -> None:
    """Display suggested commands based on context."""
    console.print()
    console.print("[bold cyan]💡 SUGGESTED COMMANDS:[/bold cyan]")
    console.print()

    if not action_recommendations:
        action_recommendations = []
    if not rag_knowledge:
        rag_knowledge = []

    suggestions = []

    if action_recommendations:
        for rec in action_recommendations[:3]:
            if isinstance(rec, dict):
                suggestion = rec.get("suggestion", "")
            else:
                suggestion = str(rec)
            if suggestion:
                suggestions.append(suggestion)

    if not suggestions:
        if active_wu:
            suggestions.append(f"phoenix work-unit inspect {active_wu.get('id')}")
        suggestions.append("phoenix steward context --with-blockers")
        suggestions.append("phoenix search --query architecture")

    for i, suggestion in enumerate(suggestions[:4], 1):
        console.print(f"  {i}. {suggestion}")

    console.print()
