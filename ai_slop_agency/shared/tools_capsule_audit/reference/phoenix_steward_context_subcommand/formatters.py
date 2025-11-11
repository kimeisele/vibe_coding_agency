"""Output formatting for the steward context command."""

import re
from typing import Any, Dict, List


def format_git_reality(git_reality: Dict[str, Any] | None) -> List[str]:
    """Format git reality section."""
    lines = []
    if git_reality:
        lines.append("[bold]🌿 Git Reality[/bold]")
        lines.append(
            f"   ├─ Branch: [cyan]{git_reality['branch']}[/cyan] ({git_reality['commits_ahead']} commits ahead of main)"
        )
        if git_reality.get("recent_commits"):
            lines.append("   ├─ Recent Activity:")
            for commit in git_reality["recent_commits"]:
                lines.append(f"   │  ├─ [dim]{commit}[/dim]")

        # Filter out noisy files
        relevant_changes = [
            line
            for line in git_reality.get("uncommitted_summary", [])
            if "commit_message.tmp" not in line
            and "files changed" not in line
            and "work_units/" not in line
        ]
        if relevant_changes:
            lines.append("   └─ Uncommitted Changes:")
            for line in relevant_changes:
                lines.append(f"      └─ [yellow]{line.strip()}[/yellow]")
        lines.append("")
    return lines


def format_priority_blockers(priority_blockers: Dict[str, List[str]]) -> List[str]:
    """Format priority blockers section."""
    lines = []
    if priority_blockers:
        lines.append("[bold]🔥 Priority Blockers[/bold]")
        for file, blockers in priority_blockers.items():
            lines.append(f"   ├─ In [bold]{file}[/bold]:")
            for i, blocker in enumerate(blockers):
                prefix = "└─" if i == len(blockers) - 1 else "├─"
                lines.append(f"   │  {prefix} [yellow]{blocker}[/yellow]")
        lines.append("")
    return lines


def format_active_wu(active_wu: Dict[str, Any] | None) -> List[str]:
    """Format active work unit section."""
    lines = []
    if active_wu:
        lines.append("[bold]🎯 Active Work Unit[/bold]")
        lines.append(
            f"   ├─ {active_wu['id']} ([yellow]{active_wu['status']}[/yellow])"
        )
        lines.append(f"   └─ Tests: {active_wu.get('test_status', 'N/A')}")
        lines.append("")
    return lines


def format_system_health(system_health: Dict[str, Any] | None) -> List[str]:
    """Format system health section."""
    lines = []
    if system_health:
        health_str = f"Grade: {system_health['grade']} | Issues: {system_health['critical_count']} Critical, {system_health['high_count']} High, {system_health['medium_count']} Medium"
        lines.append("[bold]🚨 System Health[/bold]")
        lines.append(
            f"   └─ {health_str} (Audit: {system_health.get('age_minutes', 0):.0f} min ago)"
        )
        lines.append("")
    return lines


def format_scheduler_status(scheduler_status: Dict[str, Any] | None) -> List[str]:
    """Format scheduler status section."""
    lines = []
    if scheduler_status:
        state = "🟢 RUNNING" if scheduler_status.get("running", False) else "🔴 STOPPED"
        total = scheduler_status.get("total_schedules", 0)
        enabled = scheduler_status.get("enabled_schedules", 0)
        lines.append("[bold]⏰ Scheduler[/bold]")
        lines.append(f"   ├─ State: {state}")
        lines.append(
            f"   └─ Jobs: {enabled}/{total} enabled ({scheduler_status.get('schedules_due_now', 0)} due now)"
        )
        lines.append("")
    return lines


def format_technical_debt(tech_debt: Dict[str, Any] | None) -> List[str]:
    """Format technical debt section."""
    lines: List[str] = []
    if not tech_debt:
        return lines

    stale_str = (
        "[bold red](STALE)[/bold red]" if tech_debt.get("is_stale", False) else ""
    )
    age_days = tech_debt.get("age_days", 0) or 0
    lines.append(
        f"[bold]📋 Technical Debt[/bold] {stale_str} (Updated {age_days:.0f} days ago)"
    )

    if tech_debt.get("has_data"):
        if tech_debt.get("p0_title"):
            lines.append(f"   ├─ P0 ({tech_debt['p0_count']}): {tech_debt['p0_title']}")
        else:
            lines.append(f"   ├─ P0 Issues: {tech_debt.get('p0_count', 0)}")

        if tech_debt.get("p1_title"):
            lines.append(f"   ├─ P1 ({tech_debt['p1_count']}): {tech_debt['p1_title']}")
        else:
            lines.append(f"   ├─ P1 Issues: {tech_debt.get('p1_count', 0)}")

        lines.append(f"   └─ P2 Issues: {tech_debt.get('p2_count', 0)}")
    else:
        lines.append("   └─ No tracked technical debt entries found.")
    lines.append("")
    return lines


def format_agent_toolbox() -> List[str]:
    """Format agent toolbox section."""
    lines = []
    lines.append(
        "[bold]🛠️  Agent Toolbox[/bold] [dim](Essential commands for agents)[/dim]"
    )
    lines.append("   ├─ [cyan]work-unit list[/cyan]         → See available work units")
    lines.append('   ├─ [cyan]knowledge query "..."[/cyan]  → Search knowledge base')
    lines.append("   ├─ [cyan]work-unit show <ID>[/cyan]    → View work unit details")
    lines.append(
        "   ├─ [cyan]steward handover[/cyan]       → Create agent handover summary"
    )
    lines.append(
        "   └─ [cyan]steward context[/cyan]        → View current system state"
    )
    lines.append("")
    lines.append(
        '   [dim]💡 Example:[/dim] [green]phoenix knowledge query "architecture patterns"[/green]'
    )
    lines.append("")
    return lines


def format_next_actions(
    priority_blockers: Dict[str, List[str]],
    git_reality: Dict[str, Any] | None,
    active_wu: Dict[str, Any] | None,
) -> List[str]:
    """Format recommended next actions."""
    next_actions = []
    if priority_blockers:
        next_actions.append("Fix priority blockers:")
        # Suggest fixes for mypy errors
        for file, blockers in priority_blockers.items():
            if any("MyPy" in b for b in blockers):
                first_error = next((b for b in blockers if "line" in b), None)
                if first_error:
                    match = re.search(r"line (\d+)", first_error)
                    if match:
                        line = match.group(1)
                        next_actions.append(
                            f"   → Fix MyPy errors in {file} (lines like {line})"
                        )
                        next_actions.append(f"   → Command: vim +{line} {file}")
                        next_actions.append(f"   → Verify: mypy --strict {file}")
                break  # Only suggest for the first file with MyPy errors

    elif git_reality and git_reality.get("uncommitted_summary"):
        next_actions.append(
            "Stage and commit your changes (`git add .`, `phoenix commit`)"
        )
    elif active_wu:
        next_actions.append(f"Continue work on {active_wu.get('id', 'unknown')}")
    else:
        next_actions.append("Find new work (`phoenix work-unit list`)")

    return next_actions
