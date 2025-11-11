"""Semantic quality validation for templates and outputs."""

import json
from pathlib import Path

import pytest


class TestTemplateQuality:
    """Validate registry templates against AI slop and quality standards."""

    @pytest.fixture
    def templates(self):
        """Load templates from registry."""
        registry_path = (
            Path(__file__).parent.parent.parent
            / "registry"
            / "seeds"
            / "templates.json"
        )
        with open(registry_path) as f:
            data = json.load(f)
        return data.get("templates", {})

    def test_all_templates_have_required_fields(self, templates):
        """Ensure all templates have essential metadata."""
        for template_id, template in templates.items():
            assert "name" in template, f"{template_id} missing 'name'"
            assert "description" in template, f"{template_id} missing 'description'"
            assert "prompt_prefix" in template, f"{template_id} missing 'prompt_prefix'"
            assert "mood" in template, f"{template_id} missing 'mood'"

    def test_prompts_contain_quality_indicators(self, templates):
        """Validate prompts contain quality/detail indicators."""
        quality_keywords = [
            "professional",
            "high quality",
            "detailed",
            "4k",
            "8k",
            "cinematic",
            "photography",
            "polished",
            "clean",
            "modern",
            "aesthetic",
            "minimalist",
            "luxury",
            "elegant",
        ]

        for template_id, template in templates.items():
            prompt = template["prompt_prefix"].lower()

            # Check for at least one quality indicator
            has_quality = any(keyword in prompt for keyword in quality_keywords)
            assert has_quality, (
                f"Template '{template_id}' prompt lacks quality indicators. "
                f"Prompt: {template['prompt_prefix']}"
            )

    def test_prompts_avoid_lazy_words(self, templates):
        """Ensure prompts don't contain overused/lazy descriptors."""
        lazy_words = ["vibrant", "stunning", "amazing", "incredible", "awesome"]

        for template_id, template in templates.items():
            prompt = template["prompt_prefix"].lower()

            found_lazy = [word for word in lazy_words if word in prompt]

            # Allow 'vibrant' in playful template only
            if template_id == "playful" and found_lazy == ["vibrant"]:
                continue

            assert not found_lazy, (
                f"Template '{template_id}' uses lazy words: {found_lazy}. "
                f"Prompt: {template['prompt_prefix']}"
            )

    def test_templates_have_valid_color_palettes(self, templates):
        """Ensure color palettes are valid hex codes."""
        import re

        hex_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

        for template_id, template in templates.items():
            if "color_palette" in template:
                colors = template["color_palette"]
                assert isinstance(
                    colors, list
                ), f"{template_id} color_palette must be a list"
                assert len(colors) >= 2, f"{template_id} needs at least 2 colors"

                for color in colors:
                    assert hex_pattern.match(
                        color
                    ), f"{template_id} has invalid color: {color}"


class TestOutputContracts:
    """Validate output artifacts meet expected contracts."""

    def test_pdf_structure_contract(self, tmp_path):
        """Ensure generated PDFs contain expected sections."""
        # This is a placeholder for actual PDF generation test
        # Will be implemented with snapshot testing
        pass

    def test_json_structure_contract(self, tmp_path):
        """Ensure generated JSON has required fields."""
        # This is a placeholder for actual JSON generation test
        # Will be implemented with snapshot testing
        pass
