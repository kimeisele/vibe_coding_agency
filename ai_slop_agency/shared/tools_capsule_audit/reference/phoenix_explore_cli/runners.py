"""Explore command runners - Core logic implementation."""

import json
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Optional

import click

from phoenix_system.agent_api import AgentAPI
from phoenix_system.agents.explore import ExploreAgent
from phoenix_system.cli.shared_spot import extract_spot_context, get_spot_snapshot
from phoenix_system.iron_core import IronCoreFactory
from phoenix_system.knowledge.safe_access import get_ingestor_handle
from phoenix_system.llm import LocalDeterministicProvider, get_llm_provider


# ============================================================================
# Exceptions
# ============================================================================


class ExplorationTimeout(Exception):
    """Raised when exploration exceeds time limit."""

    pass


class ExplorationAbort(Exception):
    """Signal to abort exploration gracefully."""

    pass


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ExplorationContext:
    """Encapsulate exploration state and results."""

    goal: str
    max_iterations: int
    status: str = "initial"
    markdown_summary: str = ""
    execution_history: list = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    output_path: Optional[Path] = None
    json_data: Optional[dict] = None
    llm_provider: Optional[object] = None


# ============================================================================
# Setup & Initialization
# ============================================================================


def _timeout_handler(signum, frame):
    """Handler for SIGALRM timeout signal."""
    raise ExplorationTimeout("Exploration exceeded time limit")


def initialize_iron_core():
    """Create IronCore production core with graceful failure."""
    try:
        return IronCoreFactory.create_production_core(), None
    except Exception as exc:
        return None, f"IronCore initialization failed: {exc}"


def initialize_agent_api(iron_core, agent_session):
    """Initialize AgentAPI with specified IronCore and agent session."""
    return AgentAPI(iron_core, agent_session)


def resolve_llm_provider(
    llm_provider_name: Optional[str],
) -> tuple[object, Optional[str]]:
    """Resolve LLM provider (specified, auto-detected, or stub)."""
    try:
        return get_llm_provider(llm_provider_name), None
    except Exception as exc:
        return LocalDeterministicProvider(), f"LLM provider fallback: {exc}"


def validate_ingestor_handle():
    """Validate ingestor handle is available."""
    handle = get_ingestor_handle()
    if not handle.available:
        return handle, f"Knowledge ingestor unavailable: {handle.error}"
    return handle, None


def create_explore_agent(agent_api, llm_provider, ingestor_handle):
    """Create and configure ExploreAgent."""
    return ExploreAgent(
        api=agent_api,
        llm_provider=llm_provider,
    )


def run_agent_exploration(
    agent: ExploreAgent,
    goal: str,
    max_iterations: int,
    timeout_seconds: int = 60,
) -> tuple[str, list]:
    """Execute exploration and return summary + history."""
    import platform

    original_handler = None
    timeout_active = False

    try:
        if platform.system() != "Windows" and timeout_seconds > 0:
            original_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_seconds)
            timeout_active = True

        start_time = time.time()
        markdown_summary = agent.run(goal=goal, max_iterations=max_iterations)
        elapsed = time.time() - start_time

        return markdown_summary, agent.execution_history
    finally:
        if timeout_active and original_handler is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)


# ============================================================================
# Utilities
# ============================================================================


def build_json_output(
    goal: str,
    max_iterations: int,
    markdown_summary: str,
    execution_history: list,
    *,
    status: str,
    errors: list[str],
    llm_provider: object | None = None,
) -> dict:
    """Build JSON output that respects SPOT worldview."""
    timestamp = datetime.utcnow()
    timestamp_str = timestamp.strftime("%Y%m%dT%H%M%SZ")

    goal_hash = sha256(goal.encode()).hexdigest()[:12]
    exploration_id = f"explore_{timestamp_str}_{goal_hash}"

    spot_snapshot = get_spot_snapshot()
    spot_context = extract_spot_context(spot_snapshot)

    mode = "online"
    capabilities_missing = []
    degradation_reason = None

    if llm_provider is not None:
        provider_name = type(llm_provider).__name__
        if "LocalDeterministic" in provider_name or "Stub" in provider_name:
            mode = "offline_stub"
            capabilities_missing = [
                "deep cross-file semantic reasoning",
                "vector/embedding-based recall",
                "external knowledge beyond local codebase",
                "probabilistic code path analysis",
            ]
            degradation_reason = (
                "Running in offline stub mode (no Anthropic or Mistral provider available). "
                "Exploration uses deterministic local heuristics instead of AI reasoning. "
                "Results are valid but limited to obvious patterns and file structure."
            )

    if status == "degraded" and degradation_reason is None:
        degradation_reason = errors[0] if errors else "Unknown degradation"

    output = {
        "exploration_id": exploration_id,
        "goal": goal,
        "max_iterations": max_iterations,
        "timestamp": timestamp.isoformat() + "Z",
        "mode": mode,
        "findings": {
            "summary": markdown_summary,
            "execution_history": execution_history[-10:],
        },
        "spot_context": spot_context,
        "source": "ExploreAgent",
        "status": status,
        "errors": errors,
    }

    if status == "degraded":
        output["degradation_reason"] = degradation_reason
        output["capabilities_missing"] = capabilities_missing

    return output


def persist_exploration(exploration_id: str, json_output: dict) -> Path:
    """Persist exploration results to filesystem and auto-index to RAG."""
    explorations_dir = Path.cwd() / "explorations"
    explorations_dir.mkdir(exist_ok=True)

    output_file = explorations_dir / f"{exploration_id}.json"
    output_file.write_text(json.dumps(json_output, indent=2))

    try:
        _auto_index_exploration(output_file, json_output)
    except Exception:
        pass

    return output_file


def _auto_index_exploration(exploration_file: Path, data: dict) -> None:
    """Index exploration to RAG knowledge base (best effort)."""
    try:
        from phoenix_system.knowledge.ingestor import KnowledgeIngestor

        ingestor = KnowledgeIngestor()

        goal = data.get("goal", "")
        findings = data.get("findings", {})
        summary = findings.get("summary", "")
        timestamp = data.get("timestamp", "")

        md_content = f"""# Exploration: {goal}

Timestamp: {timestamp}

## Summary
{summary}
"""

        md_file = exploration_file.with_suffix(".md")
        md_file.write_text(md_content)

        ingestor.ingest_file(md_file)

    except ImportError:
        pass
    except Exception:
        pass


@contextmanager
def json_logging_context(output_json: bool):
    """Suppress intermediate logging when outputting JSON."""
    if output_json:
        import logging

        logging.disable(logging.CRITICAL)
    try:
        yield
    finally:
        if output_json:
            import logging

            logging.disable(logging.NOTSET)


# ============================================================================
# Rendering Formats
# ============================================================================


def render_default_format(result: ExplorationContext) -> None:
    """Original markdown format."""
    click.echo(result.markdown_summary)
    if result.status == "failed":
        click.echo("⚠️ Exploration failed; results not saved.", err=True)
    elif result.output_path is not None:
        click.echo(f"\n📝 Exploration saved: {result.output_path}")
    else:
        click.echo("\n⚠️ Exploration degraded; results not persisted.", err=True)


def render_clean_format(result: ExplorationContext) -> None:
    """Clean, readable format without clutter."""
    click.echo("=" * 70)
    click.echo(f"🔍 Exploration: {result.goal}")
    click.echo("=" * 70)
    click.echo()
    click.echo(result.markdown_summary)
    click.echo()
    click.echo("-" * 70)
    if result.status == "failed":
        click.echo("❌ Status: FAILED", err=True)
    elif result.status == "degraded":
        click.echo("⚠️  Status: DEGRADED (partial results)")
    else:
        click.echo("✅ Status: SUCCESS")

    if result.output_path:
        click.echo(f"📄 Saved: {result.output_path}")
    click.echo("-" * 70)


def render_summary_format(result: ExplorationContext) -> None:
    """Brief summary format."""
    status_icon = (
        "✅"
        if result.status == "completed"
        else "⚠️"
        if result.status == "degraded"
        else "❌"
    )
    click.echo(f"{status_icon} Goal: {result.goal}")
    click.echo(f"   Status: {result.status.upper()}")

    lines = result.markdown_summary.split("\n")
    findings = [line for line in lines[:5] if line.strip()]
    if findings:
        click.echo(f"   Findings: {findings[0][:80]}...")

    if result.output_path:
        click.echo(f"   Saved: {result.output_path}")


def render_suggested_actions(result: ExplorationContext) -> None:
    """Show suggested next actions based on exploration results."""
    click.echo()
    click.echo("💡 SUGGESTED NEXT ACTIONS:")
    click.echo()

    summary_lower = result.markdown_summary.lower()
    suggestions = []

    if "test" in summary_lower or "testing" in summary_lower:
        suggestions.append("phoenix test run  # Run tests for explored code")

    if "file" in summary_lower or "module" in summary_lower:
        suggestions.append(
            'phoenix explore run --goal "analyze specific module" --format clean'
        )

    if "persistence" in summary_lower or "database" in summary_lower:
        suggestions.append('phoenix search --query "database models" --format clean')

    if "error" in summary_lower or "issue" in summary_lower:
        suggestions.append("phoenix work-unit create --type bugfix  # Create fix task")

    if not suggestions:
        suggestions = [
            'phoenix search --query "<related topic>" --format clean',
            "phoenix steward context --format summary  # Check system status",
            'phoenix explore run --goal "<deeper analysis>" --format clean',
        ]

    for i, suggestion in enumerate(suggestions[:4], 1):
        click.echo(f"  {i}. {suggestion}")

    click.echo()


# ============================================================================
# Core Execution Logic
# ============================================================================


def _execute_async_mode(
    goal: str,
    max_iterations: int,
    llm_provider_name: str | None,
    output_json: bool,
) -> None:
    """Queue exploration as background job."""
    try:
        from phoenix_system.background.jobs import create_job, get_session

        spot_at_creation = extract_spot_context(get_spot_snapshot())
        with get_session() as db:
            job = create_job(
                db,
                job_type="explore",
                payload={
                    "goal": goal,
                    "max_iterations": max_iterations,
                    "llm_provider": llm_provider_name,
                    "spot_context_at_creation": spot_at_creation,
                },
                max_retries=2,
            )
            job_id = job.id

        response = {
            "status": "queued",
            "job_id": job_id,
            "goal": goal,
            "message": f"Exploration queued as job {job_id}. Monitor with: phoenix jobs describe {job_id}",
            "spot_context": spot_at_creation,
        }

        if output_json:
            click.echo(json.dumps(response, indent=2))
        else:
            click.echo(f"✅ Exploration queued: job_id={job_id}")
            click.echo(f"   Goal: {goal}")
            click.echo(f"   Monitor with: phoenix jobs describe {job_id}")
    except Exception as exc:
        error_type = type(exc).__name__
        error_detail = str(exc)
        if "database" in error_detail.lower() or isinstance(exc, (IOError, OSError)):
            error_msg = (
                f"Failed to queue exploration: Database/filesystem issue ({error_type}): "
                f"{error_detail[:100]}"
            )
        elif "permission" in error_detail.lower():
            error_msg = (
                f"Failed to queue exploration: Permission denied ({error_type}): "
                f"{error_detail[:100]}"
            )
        else:
            error_msg = (
                f"Failed to queue exploration: {error_type}: {error_detail[:100]}"
            )

        response = {
            "status": "failed",
            "error": error_msg,
            "error_type": error_type,
            "spot_context": extract_spot_context(get_spot_snapshot()),
        }
        if output_json:
            click.echo(json.dumps(response, indent=2))
        else:
            click.echo(f"❌ {error_msg}", err=True)
        raise SystemExit(1) from None


def _run_synchronous_exploration(
    goal: str,
    max_iterations: int,
    output_json: bool,
    llm_provider_name: Optional[str],
    timeout_seconds: int = 60,
) -> ExplorationContext:
    """Run synchronous exploration with full error handling."""
    context = ExplorationContext(
        goal=goal,
        max_iterations=max_iterations,
    )

    try:
        iron_core, iron_warning = initialize_iron_core()
        if iron_warning:
            context.errors.append(iron_warning)

        agent_session = iron_core.session_manager.get_agent_session()

        agent_api = initialize_agent_api(iron_core, agent_session)
        llm_provider, llm_warning = resolve_llm_provider(llm_provider_name)
        context.llm_provider = llm_provider
        if llm_warning:
            context.errors.append(llm_warning)
            context.status = "degraded"

        ingestor_handle, ingestor_warning = validate_ingestor_handle()
        if ingestor_warning:
            context.errors.append(ingestor_warning)
            context.status = "degraded"

        agent = create_explore_agent(agent_api, llm_provider, ingestor_handle)

        try:
            markdown_summary, execution_history = run_agent_exploration(
                agent, goal, max_iterations, timeout_seconds=timeout_seconds
            )
        except ExplorationTimeout as e:
            markdown_summary = f"❌ Exploration timeout: {str(e)}\n\nUse --timeout to increase the limit if needed."
            execution_history = []

        context.markdown_summary = markdown_summary
        context.execution_history = execution_history
        context.status = "completed" if not context.errors else "degraded"

        context.json_data = build_json_output(
            goal=goal,
            max_iterations=max_iterations,
            markdown_summary=markdown_summary,
            execution_history=execution_history,
            status=context.status,
            errors=context.errors,
            llm_provider=llm_provider,
        )

        exploration_id = context.json_data["exploration_id"]
        try:
            context.output_path = persist_exploration(exploration_id, context.json_data)
        except Exception as persist_error:
            context.errors.append(f"Failed to persist exploration: {persist_error}")
            context.status = "degraded"

    except ExplorationAbort:
        context.status = "aborted"
        context.errors.append("Exploration aborted by user")
    except Exception as exc:
        context.status = "failed"
        context.errors.append(f"Exploration failed: {exc}")

    return context


def _render_formatted_output(
    result: ExplorationContext,
    output_format: str,
    suggest_next: bool,
) -> None:
    """Render exploration result in different formats."""
    if output_format == "summary":
        render_summary_format(result)
    elif output_format == "clean":
        render_clean_format(result)
    else:
        render_default_format(result)

    if suggest_next:
        render_suggested_actions(result)


def _render_exploration_result(
    result: ExplorationContext,
    output_json: bool,
    output_format: str = "default",
    suggest_next: bool = False,
) -> None:
    """Render exploration result with appropriate output format."""
    payload = result.json_data or build_json_output(
        goal=result.goal,
        max_iterations=result.max_iterations,
        markdown_summary=result.markdown_summary,
        execution_history=result.execution_history,
        status=result.status,
        errors=result.errors,
        llm_provider=result.llm_provider,
    )

    if output_json:
        click.echo(json.dumps(payload, indent=2))
        if result.status == "degraded":
            click.echo("degraded", err=True)
        elif result.status == "failed":
            click.echo("failed", err=True)
    else:
        _render_formatted_output(result, output_format, suggest_next)

    if result.status == "failed":
        raise SystemExit(1) from None


def run_exploration(
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
      phoenix explore run --goal "map data ingestion flow" --json
      phoenix explore run --goal "find security issues" --async
      phoenix explore run --goal "find persistence code" --format clean
      phoenix explore run --goal "analyze models" --suggest-next
      phoenix explore run --goal "quick check" --format summary
      phoenix explore run --goal "long analysis" --timeout 120
    """
    if async_mode:
        _execute_async_mode(goal, max_iterations, llm_provider_name, output_json)
        return

    with json_logging_context(output_json):
        result = _run_synchronous_exploration(
            goal=goal,
            max_iterations=max_iterations,
            output_json=output_json,
            llm_provider_name=llm_provider_name,
            timeout_seconds=timeout,
        )

    _render_exploration_result(result, output_json, output_format, suggest_next)
