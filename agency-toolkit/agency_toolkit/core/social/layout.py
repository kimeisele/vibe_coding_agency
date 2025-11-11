"""Layout calculation functions for social media posts."""


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string

    Returns:
        RGB tuple (r, g, b)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


def calculate_text_position(template: dict, width: int, height: int) -> tuple[int, int]:
    """Calculate text position from template.

    Args:
        template: Template configuration dict
        width: Image width
        height: Image height

    Returns:
        Tuple of (x, y) position
    """
    default_x = width // 2
    default_y = height // 2
    return template.get("text_position_xy", [default_x, default_y])
