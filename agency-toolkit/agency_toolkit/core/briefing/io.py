"""JSON loading and markdown writing for briefings."""

import json
import logging
from datetime import datetime
from pathlib import Path

from agency_toolkit.core.briefing.models import BriefingData

logger = logging.getLogger(__name__)


def load_from_json(json_path: Path) -> BriefingData:
    """Load briefing data from JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        BriefingData object

    Raises:
        FileNotFoundError: If file not found
        ValueError: If JSON is invalid
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    try:
        with open(json_path) as f:
            data = json.load(f)

        if isinstance(data.get("deadline"), str):
            data["deadline"] = datetime.strptime(data["deadline"], "%Y-%m-%d").date()

        return BriefingData(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


def write_markdown(briefing_data: BriefingData, output_path: Path) -> None:
    """Write briefing to Markdown file.

    Args:
        briefing_data: BriefingData instance
        output_path: Output file path
    """
    content = f"""# Project Briefing

## Client Information
- **Client:** {briefing_data.client_name}
- **Project:** {briefing_data.project_name}
- **Type:** {briefing_data.project_type or 'N/A'}

## Timeline & Budget
- **Deadline:** {briefing_data.deadline}
- **Budget:** {f'${briefing_data.budget:,.2f}' if briefing_data.budget else 'N/A'}

## Project Details

### Objectives
{briefing_data.objectives or 'N/A'}

### Target Audience
{briefing_data.target_audience or 'N/A'}

### Deliverables
"""
    if briefing_data.deliverables:
        for item in briefing_data.deliverables:
            content += f"- {item}\n"
    else:
        content += "N/A\n"

    if briefing_data.notes:
        content += f"\n## Additional Notes\n{briefing_data.notes}\n"

    content += f"\n---\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    output_path.write_text(content)
