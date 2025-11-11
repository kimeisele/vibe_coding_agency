"""Toolkit information and semantic search commands."""

import json
import logging
import time
from pathlib import Path

import typer

from agency_toolkit.core.reporter import get_reporter
from agency_toolkit.providers.mistral_provider import MistralProvider

logger = logging.getLogger(__name__)

info_command = typer.Typer(help="Toolkit information and discovery")


def get_available_social_templates() -> dict[str, str]:
    """Return available social templates with descriptions."""
    # Path: agency_toolkit/commands/info.py -> agency_toolkit_root/templates/social
    template_dir = Path(__file__).parent.parent.parent / "templates" / "social"

    templates = {}
    for template_file in sorted(template_dir.glob("*.json")):
        try:
            data = json.loads(template_file.read_text())
            templates[template_file.stem] = data.get("description", "Social template")
        except Exception as e:
            logger.warning(f"Failed to load template {template_file}: {e}")

    return templates


def get_available_seed_templates() -> dict[str, str]:
    """Return available seed templates with descriptions."""
    registry_path = (
        Path(__file__).parent.parent.parent / "registry" / "seeds" / "templates.json"
    )

    seeds = {}
    if registry_path.exists():
        try:
            data = json.loads(registry_path.read_text())
            templates = data.get("templates", {})
            for template_id, template_data in templates.items():
                seeds[template_id] = template_data.get("description", "Seed template")
        except Exception as e:
            logger.warning(f"Failed to load seed templates: {e}")

    return seeds


def get_available_providers() -> dict[str, dict]:
    """Return available image providers with descriptions."""
    providers = {
        "pollinations": {
            "description": "Free AI image generation (default)",
            "status": "✅ Default",
        },
        "replicate": {
            "description": "Replicate API (optional, requires API key)",
            "status": "",
        },
    }
    return providers


def load_toolkit_docs() -> str:
    """Load and cache toolkit documentation.

    Documentation is cached for 24 hours to avoid repeated file reads.

    Returns:
        Concatenated documentation from BLUEPRINT.yaml,
        IMPLEMENTATION.yaml, and ROADMAP.md
    """
    # Try cache first
    cache_dir = Path.home() / ".cache" / "agency-toolkit"
    cache_file = cache_dir / "docs_context.txt"

    # Check if cache exists and is less than 24 hours old
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < 86400:  # 24 hours
            logger.debug("Using cached documentation")
            return cache_file.read_text()

    # Build docs context from SSOT files
    docs_base = Path(__file__).parent.parent.parent / "docs"

    context_parts = []

    # Add BLUEPRINT
    blueprint_path = docs_base / "BLUEPRINT.yaml"
    if blueprint_path.exists():
        context_parts.append(f"# BLUEPRINT\n{blueprint_path.read_text()}")

    # Add IMPLEMENTATION
    implementation_path = docs_base / "IMPLEMENTATION.yaml"
    if implementation_path.exists():
        context_parts.append(f"\n\n# IMPLEMENTATION\n{implementation_path.read_text()}")

    # Add ROADMAP
    roadmap_path = docs_base / "ROADMAP.md"
    if roadmap_path.exists():
        context_parts.append(f"\n\n# ROADMAP\n{roadmap_path.read_text()}")

    context = "\n".join(context_parts)

    # Cache it
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(context)
        logger.debug(f"Cached documentation to {cache_file}")
    except Exception as e:
        logger.warning(f"Failed to cache documentation: {e}")

    return context


def _display_commands_section(reporter=None) -> None:
    """Display available commands section."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("📋 Available Commands:")
    commands_info = [
        ("toolkit social", "Generate social media posts"),
        ("toolkit briefing", "Create project briefings"),
        ("toolkit structure", "Create folder structures"),
        ("toolkit image", "Generate AI images"),
        ("toolkit mistral", "Query Mistral AI"),
        ("toolkit info", "Show this information"),
        ("toolkit ask <query>", "Ask about toolkit (Mistral-powered)"),
    ]
    for cmd, desc in commands_info:
        reporter.info(f"  {cmd:<30} {desc}")


def _display_social_templates_section(reporter=None) -> None:
    """Display social templates section."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("🎨 Social Templates:")
    social_templates = get_available_social_templates()
    if social_templates:
        for name, desc in social_templates.items():
            reporter.info(f"  - {name:<15} {desc}")
    else:
        reporter.info("  (no templates found)")


def _display_image_providers_section(reporter=None) -> None:
    """Display image providers section."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("🖼️ Image Providers:")
    providers = get_available_providers()
    for name, info in providers.items():
        status = info.get("status", "")
        reporter.info(f"  - {name:<15} {info['description']} {status}")


def _display_seed_templates_section(reporter=None) -> None:
    """Display seed templates section."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("🎭 Seed Templates:")
    seeds = get_available_seed_templates()
    if seeds:
        for name, desc in seeds.items():
            reporter.info(f"  - {name:<15} {desc}")
    else:
        reporter.info("  (no templates found)")


def _display_help_section(reporter=None) -> None:
    """Display help/getting started section."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("💡 Get Started:")
    help_info = [
        ("toolkit social --help", "Detailed social post help"),
        ("toolkit ask 'How do I...?'", "Ask Mistral for help"),
        ("toolkit info", "Show this information"),
    ]
    for cmd, desc in help_info:
        reporter.info(f"  {cmd:<35} {desc}")


@info_command.command(name="info")
def info(ctx: typer.Context) -> None:
    """Display toolkit capabilities and available features.

    Shows:
    - Available commands
    - Social media templates
    - Image providers
    - Seed templates for consistent aesthetics

    Examples:
        toolkit info
    """
    config = ctx.obj
    reporter = get_reporter(config.json_output)

    reporter.divider(50)
    reporter.info("Agency Toolkit - Information & Help")
    reporter.divider(50)

    # Display sections
    reporter.info("")
    _display_commands_section(reporter)
    reporter.info("")
    _display_social_templates_section(reporter)
    reporter.info("")
    _display_image_providers_section(reporter)
    reporter.info("")
    _display_seed_templates_section(reporter)
    reporter.info("")
    _display_help_section(reporter)
    reporter.info("")
    reporter.divider(50)


@info_command.command(name="ask")
def ask(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Your question about the toolkit"),
) -> None:
    """Ask Mistral AI about the toolkit.

    The AI reads documentation and answers your questions about how to use
    the toolkit, what features are available, and how to solve common tasks.

    Examples:
        toolkit ask "How do I create an image?"
        toolkit ask "What templates are available?"
        toolkit ask "How do I use seed templates with social posts?"
    """
    config = ctx.obj
    reporter = get_reporter(config.json_output)

    # Step 1: Show thinking message
    reporter.processing("🤔 Thinking...")

    # Step 2: Load documentation (this handles caching)
    try:
        docs_context = load_toolkit_docs()
    except Exception as e:
        reporter.error(f"❌ Failed to load documentation: {e}")
        raise typer.Exit(1)

    # Step 3: Build prompt for Mistral
    prompt = (
        "You are the Agency Toolkit AI assistant. You have read the toolkit's "
        "documentation and understand how all features work.\n\n"
        f"User question: {query}\n\n"
        f"Toolkit documentation:\n{docs_context}\n\n"
        "Provide a helpful, concise answer (2-3 sentences max) with a "
        "code example if relevant."
    )

    # Step 4: Query Mistral using new provider
    try:
        mistral = MistralProvider()
        result = mistral.generate(
            prompt=prompt,
            model="mistral-small-latest",
        )

        answer = result.get("response", "").strip()
        if not answer:
            reporter.error("❌ Mistral returned empty response")
            raise typer.Exit(1)

        reporter.success("✅ Answer:")
        reporter.info(answer)

    except Exception as e:
        reporter.error(f"❌ Failed to get answer: {e}")
        raise typer.Exit(1)


def _get_text_providers():
    """Get list of text AI providers with their environment variables."""
    return [
        ("Mistral", "MISTRAL_API_KEY"),
        ("Google GenAI", "GOOGLE_API_KEY"),
    ]


def _get_image_providers():
    """Get list of image providers with their environment variables and notes."""
    return [
        ("Pollinations", None, "No API key needed"),
        ("Replicate", "REPLICATE_API_TOKEN", "Set for better quality"),
    ]


def _check_text_provider_status(provider_name: str, env_var: str) -> tuple[str, str]:
    """Check status of a text AI provider.

    Returns:
        Tuple of (status, details) for display
    """
    import os

    api_key = os.environ.get(env_var)
    if api_key:
        status = "[green]✓ Ready[/green]"
        details = f"API key set ({len(api_key)} chars)"
    else:
        status = "[red]✗ Not configured[/red]"
        details = f"Set {env_var} environment variable"

    return status, details


def _check_image_provider_status(
    provider_name: str, env_var: str, note: str
) -> tuple[str, str]:
    """Check status of an image provider.

    Returns:
        Tuple of (status, details) for display
    """
    import os

    if env_var is None:
        status = "[green]✓ Ready[/green]"
        details = note
    else:
        api_key = os.environ.get(env_var)
        if api_key:
            status = "[green]✓ Ready[/green]"
            details = f"API key set ({len(api_key)} chars)"
        else:
            status = "[yellow]⚠ Optional[/yellow]"
            details = f"Set {env_var} for better quality"

    return status, details


def _create_providers_table():
    """Create and populate the providers status table."""
    from rich.table import Table

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan", width=20)
    table.add_column("Type", style="dim", width=15)
    table.add_column("Status", width=15)
    table.add_column("Details", style="dim")

    # Add text providers
    text_providers = _get_text_providers()
    for provider_name, env_var in text_providers:
        status, details = _check_text_provider_status(provider_name, env_var)
        table.add_row(provider_name, "Text AI", status, details)

    # Add image providers
    image_providers = _get_image_providers()
    for provider_name, env_var, note in image_providers:
        status, details = _check_image_provider_status(provider_name, env_var, note)
        table.add_row(provider_name, "Image AI", status, details)

    return table


def _calculate_provider_counts() -> tuple[int, int]:
    """Calculate configured and total provider counts.

    Returns:
        Tuple of (configured_count, total_required)
    """
    import os

    text_providers = _get_text_providers()
    image_providers = _get_image_providers()

    configured_count = sum(
        1
        for _, env_var in text_providers
        + [(p[0], p[1]) for p in image_providers if p[1]]
        if env_var and os.environ.get(env_var)
    )
    total_required = len(text_providers) + sum(1 for p in image_providers if p[1])

    return configured_count, total_required


def _print_summary_message(configured_count: int, total_required: int) -> None:
    """Print summary message about provider configuration."""
    from rich.console import Console

    console = Console()

    if configured_count == 0:
        console.print(
            "[yellow]⚠️  No providers configured. "
            "Set API keys to use AI features.[/yellow]"
        )
        console.print("\nQuick setup:")
        console.print("  export MISTRAL_API_KEY='your-key'")
        console.print("  export GOOGLE_API_KEY='your-key'")
    elif configured_count < total_required:
        console.print(
            f"[yellow]ℹ  {configured_count}/{total_required} optional "
            f"providers configured[/yellow]"
        )
    else:
        console.print(f"[green]✓ All {configured_count} providers configured![/green]")


def _display_providers_header(reporter=None) -> None:
    """Display providers status header."""
    if reporter is None:
        reporter = get_reporter()

    reporter.info("")
    reporter.info("Provider Configuration Status")
    reporter.divider()
    reporter.info("")


def _display_providers_table(reporter=None) -> None:
    """Display the providers status table."""
    if reporter is None:
        reporter = get_reporter()

    from rich.console import Console

    console = Console()
    table = _create_providers_table()
    console.print(table)
    console.print()


def _display_providers_summary(reporter=None) -> None:
    """Display provider configuration summary."""
    if reporter is None:
        reporter = get_reporter()

    configured_count, total_required = _calculate_provider_counts()

    if configured_count == 0:
        reporter.warning("⚠️  No providers configured. Set API keys to use AI features.")
        reporter.info("Quick setup:")
        reporter.info("  export MISTRAL_API_KEY='your-key'")
        reporter.info("  export GOOGLE_API_KEY='your-key'")
    elif configured_count < total_required:
        reporter.warning(
            f"ℹ  {configured_count}/{total_required} optional providers configured"
        )
    else:
        reporter.success(f"✓ All {configured_count} providers configured!")

    reporter.info("")


@info_command.command(name="providers")
def providers_status(ctx: typer.Context) -> None:
    """Show status of all AI and image providers.

    Checks which providers have API keys configured and are ready to use.
    Helps diagnose configuration issues before running commands.

    Examples:
        toolkit info providers
    """
    config = ctx.obj
    reporter = get_reporter(config.json_output)

    # Display header
    _display_providers_header(reporter)

    # Display providers table
    _display_providers_table(reporter)

    # Display summary
    _display_providers_summary(reporter)
