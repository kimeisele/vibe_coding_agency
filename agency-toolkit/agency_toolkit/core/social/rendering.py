"""Rendering functions for social media posts."""

import logging
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from agency_toolkit.core.social.constants import (
    DEFAULT_FONT_SIZE,
    DEFAULT_MAX_CHARS_PER_LINE,
    DEFAULT_TEXT_COLOR,
    ROBOTO_BOLD_FONT,
)
from agency_toolkit.core.social.layout import hex_to_rgb

logger = logging.getLogger(__name__)


def create_gradient_image(
    width: int, height: int, color1: str, color2: str
) -> Image.Image:
    """Create gradient background image.

    Args:
        width: Image width
        height: Image height
        color1: Start color (hex)
        color2: End color (hex)

    Returns:
        PIL Image with gradient
    """
    base = Image.new("RGB", (width, height), hex_to_rgb(color1))
    top = Image.new("RGB", (width, height), hex_to_rgb(color2))
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def create_base_image(
    width: int, height: int, template: dict, resolved_color: str
) -> Image.Image:
    """Create base image with background.

    Args:
        width: Image width
        height: Image height
        template: Template configuration
        resolved_color: Resolved hex color

    Returns:
        PIL Image with background
    """
    if template.get("background_type") == "gradient":
        gradient_colors = template.get(
            "gradient_colors", [resolved_color, resolved_color]
        )
        return create_gradient_image(
            width, height, gradient_colors[0], gradient_colors[1]
        )
    else:
        rgb = hex_to_rgb(resolved_color)
        return Image.new("RGB", (width, height), rgb)


def wrap_text(text: str, max_chars: int) -> str:
    """Wrap text to max characters per line.

    Args:
        text: Input text
        max_chars: Maximum characters per line

    Returns:
        Wrapped text with newlines
    """
    lines = text.split("\n")
    wrapped_lines = []
    for line in lines:
        if len(line) <= max_chars:
            wrapped_lines.append(line)
        else:
            wrapped_lines.extend(textwrap.wrap(line, max_chars))
    return "\n".join(wrapped_lines)


def load_font(
    template: dict, height: int
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load font from template configuration.

    Args:
        template: Template configuration
        height: Image height for relative font sizing

    Returns:
        PIL ImageFont object
    """
    if "font_size_ratio" in template:
        font_size = int(height * template["font_size_ratio"])
    else:
        font_size = template.get("font_size", DEFAULT_FONT_SIZE)

    try:
        # Try project-local font first
        project_root = Path(__file__).parent.parent.parent.parent
        font_path = project_root / "assets" / "fonts" / ROBOTO_BOLD_FONT

        if font_path.exists():
            return ImageFont.truetype(str(font_path), font_size)

        # Fallback to system fonts that support UTF-8
        # macOS system fonts with proper Unicode support
        system_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]

        for sys_font_path in system_fonts:
            if Path(sys_font_path).exists():
                logger.warning(
                    f"Using system font '{sys_font_path}' (custom font not found)"
                )
                return ImageFont.truetype(sys_font_path, font_size)

        # If no system font found, log error but still return a working font
        logger.error(
            f"No custom or system font found. Roboto not at '{font_path}'. "
            "Please add Roboto-Bold.ttf to assets/fonts/ for better rendering."
        )
        # Try to use a fallback that might work
        try:
            return ImageFont.load_default(font_size)
        except (TypeError, AttributeError):
            # load_default() doesn't accept size parameter in older PIL versions
            return ImageFont.load_default()

    except OSError as e:
        # Font file errors (not found, corrupted, permission issues)
        logger.warning(f"Failed to load font: {e}")
        try:
            return ImageFont.load_default(font_size)
        except (TypeError, AttributeError):
            # load_default() doesn't accept size parameter in older PIL versions
            return ImageFont.load_default()


def draw_text_on_image(
    image: Image.Image, text: str, template: dict, width: int, height: int
) -> None:
    """Draw text on image.

    Args:
        image: PIL Image to draw on
        text: Text content
        template: Template configuration
        width: Image width
        height: Image height
    """
    draw = ImageDraw.Draw(image)
    font = load_font(template, height)

    max_chars = template.get("max_chars_per_line", DEFAULT_MAX_CHARS_PER_LINE)
    wrapped_text = wrap_text(text, max_chars)

    text_color = template.get("text_color", DEFAULT_TEXT_COLOR)
    text_rgb = hex_to_rgb(text_color)
    x, y = template.get("text_position_xy", [width // 2, height // 2])

    draw.multiline_text(
        (x, y),
        wrapped_text,
        fill=text_rgb,
        font=font,
        anchor="mm",
        align="center",
    )
