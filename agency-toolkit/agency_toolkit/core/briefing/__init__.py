"""Briefing generation module (refactored).

Clean architecture with single-responsibility modules.
"""

from agency_toolkit.core.briefing.generator import generate
from agency_toolkit.core.briefing.interactive import collect_interactive
from agency_toolkit.core.briefing.io import load_from_json, write_markdown
from agency_toolkit.core.briefing.models import BriefingData
from agency_toolkit.core.briefing.pdf_writer import write_pdf
from agency_toolkit.core.briefing.templates import load_briefing_questions

__all__ = [
    "generate",
    "BriefingData",
    "load_briefing_questions",
    "collect_interactive",
    "load_from_json",
    "write_pdf",
    "write_markdown",
]
