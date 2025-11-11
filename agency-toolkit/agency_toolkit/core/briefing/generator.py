"""Briefing generation orchestrator."""

import logging
from datetime import datetime
from pathlib import Path

from agency_toolkit.core.briefing.io import write_markdown
from agency_toolkit.core.briefing.models import BriefingData
from agency_toolkit.core.briefing.pdf_writer import write_pdf
from agency_toolkit.utils import ensure_output_dir, sanitize_name

logger = logging.getLogger(__name__)

# Check PDF availability
try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def generate(
    briefing_data: BriefingData,
    format_type: str,
    output_dir: Path = Path("./output/briefings"),
    dry_run: bool = False,
    step_context: dict | None = None,
) -> dict:
    """Generate project briefing in the specified format.

    Args:
        briefing_data: BriefingData model instance
        format_type: Output format ('pdf' or 'md')
        output_dir: Output directory
        dry_run: If True, return path without creating file
        step_context: Optional dictionary with AI-generated content from workflow steps

    Returns:
        Dict with keys: path (str), format (str)

    Raises:
        ValueError: If format type is unsupported
        ImportError: If PDF generation requested but fpdf not available
    """
    # Generate filename
    client_slug = sanitize_name(briefing_data.client_name)
    project_slug = sanitize_name(briefing_data.project_name)
    timestamp_str = datetime.now().strftime("%Y%m%d")
    filename = (
        f"briefing_{client_slug}_{project_slug}_{timestamp_str}.{format_type.lower()}"
    )
    output_path = output_dir / filename

    if dry_run:
        logger.info(f"[DRY RUN] Would create briefing file at {output_path}")
        return {"path": str(output_path), "format": format_type.lower()}

    ensure_output_dir(output_dir)

    if format_type.lower() == "pdf":
        if not FPDF_AVAILABLE:
            raise ImportError(
                "fpdf is not available. Install it with: pip install fpdf"
            )
        write_pdf(briefing_data, output_path, step_context)
    elif format_type.lower() == "md":
        write_markdown(briefing_data, output_path)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")

    logger.info(f"Generated briefing file: {output_path}")
    return {"path": str(output_path), "format": format_type.lower()}
