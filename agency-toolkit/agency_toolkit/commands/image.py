"""AI image generation command."""

import json
import logging

import typer

from agency_toolkit.wizards import image_wizard

logger = logging.getLogger(__name__)

image_command = typer.Typer(help="Generate AI images", invoke_without_command=True)


@image_command.callback()
def image_callback(ctx: typer.Context) -> None:
    """Handle wizard mode when no subcommand is provided."""
    # If no subcommand and no arguments, launch wizard
    if ctx.invoked_subcommand is None:
        config = ctx.obj
        image_wizard(config)
        raise typer.Exit()


@image_command.command("generate")
def image(
    ctx: typer.Context,
    prompt: str,
    seed: int | None = typer.Option(None, help="Random seed (default: auto)"),
    width: int = typer.Option(1024, help="Image width in pixels"),
    height: int = typer.Option(1024, help="Image height in pixels"),
    provider: str = typer.Option(
        "pollinations", help="Image provider (replicate, pollinations)"
    ),
) -> None:
    """Generate AI image from text prompt.

    Example:
        toolkit image "modern minimalist office with large windows"
        toolkit image "sunset" --provider pollinations
    """
    from agency_toolkit import image_gen

    config = ctx.obj

    try:
        result = image_gen.generate_image(
            prompt=prompt,
            seed=seed,
            width=width,
            height=height,
            provider=provider,
            config=config,
        )

        output_data = {"status": "success", "module": "image", **result}

        if config.json_output:
            print(json.dumps(output_data))
        else:
            typer.secho(f"✅ Image generated: {result['path']}", fg="green")
            typer.secho(f"🎲 Seed: {result['seed']}", fg="cyan")
            typer.secho(f"💰 Cost: ${result['cost']:.4f}", fg="cyan")
            typer.secho(f"🔌 Provider: {result['provider']}", fg="cyan")

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        output_data = {"status": "error", "module": "image", "message": str(e)}

        if not config.json_output:
            typer.secho(f"❌ Error: {e}", fg="red")

        print(json.dumps(output_data))
        raise typer.Exit(code=1)
