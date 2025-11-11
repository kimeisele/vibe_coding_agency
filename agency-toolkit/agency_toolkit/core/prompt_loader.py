"""Prompt Registry loader for Agency Toolkit.

Provides convenient access to prompts stored in JSON files.
"""

from dataclasses import asdict
from pathlib import Path
from typing import Any

from agency_toolkit.core.prompt_registry import Prompt, PromptRegistry

# Global registry instance (lazy-loaded)
_registry: PromptRegistry | None = None


def get_registry() -> PromptRegistry:
    """Get or create the global PromptRegistry instance.

    Returns:
        Initialized PromptRegistry pointing to agency_toolkit/prompts/
    """
    global _registry
    if _registry is None:
        prompts_dir = Path(__file__).parent.parent / "prompts"
        _registry = PromptRegistry(prompts_dir=prompts_dir)
    return _registry


def _prompt_to_dict(prompt: Prompt | None) -> dict[str, Any] | None:
    """Convert a Prompt object to a dictionary.

    Args:
        prompt: Prompt dataclass instance or None

    Returns:
        Dict with all prompt fields, or None
    """
    if prompt is None:
        return None
    return asdict(prompt)


def get_prompt(prompt_id: str) -> dict[str, Any] | None:
    """Get a prompt by ID from the registry.

    Args:
        prompt_id: Unique prompt identifier (e.g., "default", "code", "creative")

    Returns:
        Prompt dict with all metadata, or None if not found

    Example:
        >>> prompt = get_prompt("creative")
        >>> print(prompt["prompt"])  # Get the actual prompt text
    """
    registry = get_registry()
    prompt = registry.get(prompt_id)
    return _prompt_to_dict(prompt)


def get_profile(profile_id: str) -> dict[str, Any] | None:
    """Get an AI profile (mistral profile) by ID.

    Args:
        profile_id: Profile ID (e.g., "default", "code", "creative")

    Returns:
        Profile dict with model, temperature, system_prompt, or None

    Example:
        >>> profile = get_profile("code")
        >>> model = profile.get("model")  # e.g., "mistral-small-latest"
        >>> temp = profile.get("temperature")  # e.g., 0.2
    """
    return get_prompt(profile_id)


def list_profiles() -> list[dict[str, Any]]:
    """List all available AI profiles.

    Returns:
        List of profile dicts from the profiles category
    """
    registry = get_registry()
    prompts = registry.list(category="profiles")
    return [_prompt_to_dict(p) for p in prompts]


def list_prompts(category: str | None = None) -> list[dict[str, Any]]:
    """List prompts, optionally filtered by category.

    Args:
        category: Optional category filter (e.g., "profiles", "templates")

    Returns:
        List of prompt dicts matching the filter
    """
    registry = get_registry()
    prompts = registry.list(category=category)
    return [_prompt_to_dict(p) for p in prompts]


def render_prompt(prompt_id: str, variables: dict[str, Any]) -> str | None:
    """Render a prompt with variable substitution.

    Args:
        prompt_id: Unique prompt identifier
        variables: Dict of variables to substitute in the prompt

    Returns:
        Rendered prompt text with variables substituted, or None if prompt not found

    Example:
        >>> result = render_prompt("task", {"task": "write code", "lang": "Python"})
    """
    registry = get_registry()
    return registry.render(prompt_id, variables)
