"""Template and question loading for briefings."""

import logging

from agency_toolkit.config import BRIEFING_TEMPLATES_DIR
from agency_toolkit.utils import load_template

logger = logging.getLogger(__name__)


def load_briefing_questions(briefing_type: str = "default") -> dict:
    """Load briefing questions template from JSON file.

    Args:
        briefing_type: Type of briefing template (default, web, video).

    Returns:
        Dict with template structure: {"required": [...], "optional": [...]}

    Raises:
        FileNotFoundError: If template file not found.
        ValueError: If JSON is invalid.
    """
    template_path = BRIEFING_TEMPLATES_DIR / f"{briefing_type}.json"

    if not template_path.exists():
        available = [f.stem for f in BRIEFING_TEMPLATES_DIR.glob("*.json")]
        raise FileNotFoundError(
            f"Template '{briefing_type}' not found at {template_path}. "
            f"Available templates: {', '.join(available)}"
        )

    try:
        template_data = load_template(template_path)
        return template_data
    except Exception as e:
        raise ValueError(f"Failed to load template: {e}") from e
