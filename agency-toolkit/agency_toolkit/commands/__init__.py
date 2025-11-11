"""Command modules for the agency toolkit CLI.

This package contains modular command implementations extracted from cli_app.py.
Each command is a separate module to avoid the God Object anti-pattern and allow
independent testing and development.

Command modules:
- social.py: Social media post generation
- briefing.py: Project briefing data management
- structure.py: Folder structure creation
- ai.py: Multi-provider AI text generation
- image.py: AI image generation
- os.py: GRAND AGENCY OS orchestrated workflows
"""

from agency_toolkit.commands.ai import ai_command
from agency_toolkit.commands.briefing import briefing_command
from agency_toolkit.commands.image import image_command
from agency_toolkit.commands.info import info_command
from agency_toolkit.commands.os import app as os_command
from agency_toolkit.commands.social import social_command
from agency_toolkit.commands.structure import structure_command
from agency_toolkit.commands.validate import validate_command

__all__ = [
    "social_command",
    "briefing_command",
    "structure_command",
    "ai_command",
    "image_command",
    "info_command",
    "validate_command",
    "os_command",
]
