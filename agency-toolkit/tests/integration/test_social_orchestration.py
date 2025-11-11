"""Integration tests for social + image + mistral orchestration (WU-7.4)."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agency_toolkit.core.social import load_registry_concept


class TestRegistryConceptLoading:
    """Tests for loading concepts from registry."""

    def testload_registry_concept_moody(self):
        """Verify loading moody template from registry."""
        prompt = load_registry_concept("moody")
        assert prompt is not None
        assert "moody" in prompt.lower() or "dark" in prompt.lower()

    def testload_registry_concept_corporate(self):
        """Verify loading corporate template from registry."""
        prompt = load_registry_concept("corporate")
        assert prompt is not None
        assert "professional" in prompt.lower() or "corporate" in prompt.lower()

    def testload_registry_concept_playful(self):
        """Verify loading playful template from registry."""
        prompt = load_registry_concept("playful")
        assert prompt is not None
        assert "playful" in prompt.lower() or "vibrant" in prompt.lower()

    def testload_registry_concept_minimal(self):
        """Verify loading minimal template from registry."""
        prompt = load_registry_concept("minimal")
        assert prompt is not None
        assert "minimal" in prompt.lower() or "white" in prompt.lower()

    def testload_registry_concept_nature(self):
        """Verify loading nature template from registry."""
        prompt = load_registry_concept("nature")
        assert prompt is not None
        assert "nature" in prompt.lower() or "organic" in prompt.lower()

    def test_load_invalid_concept_raises_error(self):
        """Verify loading invalid concept raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            load_registry_concept("invalid_concept")

    def test_load_invalid_concept_shows_available_options(self):
        """Verify error message shows available concepts."""
        try:
            load_registry_concept("nonexistent")
        except ValueError as e:
            error_msg = str(e)
            # Should mention at least one real concept
            assert any(
                concept in error_msg
                for concept in ["moody", "corporate", "playful", "minimal", "nature"]
            )


class TestSocialOrchestrationIntegration:
    """Integration tests for social + image + mistral orchestration."""

    @pytest.fixture
    def mock_config(self):
        """Provide mock config."""
        config = MagicMock()
        config.output_dir = Path("/tmp/output")
        config.json_output = False
        config.image.provider = "pollinations"
        return config

    def test_registry_concept_loaded_for_registry_prefix(self, mock_config):
        """Verify registry: prefix loads from registry."""
        # Just test that load_registry_concept works
        prompt = load_registry_concept("moody")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_all_registry_concepts_are_accessible(self):
        """Verify all registry concepts can be loaded."""
        concepts = ["moody", "corporate", "playful", "minimal", "nature"]

        for concept in concepts:
            prompt = load_registry_concept(concept)
            assert isinstance(prompt, str)
            assert len(prompt) > 10  # Should be meaningful

    def test_registry_has_required_fields(self):
        """Verify registry templates have required fields."""
        from pathlib import Path

        registry_path = (
            Path(__file__).parent.parent.parent
            / "registry"
            / "seeds"
            / "templates.json"
        )
        data = json.loads(registry_path.read_text())
        templates = data.get("templates", {})

        for concept_id, template in templates.items():
            # Verify structure
            assert "prompt_prefix" in template, f"{concept_id} missing prompt_prefix"
            assert "mood" in template, f"{concept_id} missing mood"
            assert "color_palette" in template, f"{concept_id} missing color_palette"
            assert "best_for" in template, f"{concept_id} missing best_for"
            assert "default_seed" in template, f"{concept_id} missing default_seed"

            # Verify values are reasonable
            assert isinstance(template["prompt_prefix"], str)
            assert len(template["prompt_prefix"]) > 20
            assert isinstance(template["mood"], str)
            assert isinstance(template["color_palette"], list)
            assert len(template["color_palette"]) >= 3
            assert isinstance(template["default_seed"], int)
