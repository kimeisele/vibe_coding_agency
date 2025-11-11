"""Social media post generator orchestrator.

Coordinates all modules to generate social media posts.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image as PILImage

from agency_toolkit.core.social.rendering import create_base_image, draw_text_on_image
from agency_toolkit.core.social.templates import get_template
from agency_toolkit.core.social.validators import (
    validate_color,
    validate_format,
    validate_text,
)
from agency_toolkit.exceptions import (
    AIProviderError,
    ConfigurationError,
    ImageProviderError,
)
from agency_toolkit.utils import ensure_output_dir

logger = logging.getLogger(__name__)


def generate(
    text: str,
    style: str = "modern",
    color: str = "blue",
    custom_color: str | None = None,
    format_name: str = "square",
    output_dir: Path = Path("./output/social"),
    dry_run: bool = False,
    background_image_path: Path | None = None,
    bg_concept: str | None = None,
) -> dict:
    """Generate social media post image.

    Args:
        text: Post text content
        style: Template style (modern, minimal, bold)
        color: Color name or 'custom'
        custom_color: Hex color if color='custom'
        format_name: Image format (square, story, landscape)
        output_dir: Output directory
        dry_run: If True, return path without creating file
        background_image_path: Optional path to background image to overlay text on
        bg_concept: Optional AI-generated background concept description (for future use)

    Returns:
        Dict with path, format, style, text_length, dry_run

    Raises:
        ConfigurationError: If inputs are invalid
    """
    # Validate inputs
    text = validate_text(text)
    width, height = validate_format(format_name)

    # Resolve color
    if color == "custom":
        if not custom_color:
            raise ConfigurationError("custom_color required when color='custom'")
        resolved_color = validate_color(custom_color)
    else:
        resolved_color = validate_color(color)

    # Load template
    template = get_template(style)

    # Create image with prioritized background logic
    bg_image_to_load = background_image_path  # Priority 1: Explicit path

    # Priority 2: AI-generated image if no explicit path
    if not bg_image_to_load and bg_concept:
        logger.info(f"AI background concept detected: '{bg_concept}'")
        try:
            # Import here to avoid circular dependencies
            from agency_toolkit.image_gen import generate_image
            from agency_toolkit.providers.mistral_provider import MistralProvider

            # 1. Enhance the prompt
            mistral = MistralProvider()
            enhanced_prompt = mistral.enhance_image_prompt(bg_concept)
            logger.debug(f"Enhanced AI prompt: '{enhanced_prompt}'")

            # 2. Generate deterministic seed for consistency (per DESIGN.md 6.1)
            seed = hash(text + bg_concept) % (2**32)

            # 3. Generate image (try to load config, fallback to None)
            try:
                from agency_toolkit.core.config import Config as ConfigClass

                config = ConfigClass.load() if hasattr(ConfigClass, "load") else None
            except (ImportError, AttributeError):
                config = None

            img_result = generate_image(
                prompt=enhanced_prompt,
                seed=seed,
                width=width,
                height=height,
                config=config,
            )

            bg_image_to_load = Path(img_result["path"])
            logger.info(f"AI background generated successfully: {bg_image_to_load}")

        except (AIProviderError, ImageProviderError) as e:
            logger.error(
                f"AI background generation failed for concept '{bg_concept}': {e}"
            )
            bg_image_to_load = None
        except ImportError as e:
            logger.error(
                f"Required module not available for AI background generation: {e}"
            )
            bg_image_to_load = None
        except Exception as e:
            logger.error(
                f"Unexpected error in AI background generation: {e}", exc_info=True
            )
            bg_image_to_load = None

    # Final image creation: Priority 1/2 or fallback to gradient
    if bg_image_to_load:
        try:
            image = PILImage.open(bg_image_to_load).convert("RGB")
            if image.size != (width, height):
                image = image.resize((width, height), PILImage.Resampling.LANCZOS)
        except Exception as e:
            logger.warning(
                f"Failed to load background image '{bg_image_to_load}': {e}. Using gradient fallback."
            )
            image = create_base_image(width, height, template, resolved_color)
    else:
        # Priority 3: Gradient/solid color (fallback)
        logger.debug("Using base gradient/color background.")
        image = create_base_image(width, height, template, resolved_color)

    # Draw text
    draw_text_on_image(image, text, template, width, height)

    # Generate output path with UUID to prevent collisions in batch processing
    # Using timestamp + UUID ensures both human readability and uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    output_filename = f"social_{timestamp}_{unique_id}.png"
    output_path = output_dir / output_filename

    if not dry_run:
        ensure_output_dir(output_dir)
        image.save(output_path, "PNG")
        logger.info(f"Generated social post: {output_path}")

    return {
        "path": str(output_path),
        "format": format_name,
        "style": style,
        "text_length": len(text),
        "dry_run": dry_run,
    }
