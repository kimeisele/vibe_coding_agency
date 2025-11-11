"""Helper functions for interactive wizards."""

from pathlib import Path
from typing import Any

import typer


def prompt_text(
    prompt_text: str,
    default: str | None = None,
    required: bool = True,
) -> str:
    """Prompt user for text input."""
    prompt_str = prompt_text
    if default:
        prompt_str += f" [{default}]"
    prompt_str += ": "

    while True:
        value = typer.prompt(prompt_str, default=default)
        if required and not value:
            typer.secho("⚠️  This field is required", fg="yellow")
            continue
        return value


def prompt_choice(
    prompt_text: str,
    choices: list[tuple[str, str]],
    default: str | None = None,
) -> str:
    """Prompt user to choose from options."""
    typer.echo(f"\n📋 {prompt_text}")

    for i, (key, description) in enumerate(choices, 1):
        marker = "✓" if key == default else " "
        typer.echo(f"   {marker} {i}. {key:12} - {description}")

    # Get choice
    prompt_str = f"Choose (1-{len(choices)}"
    if default:
        default_idx = next(i for i, (k, _) in enumerate(choices, 1) if k == default)
        prompt_str += f", default {default_idx}"
    prompt_str += "): "

    while True:
        try:
            choice_idx = typer.prompt(prompt_str, type=int)
            if 1 <= choice_idx <= len(choices):
                return choices[choice_idx - 1][0]
            else:
                typer.secho(f"❌ Please choose between 1 and {len(choices)}", fg="red")
        except ValueError:
            typer.secho("❌ Please enter a valid number", fg="red")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """Prompt user for yes/no choice."""
    default_str = "Y/n" if default else "y/N"
    response = typer.prompt(f"{prompt_text} [{default_str}]", default="").lower()

    if response in ("y", "yes"):
        return True
    elif response in ("n", "no"):
        return False
    else:
        return default


def prompt_number(
    prompt_text: str,
    min_val: int = 1,
    max_val: int = 100,
    default: int = 1,
) -> int:
    """Prompt user for number input."""
    prompt_str = f"{prompt_text} [{min_val}-{max_val}, default {default}]: "

    while True:
        try:
            value = typer.prompt(prompt_str, type=int, default=default)
            if min_val <= value <= max_val:
                return value
            else:
                typer.secho(
                    f"❌ Please enter a number between {min_val} and {max_val}",
                    fg="red",
                )
        except ValueError:
            typer.secho("❌ Please enter a valid number", fg="red")


def prompt_path(prompt_text: str, default: Path) -> Path:
    """Prompt user for file path."""
    default_str = str(default)
    response = typer.prompt(f"{prompt_text} [{default_str}]", default=default_str)
    return Path(response)


def show_header(title: str) -> None:
    """Display wizard header."""
    typer.secho(f"\n{'═' * 50}", fg="cyan")
    typer.secho(f"  {title}", fg="cyan", bold=True)
    typer.secho(f"{'═' * 50}\n", fg="cyan")


def show_summary(data: dict[str, Any]) -> None:
    """Display summary of choices."""
    typer.secho("\n📊 Summary of Your Choices:", fg="cyan", bold=True)
    for key, value in data.items():
        # Format key nicely (e.g., "bg_concept" -> "Background Concept")
        formatted_key = key.replace("_", " ").title()
        typer.echo(f"   {formatted_key}: {value}")
    typer.echo()


def confirm_proceed(message: str = "Proceed with these settings?") -> bool:
    """Ask for confirmation before proceeding."""
    return prompt_yes_no(f"\n✨ {message}", default=True)
