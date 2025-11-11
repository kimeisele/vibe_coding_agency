"""Image Generation Wizard (WU-7.3)."""

from pathlib import Path

import typer

from agency_toolkit import image_gen
from agency_toolkit.core.reporter import get_reporter

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


def image_wizard(config) -> None:
    """Interactive wizard for image generation."""
    show_header("🎨 Image Generator Wizard")

    # Step 1: Image description
    typer.echo("Step 1: Describe the image")
    typer.echo("   Example: 'futuristic city at sunset'\n")
    description = prompt_text("Image description", required=True)

    # Step 2: Image size
    size_choices = [
        ("square", "1080x1080 - Social media"),
        ("landscape", "1920x1080 - Website hero"),
        ("portrait", "1080x1920 - Mobile"),
        ("custom", "Enter custom dimensions"),
    ]
    size = prompt_choice("\nStep 2: Image size?", size_choices, default="square")

    custom_width = None
    custom_height = None
    if size == "custom":
        custom_width = prompt_number(
            "\nWidth in pixels", min_val=256, max_val=4096, default=1080
        )
        custom_height = prompt_number(
            "Height in pixels", min_val=256, max_val=4096, default=1080
        )

    # Step 3: Use seed template
    use_template = prompt_yes_no("\nStep 3: Use seed template?", default=False)
    seed = None
    if use_template:
        template_choices = [
            ("moody", "Dark, atmospheric"),
            ("corporate", "Professional, clean"),
            ("playful", "Bright, fun, vibrant"),
            ("minimal", "Simple, zen-like"),
        ]
        seed = prompt_choice("\nChoose template", template_choices, default="corporate")

    # Step 4: Number of variations
    num_variations = prompt_number(
        "\nStep 4: How many variations?",
        min_val=1,
        max_val=5,
        default=1,
    )

    # Step 5: Output directory
    default_output = Path("./output/images")
    output_dir = prompt_path("\nStep 5: Output directory", default_output)

    # Summary
    size_display = (
        f"{size} (custom: {custom_width}x{custom_height})" if size == "custom" else size
    )
    data = {
        "description": description,
        "size": size_display,
        "template": seed or "None",
        "variations": num_variations,
        "output_directory": str(output_dir),
    }
    show_summary(data)

    if not confirm_proceed("Ready to generate images?"):
        typer.secho("✋ Cancelled. No images generated.", fg="yellow")
        return

    # Generate images
    _generate_images(
        config,
        description,
        size,
        custom_width,
        custom_height,
        seed,
        num_variations,
        output_dir,
    )


def _generate_images(
    config,
    description: str,
    size: str,
    custom_width: int | None,
    custom_height: int | None,
    seed: str | None,
    num_variations: int,
    output_dir: Path,
) -> None:
    """Generate images based on wizard selections."""
    reporter = get_reporter(config.json_output)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Map size to dimensions
    size_map = {
        "square": (1080, 1080),
        "landscape": (1920, 1080),
        "portrait": (1080, 1920),
        "custom": (custom_width or 1080, custom_height or 1080),
    }
    width, height = size_map[size]

    # Parse seed if it's a template name
    seed_value = None
    if seed:
        # Map template names to seed values if needed
        template_map = {"moody": 1, "corporate": 2, "playful": 3, "minimal": 4}
        seed_value = template_map.get(seed, None)

    successful = 0
    failed = 0

    for i in range(1, num_variations + 1):
        if num_variations > 1:
            typer.echo(f"\n✨ Generating image {i}/{num_variations}...")

        try:
            result = image_gen.generate_image(
                prompt=description,
                width=width,
                height=height,
                seed=seed_value,
                provider=getattr(config.image, "provider", "pollinations")
                if hasattr(config, "image")
                else "pollinations",
                config=config,
            )

            # Save to output directory
            output_path = output_dir / f"image_{i:03d}_{result['seed']}.png"
            result_path = Path(result["path"])
            if result_path != output_path:
                # Copy/rename if path differs
                import shutil

                shutil.copy(result_path, output_path)

            typer.secho(f"   ✓ Created: {output_path.name}", fg="green")
            successful += 1

        except Exception as e:
            reporter.error(f"Image generation failed: {e}")
            failed += 1

    # Summary
    typer.secho("\n" + "=" * 50, fg="cyan")
    typer.secho(f"✅ Successfully created {successful} images", fg="green")
    if failed > 0:
        typer.secho(f"❌ Failed: {failed} images", fg="red")
    typer.secho(f"📁 Location: {output_dir}", fg="cyan")
    typer.secho("=" * 50 + "\n", fg="cyan")
