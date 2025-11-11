"""Template management for project structures."""

import logging

from agency_toolkit.config import STRUCTURE_TEMPLATES_DIR
from agency_toolkit.utils import load_template

logger = logging.getLogger(__name__)


def get_template(structure_type: str) -> dict:
    """Load structure template by type.

    Args:
        structure_type: Type (print, web, social, video)

    Returns:
        Template dict with 'folders' list
    """
    template_path = STRUCTURE_TEMPLATES_DIR / f"{structure_type}.json"

    if not template_path.exists():
        logger.warning(f"Template not found: {template_path}, using default")
        template_path = STRUCTURE_TEMPLATES_DIR / "default.json"

    try:
        return load_template(template_path)
    except Exception as e:
        logger.warning(f"Failed to load template: {e}, using basic structure")
        return {"folders": ["01_Briefing", "02_Design", "03_Assets", "04_Final"]}
