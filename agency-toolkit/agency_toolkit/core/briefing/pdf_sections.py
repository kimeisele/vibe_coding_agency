"""PDF generation for briefings using ReportLab/FPDF."""

import re
import unicodedata
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from agency_toolkit.core.briefing.constants import (
    FONT_FAMILY,
    FONT_SIZE_BODY,
    FONT_SIZE_SECTION_HEADER,
    FONT_SIZE_TIMESTAMP,
    FONT_SIZE_TITLE,
    FONT_STYLE_BOLD,
    FONT_STYLE_NORMAL,
    LINE_HEIGHT_BODY,
    LINE_HEIGHT_MULTI_CELL,
    LINE_HEIGHT_SECTION_HEADER,
    LINE_HEIGHT_TITLE,
    SPACING_AFTER_DELIVERABLES,
    SPACING_AFTER_HEADER,
    SPACING_AFTER_SECTION,
    SPACING_BETWEEN_ITEMS,
)


def write_header(pdf: FPDF) -> None:
    """Write PDF header with title and timestamp.

    Args:
        pdf: FPDF instance
    """
    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_TITLE)
    pdf.cell(
        0,
        LINE_HEIGHT_TITLE,
        "Project Briefing",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="C",
    )

    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_TIMESTAMP)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(
        0,
        LINE_HEIGHT_TITLE,
        f"Generated: {timestamp}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
        align="C",
    )
    pdf.ln(SPACING_AFTER_HEADER)


def write_client_info(pdf: FPDF, client: str, project: str, project_type: str) -> None:
    """Write client information section.

    Args:
        pdf: FPDF instance
        client: Client name
        project: Project name
        project_type: Project type
    """
    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0,
        LINE_HEIGHT_SECTION_HEADER,
        "Client Information",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)
    pdf.cell(
        0, LINE_HEIGHT_BODY, f"Client: {client}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    pdf.cell(
        0, LINE_HEIGHT_BODY, f"Project: {project}", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    pdf.cell(
        0,
        LINE_HEIGHT_BODY,
        f"Type: {project_type}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(SPACING_AFTER_SECTION)


def write_timeline(pdf: FPDF, deadline: str, budget: float | None) -> None:
    """Write timeline and budget section.

    Args:
        pdf: FPDF instance
        deadline: Deadline date string
        budget: Budget amount (or None)
    """
    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0,
        LINE_HEIGHT_SECTION_HEADER,
        "Timeline & Budget",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)
    pdf.cell(
        0,
        LINE_HEIGHT_BODY,
        f"Deadline: {deadline}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    if budget:
        pdf.cell(
            0,
            LINE_HEIGHT_BODY,
            f"Budget: ${budget:,.2f}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    pdf.ln(SPACING_AFTER_SECTION)


def write_details(
    pdf: FPDF, objectives: str | None, target_audience: str | None
) -> None:
    """Write project details section.

    Args:
        pdf: FPDF instance
        objectives: Objectives text
        target_audience: Target audience text
    """
    if not objectives and not target_audience:
        return

    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0,
        LINE_HEIGHT_SECTION_HEADER,
        "Project Details",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)

    if objectives:
        pdf.multi_cell(0, LINE_HEIGHT_MULTI_CELL, f"Objectives: {objectives}")
        pdf.ln(SPACING_BETWEEN_ITEMS)

    if target_audience:
        pdf.multi_cell(0, LINE_HEIGHT_MULTI_CELL, f"Target Audience: {target_audience}")
        pdf.ln(SPACING_BETWEEN_ITEMS)


def write_deliverables(pdf: FPDF, deliverables: list[str]) -> None:
    """Write deliverables section.

    Args:
        pdf: FPDF instance
        deliverables: List of deliverable items
    """
    if not deliverables or deliverables == [""]:
        return

    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0,
        LINE_HEIGHT_SECTION_HEADER,
        "Deliverables",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)

    for deliverable in deliverables:
        if deliverable:
            pdf.cell(
                0,
                LINE_HEIGHT_BODY,
                f"- {deliverable.strip()}",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

    pdf.ln(SPACING_AFTER_DELIVERABLES)


def write_notes(pdf: FPDF, notes: str | None) -> None:
    """Write notes section.

    Args:
        pdf: FPDF instance
        notes: Notes text
    """
    if not notes:
        return

    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0, LINE_HEIGHT_SECTION_HEADER, "Notes", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)
    pdf.multi_cell(0, LINE_HEIGHT_MULTI_CELL, notes)


def _sanitize_for_pdf(text: str) -> str:
    """Sanitize text for PDF output by replacing Unicode characters with ASCII equivalents.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for PDF rendering with default fonts
    """
    if not isinstance(text, str):
        return str(text)

    # First, apply explicit replacements for common special characters
    replacements = {
        # Dashes
        "–": "-",  # en dash
        "—": "-",  # em dash
        "‐": "-",  # hyphen
        "‑": "-",  # non-breaking hyphen
        # Quotes
        """: '"',  # left double quote
        """: '"',  # right double quote
        "„": '"',  # double low quote
        "'": "'",  # left single quote
        "'": "'",  # right single quote
        "‚": "'",  # single low quote
        "´": "'",  # acute accent
        "`": "'",  # grave accent
        "ˋ": "'",  # modifier letter grave accent
        # Bullets and symbols
        "•": "-",  # bullet
        "·": "-",  # middle dot
        "○": "o",  # white circle
        "●": "o",  # black circle
        "→": "->",  # arrow
        "←": "<-",  # left arrow
        "↔": "<->",  # bidirectional arrow
        "✔": "[ok]",  # checkmark
        "✓": "[ok]",  # check mark
        "✗": "[x]",  # x mark
        "★": "*",  # star
        "☆": "*",  # white star
        "°": "deg",  # degree
        "€": "EUR",  # Euro
        "£": "GBP",  # Pound
        "¥": "JPY",  # Yen
        "¢": "cent",  # cent
        "©": "(c)",  # copyright
        "®": "(R)",  # registered
        "™": "(TM)",  # trademark
        # Subscripts and superscripts (just remove them)
        "₀": "0",  # subscript 0
        "₁": "1",  # subscript 1
        "₂": "2",  # subscript 2
        "₃": "3",  # subscript 3
        "₄": "4",  # subscript 4
        "₅": "5",  # subscript 5
        "₆": "6",  # subscript 6
        "₇": "7",  # subscript 7
        "₈": "8",  # subscript 8
        "₉": "9",  # subscript 9
        "⁰": "0",  # superscript 0
        "¹": "1",  # superscript 1
        "²": "2",  # superscript 2
        "³": "3",  # superscript 3
    }

    sanitized = text
    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)

    # Second, remove any remaining non-ASCII characters that aren't in the Latin-1 range
    try:
        # Try to encode as Latin-1 (which is what FPDF uses)
        sanitized.encode("latin-1")
    except UnicodeEncodeError:
        # If that fails, decompose accented characters and remove accents
        sanitized = unicodedata.normalize("NFKD", sanitized)
        sanitized = "".join(c for c in sanitized if unicodedata.category(c) != "Mn")
        # Remove any remaining non-ASCII
        sanitized = re.sub(r"[^\x00-\x7F]", "", sanitized)

    return sanitized


def write_ai_content(pdf: FPDF, step_context: dict | None) -> None:
    """Write AI-generated content section.

    Args:
        pdf: FPDF instance
        step_context: Dictionary with AI-generated content from workflow steps
    """
    if not step_context:
        return

    # Check for any AI-generated content keys
    ai_content_keys = [
        "website_concepts",
        "design_recommendations",
        "content_strategy",
        "campaign_concepts",
        "recruiting_taglines",
        "job_ad_text",
        "whitepaper_topics",
        "lead_magnet_ideas",
    ]

    # Find which AI content exists in context
    existing_content = {
        k: v for k, v in step_context.items() if k in ai_content_keys and v
    }

    if not existing_content:
        return

    # Write Executive Summary / AI-Generated Content section
    pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_SECTION_HEADER)
    pdf.cell(
        0,
        LINE_HEIGHT_SECTION_HEADER,
        "Strategic Recommendations & Generated Content",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)

    # Write each AI content section
    content_labels = {
        "website_concepts": "Website Concepts",
        "design_recommendations": "Design Recommendations",
        "content_strategy": "Content Strategy",
        "campaign_concepts": "Campaign Concepts",
        "recruiting_taglines": "Recruiting Taglines",
        "job_ad_text": "Job Advertisement",
        "whitepaper_topics": "Whitepaper Topics",
        "lead_magnet_ideas": "Lead Magnet Ideas",
    }

    for key, content in existing_content.items():
        label = content_labels.get(key, key.replace("_", " ").title())

        # Write subsection heading (use hyphen instead of bullet for font compatibility)
        pdf.set_font(FONT_FAMILY, FONT_STYLE_BOLD, FONT_SIZE_BODY)
        pdf.cell(
            0, LINE_HEIGHT_BODY, f"- {label}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )

        # Write content with word wrapping
        pdf.set_font(FONT_FAMILY, FONT_STYLE_NORMAL, FONT_SIZE_BODY)
        if isinstance(content, str):
            # Sanitize AI-generated text for PDF compatibility
            sanitized_content = _sanitize_for_pdf(content)
            pdf.multi_cell(0, LINE_HEIGHT_MULTI_CELL, sanitized_content)
        else:
            # Handle list content
            content_str = (
                str(content)
                if not isinstance(content, (list, tuple))
                else "\n".join(str(item) for item in content)
            )
            sanitized_content = _sanitize_for_pdf(content_str)
            pdf.multi_cell(0, LINE_HEIGHT_MULTI_CELL, sanitized_content)

        pdf.ln(SPACING_BETWEEN_ITEMS)

    pdf.ln(SPACING_AFTER_SECTION)
