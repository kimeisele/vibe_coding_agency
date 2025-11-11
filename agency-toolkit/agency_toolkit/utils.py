"""Utilities for validation and path handling."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import toml

from agency_toolkit.core.phoenix_config import UniversalConfig
from agency_toolkit.exceptions import TemplateValidationError
from agency_toolkit.models import Config

logger = logging.getLogger(__name__)


def _load_toml_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load config file from standard TOML locations.

    Priority (highest to lowest):
        1. Project config (./config.toml in current working directory)
        2. User config (~/.config/agency-toolkit/config.toml)
        3. Explicitly provided config_path

    Args:
        config_path: Optional explicit path to config.toml file

    Returns:
        Merged config dict from all sources (empty dict if no configs found)
    """
    configs_to_merge = []

    # Priority 3: Explicit config path (lowest)
    if config_path and config_path.exists():
        configs_to_merge.append(("explicit", config_path))

    # Priority 2: User config directory
    user_config_path = Path.home() / ".config" / "agency-toolkit" / "config.toml"
    if user_config_path.exists():
        configs_to_merge.append(("user", user_config_path))

    # Priority 1: Project config (highest - current directory)
    project_config_path = Path.cwd() / "config.toml"
    if project_config_path.exists():
        configs_to_merge.append(("project", project_config_path))

    # Merge all configs (later ones override earlier ones)
    merged_config: dict[str, Any] = {}
    for config_type, path in configs_to_merge:
        config = toml.load(path)

        # Merge settings section
        if "settings" in config:
            merged_config.update(config["settings"])

        # Merge image section separately
        if "image" in config:
            if "image" not in merged_config:
                merged_config["image"] = {}
            merged_config["image"].update(config["image"])

    return merged_config


def load_config(config_path: Path | None = None, validate: bool = True) -> Config:
    """Load and validate configuration from TOML files and defaults.

    Priority (highest to lowest):
        1. Project config (./config.toml in current working directory)
        2. User config (~/.config/agency-toolkit/config.toml)
        3. Phoenix UniversalConfig defaults
        4. Hard-coded defaults

    Args:
        config_path: Optional explicit path to config.toml file
        validate: Whether to validate (kept for backward compatibility)

    Returns:
        A Pydantic Config model with loaded configuration values.
    """
    try:
        # Step 1: Load TOML configs (this takes priority)
        toml_config = _load_toml_config(config_path)

        # Step 2: Load UniversalConfig to get defaults and validate
        universal_config = UniversalConfig.create_default()

        # Step 3: Merge TOML values over UniversalConfig defaults
        # TOML values override the universal config defaults
        legacy_config_data = {
            "output_dir": Path(
                toml_config.get("output_dir", universal_config.shell.output_dir)
            ),
            "social_style": toml_config.get(
                "social_style", universal_config.task.social_style
            ),
            "social_color": toml_config.get(
                "social_color", universal_config.task.social_color
            ),
            "social_format": toml_config.get("social_format", "square"),
            "briefing_type": toml_config.get("briefing_type", "default"),
            "mistral_model": toml_config.get("mistral_model", "mistral-small-latest"),
            "mistral_temperature": toml_config.get("mistral_temperature", 0.7),
            "mistral_max_tokens": toml_config.get("mistral_max_tokens", 1000),
            "json_output": toml_config.get("json_output", False),
        }

        # Handle image config
        if "image" in toml_config:
            from agency_toolkit.models import ImageGenerationConfig

            legacy_config_data["image"] = ImageGenerationConfig(**toml_config["image"])

        return Config(**legacy_config_data)

    except Exception as e:
        # Provide a clear error message on failure
        raise ValueError(f"Configuration error: {e}") from e


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)


def sanitize_name(name: str) -> str:
    """Convert name to filesystem-safe slug."""
    import re

    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[-\s]+", "-", name)
    return name.strip("-")


def ensure_output_dir(path: Path) -> Path:
    """Ensure output directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_template(template_path: Path) -> dict[str, Any]:
    """Load and validate JSON template."""
    if not template_path.exists():
        raise TemplateValidationError(f"Template not found: {template_path}")

    try:
        with open(template_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise TemplateValidationError(f"Invalid JSON in {template_path}: {e}")
