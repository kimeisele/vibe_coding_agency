"""Template loading and management for social media posts."""

import logging

from agency_toolkit.config import SOCIAL_TEMPLATES_DIR
from agency_toolkit.utils import load_template

logger = logging.getLogger(__name__)


def get_template(style: str) -> dict:
    """Load template by style name.

    Args:
        style: Template style name (modern, minimal, bold)

    Returns:
        Template configuration dict

    Raises:
        ValueError: If template style is not found
    """
    # Get available templates
    available_templates = sorted(
        [p.stem for p in SOCIAL_TEMPLATES_DIR.glob("*.json") if p.is_file()]
    )

    template_path = SOCIAL_TEMPLATES_DIR / f"{style}.json"

    if not template_path.exists():
        # User provided an invalid style - fail loudly with clear error
        available_str = ", ".join(available_templates)
        raise ValueError(
            f"Invalid social template style: '{style}'. "
            f"Available styles: {available_str}"
        )

    try:
        return load_template(template_path)
    except Exception as e:
        logger.error(f"Failed to load template {template_path}: {e}")
        raise ValueError(
            f"Failed to load template '{style}': {e}. "
            f"Available styles: {', '.join(available_templates)}"
        )
