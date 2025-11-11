"""PDF writer for project briefings."""

import logging
import threading
from collections.abc import Callable
from functools import wraps
from pathlib import Path

from fpdf import FPDF

from agency_toolkit.core.briefing.models import BriefingData
from agency_toolkit.core.briefing.pdf_sections import (
    write_ai_content,
    write_client_info,
    write_deliverables,
    write_details,
    write_header,
    write_notes,
    write_timeline,
)

logger = logging.getLogger(__name__)


class PDFTimeoutError(Exception):
    """Raised when PDF generation times out."""

    pass


def timeout_handler(timeout_seconds: int = 10) -> Callable:
    """Decorator to add timeout to PDF operations.

    Args:
        timeout_seconds: Maximum seconds to wait (default: 10, reduced from 30)

    Returns:
        Decorated function

    Note:
        Uses threading-based timeout instead of signal.alarm() for cross-platform compatibility.
        If timeout occurs, a PDFTimeoutError is raised with diagnostic information.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=timeout_seconds)

            if thread.is_alive():
                # Thread is still running (timed out)
                logger.warning(
                    f"PDF generation timed out after {timeout_seconds}s. "
                    "This may be due to font loading. Using fallback approach."
                )
                raise PDFTimeoutError(
                    f"PDF generation timed out after {timeout_seconds} seconds. "
                    "This may be due to font loading issues."
                )

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator


@timeout_handler(timeout_seconds=30)
def _generate_pdf_with_timeout(
    briefing_data: BriefingData, pdf: FPDF, step_context: dict | None = None
) -> None:
    """Generate PDF sections (with timeout protection).

    Args:
        briefing_data: Briefing data model
        pdf: FPDF instance
        step_context: Optional dictionary with AI-generated content from workflow steps

    Raises:
        PDFTimeoutError: If generation takes too long
    """
    # Write sections
    write_header(pdf)
    write_client_info(
        pdf,
        briefing_data.client_name,
        briefing_data.project_name,
        briefing_data.project_type,
    )
    write_timeline(pdf, briefing_data.deadline, briefing_data.budget)
    write_details(pdf, briefing_data.objectives, briefing_data.target_audience)
    write_deliverables(pdf, briefing_data.deliverables)
    # NEW: Write AI-generated content if available
    write_ai_content(pdf, step_context)
    write_notes(pdf, briefing_data.notes)


def write_pdf(
    briefing_data: BriefingData, output_path: Path, step_context: dict | None = None
) -> None:
    """Write briefing data to PDF file.

    Args:
        briefing_data: Briefing data model
        output_path: Output PDF path
        step_context: Optional dictionary with AI-generated content from workflow steps

    Raises:
        PDFTimeoutError: If PDF generation times out
        FileNotFoundError: If output directory doesn't exist

    Note:
        If font loading times out, retries with fallback approach.
    """
    if not output_path.parent.exists():
        raise FileNotFoundError(
            f"Output directory does not exist: {output_path.parent}"
        )

    pdf = FPDF()
    pdf.add_page()

    try:
        # Try to generate PDF with timeout protection
        _generate_pdf_with_timeout(briefing_data, pdf, step_context)
    except PDFTimeoutError as e:
        # Log the timeout and retry with basic approach (no fancy fonts)
        logger.warning(
            f"PDF generation timed out: {e}. Retrying with fallback approach."
        )

        # Create a fresh PDF and use only default fonts
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)

        # Write minimal structure with default font (won't hang)
        pdf.cell(0, 10, f"Project Briefing: {briefing_data.project_name}", ln=True)
        pdf.cell(0, 10, f"Client: {briefing_data.client_name}", ln=True)
        pdf.cell(0, 10, f"Deadline: {briefing_data.deadline}", ln=True)

        if briefing_data.budget:
            pdf.cell(0, 10, f"Budget: ${briefing_data.budget:,.2f}", ln=True)

        if briefing_data.objectives:
            pdf.cell(0, 10, f"Objectives: {briefing_data.objectives}", ln=True)

        logger.info("Used fallback PDF generation (default fonts only)")

    # Save PDF
    pdf.output(str(output_path))
