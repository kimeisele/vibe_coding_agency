"""Dynamic discovery system for interactive prompts.

This module provides helpers to discover and present available options from
the codebase and registry, eliminating guesswork for users.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_available_seeds() -> dict[str, dict[str, Any]]:
    """Get all available seed templates from registry.

    Returns:
        Dict mapping seed ID to seed metadata:
        {
            "moody": {
                "name": "Moody & Dramatic",
                "description": "Dark, cinematic, introspective",
                ...
            },
            ...
        }
    """
    registry_path = (
        Path(__file__).parent.parent.parent / "registry" / "seeds" / "templates.json"
    )

    if not registry_path.exists():
        logger.warning(f"Registry not found at {registry_path}")
        return {}

    try:
        with open(registry_path) as f:
            data = json.load(f)
        return data.get("templates", {})
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        return {}


def get_available_social_styles() -> dict[str, str]:
    """Get available social media post styles.

    Returns:
        Dict mapping style ID to description:
        {
            "modern": "Clean, tech-forward, gradient backgrounds",
            "bold": "High contrast, impact-focused",
            ...
        }
    """
    # These are defined in core/social/templates.py
    return {
        "modern": "Clean, tech-forward, gradient backgrounds",
        "bold": "High contrast, impact-focused, strong typography",
        "minimal": "Subtle, elegant, lots of white space",
        "playful": "Fun, colorful, casual and friendly",
    }


def get_available_social_formats() -> dict[str, str]:
    """Get available social media post formats.

    Returns:
        Dict mapping format ID to description:
        {
            "square": "1:1 (1080x1080) - Instagram, Facebook",
            ...
        }
    """
    return {
        "square": "1:1 (1080x1080) - Instagram, Facebook",
        "landscape": "16:9 (1920x1080) - YouTube, LinkedIn",
        "portrait": "9:16 (1080x1920) - Instagram Stories, TikTok",
        "twitter": "16:9 (1200x675) - Twitter/X cards",
    }


def get_available_briefing_types() -> dict[str, str]:
    """Get available briefing types.

    Returns:
        Dict mapping type ID to description:
        {
            "web": "Web development project briefing",
            ...
        }
    """
    return {
        "web": "Web development project briefing (multi-page sites, apps)",
        "video": "Video production briefing (commercials, explainers)",
        "brand": "Brand identity & design briefing (logos, guidelines)",
        "campaign": "Marketing campaign briefing (multi-channel)",
    }


def get_available_structure_types() -> dict[str, str]:
    """Get available project structure types.

    Returns:
        Dict mapping type ID to description:
        {
            "web": "Standard web project structure",
            ...
        }
    """
    return {
        "web": "Standard web project structure (HTML/CSS/JS)",
        "video": "Video production project structure (footage, exports)",
        "brand": "Brand identity structure (assets, guidelines)",
        "campaign": "Marketing campaign structure (channels, creative)",
    }


def format_choice_for_display(key: str, description: str, max_width: int = 60) -> str:
    """Format a choice for display in questionary prompts.

    Args:
        key: The choice key/ID
        description: The choice description
        max_width: Maximum width for description

    Returns:
        Formatted string like "modern - Clean, tech-forward, gradient..."
    """
    # Truncate description if too long
    if len(description) > max_width:
        description = description[: max_width - 3] + "..."

    return f"{key:12} - {description}"


def get_choice_list(choices_dict: dict[str, str], max_width: int = 60) -> list[dict]:
    """Convert choices dict to questionary choice list.

    Args:
        choices_dict: Dict mapping ID to description
        max_width: Maximum width for descriptions

    Returns:
        List of dicts for questionary: [{"name": "display", "value": "id"}, ...]
    """
    return [
        {"name": format_choice_for_display(key, desc, max_width), "value": key}
        for key, desc in choices_dict.items()
    ]


def get_seed_choice_list() -> list[dict]:
    """Get formatted choice list for seed templates.

    Returns:
        List of dicts for questionary prompts
    """
    seeds = get_available_seeds()
    choices = {}

    for seed_id, seed_data in seeds.items():
        name = seed_data.get("name", seed_id)
        description = seed_data.get("description", "")
        choices[seed_id] = f"{name} - {description}"

    return get_choice_list(choices)
