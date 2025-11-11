"""AI Profile management for Mistral and other providers.

Profiles define model, temperature, and system prompt settings.
"""

import json
from pathlib import Path
from typing import Any


def get_profile(profile_id: str) -> dict[str, Any] | None:
    """Get an AI profile by ID.

    Args:
        profile_id: Profile ID (e.g., "default", "code", "creative")

    Returns:
        Profile dict with model, temperature, system_prompt, etc., or None

    Example:
        >>> profile = get_profile("code")
        >>> model = profile["model"]
        >>> temp = profile["temperature"]
        >>> prompt = profile["prompt"]  # system prompt
    """
    profiles_dir = Path(__file__).parent.parent / "prompts" / "profiles"
    profile_file = profiles_dir / f"{profile_id}.json"

    if not profile_file.exists():
        return None

    with open(profile_file) as f:
        return json.load(f)


def list_profiles() -> list[dict[str, Any]]:
    """List all available AI profiles.

    Returns:
        List of profile dicts, each containing model, temperature, system_prompt
    """
    profiles_dir = Path(__file__).parent.parent / "prompts" / "profiles"
    profiles = []

    if not profiles_dir.exists():
        return profiles

    for profile_file in sorted(profiles_dir.glob("*.json")):
        try:
            with open(profile_file) as f:
                profile = json.load(f)
                profiles.append(profile)
        except Exception:
            pass  # Skip invalid files

    return profiles


def get_system_prompt(profile_id: str) -> str | None:
    """Get the system prompt for a profile.

    Args:
        profile_id: Profile ID

    Returns:
        System prompt text, or None if profile not found
    """
    profile = get_profile(profile_id)
    if profile:
        return profile.get("prompt")
    return None


def get_model_config(profile_id: str) -> dict[str, Any] | None:
    """Get model configuration for a profile.

    Args:
        profile_id: Profile ID

    Returns:
        Dict with model, temperature, and other settings, or None

    Example:
        >>> config = get_model_config("creative")
        >>> # Use in AI provider:
        >>> provider.generate(
        ...     prompt=user_prompt,
        ...     model=config["model"],
        ...     temperature=config["temperature"],
        ...     system_prompt=config.get("prompt")
        ... )
    """
    profile = get_profile(profile_id)
    if profile:
        return {
            "model": profile.get("model"),
            "temperature": profile.get("temperature"),
            "system_prompt": profile.get("prompt"),
        }
    return None
