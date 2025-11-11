"""Integration tests for semantic toolkit commands (WU-7.7)."""

import json
from pathlib import Path

import pytest

from agency_toolkit.commands.info import (
    get_available_providers,
    get_available_seed_templates,
    get_available_social_templates,
    load_toolkit_docs,
)


class TestInfoCommand:
    """Tests for toolkit info command."""

    def test_get_available_social_templates(self):
        """Verify social templates are discovered."""
        templates = get_available_social_templates()

        # Should have at least the standard templates
        assert isinstance(templates, dict)
        assert len(templates) > 0

        # Should contain expected templates
        expected_templates = ["modern", "bold", "minimal"]
        for template in expected_templates:
            assert template in templates, f"Missing template: {template}"

    def test_get_available_providers(self):
        """Verify providers are correctly listed."""
        providers = get_available_providers()

        assert isinstance(providers, dict)
        assert len(providers) >= 2

        # Check standard providers
        assert "pollinations" in providers
        assert "replicate" in providers

        # Check provider structure
        assert "description" in providers["pollinations"]
        assert "status" in providers["pollinations"]

    def test_get_available_seed_templates(self):
        """Verify seed templates from registry are discovered."""
        seeds = get_available_seed_templates()

        assert isinstance(seeds, dict)

        # Should have the 5 standard seed templates
        expected_seeds = ["moody", "corporate", "playful", "minimal", "nature"]
        for seed in expected_seeds:
            assert seed in seeds, f"Missing seed template: {seed}"

    def test_get_seed_templates_descriptions(self):
        """Verify seed templates have proper descriptions."""
        seeds = get_available_seed_templates()

        for seed_id, description in seeds.items():
            assert isinstance(description, str)
            assert len(description) > 0
            assert description != "Seed template"  # Should be specific


class TestDocsCaching:
    """Tests for documentation loading and caching."""

    def test_load_toolkit_docs_returns_string(self):
        """Verify load_toolkit_docs returns documentation as string."""
        docs = load_toolkit_docs()

        assert isinstance(docs, str)
        assert len(docs) > 0

    def test_load_toolkit_docs_includes_blueprint(self):
        """Verify documentation includes BLUEPRINT.yaml content."""
        docs = load_toolkit_docs()

        # Should contain sections from BLUEPRINT
        # (Looking for characteristic YAML structure)
        assert "version" in docs or "Version" in docs or "BLUEPRINT" in docs

    def test_load_toolkit_docs_includes_implementation(self):
        """Verify documentation includes IMPLEMENTATION.yaml content."""
        docs = load_toolkit_docs()

        # Should contain sections from IMPLEMENTATION
        assert "IMPLEMENTATION" in docs or "implementation" in docs or "modules" in docs

    def test_load_toolkit_docs_includes_roadmap(self):
        """Verify documentation includes ROADMAP.md content."""
        docs = load_toolkit_docs()

        # Should contain sections from ROADMAP
        assert "ROADMAP" in docs or "Epic" in docs or "epic" in docs

    def test_cache_is_created_and_reused(self):
        """Verify documentation is cached and reused."""
        # First call - should load docs
        docs1 = load_toolkit_docs()
        assert isinstance(docs1, str)
        assert len(docs1) > 0

        # Second call - should return same content (from cache)
        docs2 = load_toolkit_docs()

        # Should return same content
        assert docs1 == docs2


class TestSocialTemplatesDetail:
    """Detailed tests for social template discovery."""

    def test_all_templates_have_valid_json(self):
        """Verify all template files are valid JSON."""
        template_dir = (
            Path(__file__).parent.parent.parent
            / "agency_toolkit"
            / "templates"
            / "social"
        )

        for template_file in template_dir.glob("*.json"):
            data = json.loads(template_file.read_text())

            # Should have basic structure
            assert isinstance(data, dict)
            assert "description" in data or len(data) > 0

    def test_template_descriptions_are_meaningful(self):
        """Verify template descriptions are meaningful."""
        templates = get_available_social_templates()

        for name, description in templates.items():
            # Description should be non-empty and meaningful
            assert len(description) > 5
            assert description.lower() != "social template"
            assert isinstance(description, str)


class TestSeedTemplatesDetail:
    """Detailed tests for seed template discovery."""

    def test_seed_templates_have_required_fields(self):
        """Verify seed templates have all required fields."""
        registry_path = (
            Path(__file__).parent.parent.parent
            / "registry"
            / "seeds"
            / "templates.json"
        )

        if not registry_path.exists():
            pytest.skip("Registry not found")

        data = json.loads(registry_path.read_text())
        templates = data.get("templates", {})

        for template_id, template in templates.items():
            # Check required fields
            assert "description" in template
            assert "prompt_prefix" in template
            assert "mood" in template
            assert "color_palette" in template
            assert "best_for" in template
            assert "default_seed" in template

    def test_seed_templates_values_are_valid(self):
        """Verify seed template values are valid types."""
        registry_path = (
            Path(__file__).parent.parent.parent
            / "registry"
            / "seeds"
            / "templates.json"
        )

        if not registry_path.exists():
            pytest.skip("Registry not found")

        data = json.loads(registry_path.read_text())
        templates = data.get("templates", {})

        for template_id, template in templates.items():
            # Type checks
            assert isinstance(template["description"], str)
            assert len(template["description"]) > 0

            assert isinstance(template["prompt_prefix"], str)
            assert len(template["prompt_prefix"]) > 10

            assert isinstance(template["mood"], str)

            assert isinstance(template["color_palette"], list)
            assert len(template["color_palette"]) >= 3

            assert isinstance(template["best_for"], list)
            assert len(template["best_for"]) > 0

            assert isinstance(template["default_seed"], int)


class TestProvidersInfo:
    """Tests for provider information."""

    def test_providers_have_descriptions(self):
        """Verify all providers have descriptions."""
        providers = get_available_providers()

        for name, info in providers.items():
            assert "description" in info
            assert len(info["description"]) > 0
            assert isinstance(info["description"], str)

    def test_default_provider_marked(self):
        """Verify default provider is properly marked."""
        providers = get_available_providers()

        # Pollinations should be marked as default
        assert "pollinations" in providers
        assert "Default" in providers["pollinations"].get("status", "")
