"""Background image generation for social posts."""

import logging
from pathlib import Path

from agency_toolkit.image_gen import generate_image
from agency_toolkit.providers.mistral_provider import MistralProvider

logger = logging.getLogger(__name__)


def load_registry_concept(concept_id: str) -> str:
    """Load concept prompt from registry.

    Args:
        concept_id: Concept identifier (e.g., 'moody', 'corporate')

    Returns:
        Prompt string

    Raises:
        ValueError: If concept not found in registry
    """
    import json

    registry_path = (
        Path(__file__).parent.parent.parent.parent
        / "registry"
        / "seeds"
        / "templates.json"
    )

    if not registry_path.exists():
        raise ValueError(f"Registry not found at {registry_path}")

    data = json.loads(registry_path.read_text())
    templates = data.get("templates", {})

    if concept_id not in templates:
        available = list(templates.keys())
        raise ValueError(
            f"Concept '{concept_id}' not found. Available: {', '.join(available)}"
        )

    return templates[concept_id]["prompt_prefix"]


def generate_background(
    bg_concept: str,
    bg_seed: int | None = None,
    provider: str = "pollinations",
    config=None,
) -> dict:
    """Generate background image from concept.

    Args:
        bg_concept: Background concept (e.g., 'moody', 'registry:corporate')
        bg_seed: Optional seed for reproducibility
        provider: Image provider to use
        config: Configuration object

    Returns:
        dict with 'path', 'cost', 'prompt' keys

    Raises:
        ValueError: If concept resolution or generation fails
    """
    # Step 1: Resolve concept (registry or Mistral enhancement)
    if bg_concept.startswith("registry:"):
        # Load from registry
        concept_id = bg_concept.replace("registry:", "")
        actual_prompt = load_registry_concept(concept_id)
        logger.info(f"Using registry template: {concept_id}")
    else:
        # Enhance via Mistral
        mistral = MistralProvider()
        actual_prompt = mistral.enhance_image_prompt(bg_concept)

        if not actual_prompt:
            raise ValueError("Mistral returned empty prompt")

        logger.info(f"Enhanced prompt: {actual_prompt[:80]}...")

    # Step 2: Generate image
    img_result = generate_image(
        prompt=actual_prompt,
        seed=bg_seed,
        provider=provider,
        config=config,
    )

    return {
        "path": img_result["path"],
        "cost": img_result.get("cost", 0.0),
        "prompt": actual_prompt,
    }
