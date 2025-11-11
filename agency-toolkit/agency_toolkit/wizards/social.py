"""Social Post Generation Wizard (WU-7.3)."""

from pathlib import Path

import typer

from agency_toolkit.core.reporter import get_reporter
from agency_toolkit.core.social import generate as generate_social_post
from agency_toolkit.core.social import generate_background

from .helpers import (
    confirm_proceed,
    prompt_choice,
    prompt_number,
    prompt_path,
    prompt_text,
    prompt_yes_no,
    show_header,
    show_summary,
)


def social_wizard(config) -> None:
    """Interactive wizard for social post generation."""
    show_header("📝 Social Post Generator Wizard")

    # Step 1: Main message
    typer.echo("Step 1: What's your message?")
    typer.echo("   Example: 'Check out our new product launch!'\n")
    text = prompt_text("Your message", required=True)

    # Step 2: Style
    style_choices = [
        ("modern", "Clean, minimal, professional"),
        ("bold", "Bright, energetic, eye-catching"),
        ("minimal", "Zen, simple, elegant"),
    ]
    style = prompt_choice(
        "\nStep 2: What style do you prefer?", style_choices, default="modern"
    )

    # Step 3: Color theme
    color_choices = [
        ("auto", "Let AI decide"),
        ("warm", "Oranges, reds, yellows"),
        ("cool", "Blues, purples, greens"),
        ("neutral", "Blacks, grays, whites"),
    ]
    color = prompt_choice("\nStep 3: What color theme?", color_choices, default="auto")

    # Step 4: Background image
    add_background = prompt_yes_no("\nStep 4: Add background image?", default=False)
    bg_concept = None
    if add_background:
        typer.echo("   Example: 'sunset beach', 'futuristic city'\n")
        bg_concept = prompt_text("Background concept")

    # Step 5: Number of variations
    num_variations = prompt_number(
        "\nStep 5: How many variations?",
        min_val=1,
        max_val=100,
        default=1,
    )

    # Step 6: Output directory
    default_output = Path("./output/social")
    output_dir = prompt_path("\nStep 6: Output directory", default_output)

    # Step 7: Preview
    action_choices = [
        ("dry-run", "Preview without saving"),
        ("generate", "Generate now"),
        ("save-config", "Save config and exit"),
    ]
    action = prompt_choice(
        "\nStep 7: What would you like to do?", action_choices, default="generate"
    )

    # Summary
    data = {
        "message": text,
        "style": style,
        "color_theme": color,
        "background": bg_concept or "None",
        "variations": num_variations,
        "output_directory": str(output_dir),
        "action": action,
    }
    show_summary(data)

    if not confirm_proceed("Ready to generate?"):
        typer.secho("✋ Cancelled. No posts generated.", fg="yellow")
        return

    # Generate posts
    _generate_social_posts(
        config, text, style, color, bg_concept, num_variations, output_dir, action
    )


def _generate_social_posts(
    config,
    text: str,
    style: str,
    color: str,
    bg_concept: str | None,
    num_variations: int,
    output_dir: Path,
    action: str,
) -> None:
    """Generate social posts based on wizard selections."""
    reporter = get_reporter(config.json_output)

    if action == "save-config":
        typer.secho("📝 Configuration saved. Run again to generate.", fg="cyan")
        return

    dry_run = action == "dry-run"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    for i in range(1, num_variations + 1):
        if num_variations > 1:
            typer.echo(f"\n✨ Generating variation {i}/{num_variations}...")

        background_image_path = None

        # Generate background if requested
        if bg_concept:
            try:
                bg_result = generate_background(
                    bg_concept=bg_concept,
                    bg_seed=None,
                    provider=getattr(config.image, "provider", "pollinations"),
                    config=config,
                )
                background_image_path = Path(bg_result["path"])
            except Exception as e:
                reporter.error(f"Background generation failed: {e}")
                failed += 1
                continue

        # Generate social post
        try:
            result = generate_social_post(
                text=text,
                style=style,
                color=color,
                custom_color=None,
                format_name="square",
                output_dir=output_dir,
                dry_run=dry_run,
                background_image_path=background_image_path,
            )

            if dry_run:
                reporter.dry_run(f"Would create: {result['path']}")
            else:
                typer.secho(f"   ✓ Created: {Path(result['path']).name}", fg="green")

            successful += 1

        except Exception as e:
            reporter.error(f"Post generation failed: {e}")
            failed += 1

    # Summary
    typer.secho("\n" + "=" * 50, fg="cyan")
    if dry_run:
        typer.secho(f"🔍 DRY RUN: Would create {successful} posts", fg="cyan")
    else:
        typer.secho(f"✅ Successfully created {successful} posts", fg="green")
        if failed > 0:
            typer.secho(f"❌ Failed: {failed} posts", fg="red")
        typer.secho(f"📁 Location: {output_dir}", fg="cyan")
    typer.secho("=" * 50 + "\n", fg="cyan")
