"""Interactive CLI utilities for user-friendly prompts.

This module is in core/ (not commands/) to avoid circular imports.
It's used by both core modules and CLI commands.
"""

try:
    import questionary
except ImportError as e:
    raise ImportError(
        "Interactive mode requires 'questionary' package.\n"
        "Install with: pip install agency-toolkit[interactive]"
    ) from e

from agency_toolkit.config import COLORS
from agency_toolkit.core.discovery import (
    get_available_briefing_types,
    get_available_social_formats,
    get_available_social_styles,
    get_available_structure_types,
    get_choice_list,
    get_seed_choice_list,
)


def prompt_for_social_post() -> dict:
    """Interactive prompt for social post generation.

    Guides user through text, style, color, and format selection.

    Returns:
        Dict with keys: text, style, color, format, bg_concept (optional)
    """
    # Prompt for message text
    text = questionary.text(
        "What's your message? (max 280 characters)",
        validate=lambda x: len(x) > 0 and len(x) <= 280,
    ).ask()

    if not text:
        return None

    # Prompt for style using discovery
    styles = get_available_social_styles()
    style = questionary.select(
        "Choose template style:",
        choices=get_choice_list(styles),
        default="modern",
    ).ask()

    # Prompt for color
    color_choices = [{"name": f"{k:12} - {v}", "value": k} for k, v in COLORS.items()]
    color = questionary.select(
        "Choose color:",
        choices=color_choices,
        default="blue",
    ).ask()

    # Prompt for format using discovery
    formats = get_available_social_formats()
    format_choice = questionary.select(
        "Choose format:",
        choices=get_choice_list(formats),
        default="square",
    ).ask()

    # Optional: Ask if they want an AI background
    add_bg = questionary.confirm("Add AI-generated background?", default=False).ask()

    bg_concept = None
    if add_bg:
        # Show registry seeds
        seed_choices = get_seed_choice_list()
        # Add "custom" option
        seed_choices.append(
            {"name": "custom      - Describe your own concept", "value": "custom"}
        )

        bg_choice = questionary.select(
            "Choose background concept:",
            choices=seed_choices,
            default=seed_choices[0]["value"] if seed_choices else None,
        ).ask()

        if bg_choice == "custom":
            bg_concept = questionary.text("Describe your background concept:").ask()
        else:
            bg_concept = f"registry:{bg_choice}"

    return {
        "text": text,
        "style": style,
        "color": color,
        "format": format_choice,
        "bg_concept": bg_concept,
    }


def prompt_for_briefing_type() -> str:
    """Interactive prompt for briefing type selection.

    Returns:
        Briefing type (web, video, brand, campaign)
    """
    types = get_available_briefing_types()
    return questionary.select(
        "Choose briefing template:",
        choices=get_choice_list(types),
        default="web",
    ).ask()


def prompt_for_structure_type() -> str:
    """Interactive prompt for folder structure type selection.

    Returns:
        Structure type (web, video, brand, campaign)
    """
    types = get_available_structure_types()
    return questionary.select(
        "Choose folder structure template:",
        choices=get_choice_list(types),
        default="web",
    ).ask()


def confirm_action(message: str = "Proceed?") -> bool:
    """Show confirmation prompt and ask for user confirmation.

    Args:
        message: Confirmation message to display

    Returns:
        True if user confirmed, False otherwise
    """
    return questionary.confirm(message, auto_enter=False).ask()


def display_summary(title: str, items: dict[str, str]) -> None:
    """Display a formatted summary of items.

    Args:
        title: Summary title
        items: Dict of key-value pairs to display
    """
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")
    for key, value in items.items():
        print(f"  {key}: {value}")
    print(f"{'=' * 50}\n")


def prompt_with_fallback(
    prompt_text: str, interactive: bool = False, default: str = None
) -> str:
    """Prompt for input with optional interactive mode.

    Args:
        prompt_text: Prompt message
        interactive: If True, use questionary; if False, use standard input
        default: Default value if skipped

    Returns:
        User input or default value
    """
    if interactive:
        return questionary.text(prompt_text, default=default).ask()
    else:
        return input(f"{prompt_text}: ") or default


def prompt_for_selection(
    prompt_text: str,
    choices: list[dict],
    id_key: str = "id",
    name_key: str = "name",
    description_key: str = "description",
) -> dict:
    """Generic selection prompt from a list of items.

    Args:
        prompt_text: Prompt message to display
        choices: List of dicts representing items
        id_key: Key for the item ID
        name_key: Key for the item name
        description_key: Key for the item description

    Returns:
        Selected item dict
    """
    choice_list = [
        {
            "name": f"{item.get(name_key, 'Unknown')} - {item.get(description_key, '')}",
            "value": item,
        }
        for item in choices
    ]

    return questionary.select(prompt_text, choices=choice_list).ask()
