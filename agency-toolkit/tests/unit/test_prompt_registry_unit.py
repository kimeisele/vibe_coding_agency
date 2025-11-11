"""Unit tests for the Prompt Registry system."""

import json
from datetime import datetime

import pytest

from agency_toolkit.core.prompt_registry import Prompt, PromptRegistry


class TestPromptModel:
    """Test Prompt dataclass functionality."""

    def test_prompt_from_json_basic(self):
        """Test loading a prompt from JSON with basic fields."""
        data = {
            "id": "test_prompt",
            "category": "templates",
            "prompt": "This is a test prompt",
            "description": "A test description",
        }
        prompt = Prompt.from_json(data)

        assert prompt.id == "test_prompt"
        assert prompt.category == "templates"
        assert prompt.prompt == "This is a test prompt"
        assert prompt.description == "A test description"

    def test_prompt_from_json_with_all_fields(self):
        """Test loading a prompt from JSON with all optional fields."""
        data = {
            "id": "full_prompt",
            "category": "expert_personas",
            "prompt": "You are an expert",
            "description": "Expert persona",
            "model": "claude-sonnet",
            "variables": ["topic", "depth"],
            "tags": ["expert", "technical"],
            "usage_count": 10,
            "last_used": datetime.now().isoformat(),
            "version": "2.0",
            "rag_tags": ["semantic", "vector"],
            "intent_keywords": ["analyze", "explain"],
            "composable": True,
            "requires_context": True,
            "input_schema": {"type": "object"},
            "output_schema": {"type": "string"},
            "constraints": ["length < 500"],
            "quality_score": 0.95,
            "avg_tokens_used": 250,
            "success_rate": 0.92,
        }
        prompt = Prompt.from_json(data)

        assert prompt.id == "full_prompt"
        assert prompt.model == "claude-sonnet"
        assert prompt.variables == ["topic", "depth"]
        assert prompt.tags == ["expert", "technical"]
        assert prompt.usage_count == 10
        assert prompt.version == "2.0"
        assert prompt.composable is True
        assert prompt.requires_context is True
        assert prompt.quality_score == 0.95
        assert prompt.success_rate == 0.92

    def test_prompt_to_json(self):
        """Test converting a prompt to JSON."""
        prompt = Prompt(
            id="export_test",
            category="templates",
            prompt="Test content",
            description="Test description",
            model="claude-sonnet",
            variables=["var1"],
            tags=["tag1"],
            quality_score=0.8,
        )
        json_data = prompt.to_json()

        assert json_data["id"] == "export_test"
        assert json_data["category"] == "templates"
        assert json_data["prompt"] == "Test content"
        assert json_data["model"] == "claude-sonnet"
        assert json_data["variables"] == ["var1"]
        assert json_data["quality_score"] == 0.8

    def test_prompt_roundtrip_json(self):
        """Test that a prompt can be converted to JSON and back."""
        original = Prompt(
            id="roundtrip_test",
            category="agent_primers",
            prompt="Original prompt",
            description="Original description",
            tags=["test"],
            quality_score=0.75,
        )
        json_data = original.to_json()
        restored = Prompt.from_json(json_data)

        assert restored.id == original.id
        assert restored.category == original.category
        assert restored.prompt == original.prompt
        assert restored.description == original.description
        assert restored.tags == original.tags
        assert restored.quality_score == original.quality_score


class TestPromptRegistry:
    """Test PromptRegistry functionality."""

    @pytest.fixture
    def mock_prompts_dir(self, tmp_path):
        """Create a temporary directory with sample prompt files."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        # Create sample prompt files
        prompt1 = {
            "id": "test1",
            "category": "templates",
            "prompt": "Prompt 1 content",
            "description": "First test prompt",
            "tags": ["test"],
        }
        prompt2 = {
            "id": "test2",
            "category": "profiles",
            "prompt": "Prompt 2 content",
            "description": "Second test prompt",
            "tags": ["profile", "mistral"],
            "model": "mistral-small-latest",
        }
        prompt3 = {
            "id": "code_helper",
            "category": "expert_personas",
            "prompt": "You are a code expert",
            "description": "Code expertise prompt",
            "tags": ["code", "expert"],
        }

        (prompts_dir / "test1.json").write_text(json.dumps(prompt1))
        (prompts_dir / "test2.json").write_text(json.dumps(prompt2))
        (prompts_dir / "code_helper.json").write_text(json.dumps(prompt3))

        return prompts_dir

    def test_registry_loads_all_prompts(self, mock_prompts_dir):
        """Test that PromptRegistry loads all prompts from directory."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        assert len(registry.prompts) == 3
        assert "test1" in registry.prompts
        assert "test2" in registry.prompts
        assert "code_helper" in registry.prompts

    def test_registry_get_prompt(self, mock_prompts_dir):
        """Test retrieving a single prompt by ID."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompt = registry.get("test1")

        assert prompt is not None
        assert prompt.id == "test1"
        assert prompt.prompt == "Prompt 1 content"

    def test_registry_get_missing_prompt_returns_none(self, mock_prompts_dir):
        """Test that getting a non-existent prompt returns None."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompt = registry.get("nonexistent")

        assert prompt is None

    def test_registry_list_all_prompts(self, mock_prompts_dir):
        """Test listing all prompts."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompts = registry.list()

        assert len(prompts) == 3
        # Verify they're sorted by ID
        ids = [p.id for p in prompts]
        assert ids == sorted(ids)

    def test_registry_list_by_category(self, mock_prompts_dir):
        """Test listing prompts filtered by category."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompts = registry.list(category="templates")

        assert len(prompts) == 1
        assert prompts[0].id == "test1"

    def test_registry_list_by_tag(self, mock_prompts_dir):
        """Test listing prompts filtered by tag."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompts = registry.list(tag="expert")

        assert len(prompts) == 1
        assert prompts[0].id == "code_helper"

    def test_registry_search_by_id(self, mock_prompts_dir):
        """Test searching prompts by ID."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        results = registry.search("test")

        assert len(results) == 2
        ids = {p.id for p in results}
        assert ids == {"test1", "test2"}

    def test_registry_search_by_description(self, mock_prompts_dir):
        """Test searching prompts by description."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        results = registry.search("expertise")

        assert len(results) == 1
        assert results[0].id == "code_helper"

    def test_registry_search_by_tag(self, mock_prompts_dir):
        """Test searching prompts by tag."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        results = registry.search("mistral")

        assert len(results) == 1
        assert results[0].id == "test2"

    def test_registry_search_case_insensitive(self, mock_prompts_dir):
        """Test that search is case-insensitive."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        results = registry.search("CODE")

        assert len(results) >= 1
        assert any(p.id == "code_helper" for p in results)

    def test_registry_render_prompt_without_variables(self, mock_prompts_dir):
        """Test rendering a prompt without variable substitution."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        rendered = registry.render("test1", {})

        assert "Prompt 1 content" in rendered

    def test_registry_render_missing_prompt_raises_error(self, mock_prompts_dir):
        """Test that rendering a missing prompt raises ValueError."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        with pytest.raises(ValueError, match="Prompt not found"):
            registry.render("nonexistent", {})

    def test_registry_report_usage_increments_count(self, mock_prompts_dir):
        """Test that reporting usage increments the usage count."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompt = registry.get("test1")
        initial_count = prompt.usage_count

        registry.report_usage("test1", success=True)
        prompt = registry.get("test1")

        assert prompt.usage_count == initial_count + 1

    def test_registry_report_usage_updates_success_rate(self, mock_prompts_dir):
        """Test that reporting usage updates the success rate."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        registry.report_usage("test1", success=True)
        registry.report_usage("test1", success=True)
        registry.report_usage("test1", success=False)

        prompt = registry.get("test1")
        assert prompt.success_rate == pytest.approx(2 / 3)

    def test_registry_report_usage_tracks_tokens(self, mock_prompts_dir):
        """Test that reporting usage tracks average tokens used."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        registry.report_usage("test1", success=True, tokens_used=100)
        registry.report_usage("test1", success=True, tokens_used=200)

        prompt = registry.get("test1")
        assert prompt.avg_tokens_used == pytest.approx(150)

    def test_registry_report_usage_updates_quality_score(self, mock_prompts_dir):
        """Test that quality score is updated based on success rate."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        registry.report_usage("test1", success=True)
        prompt = registry.get("test1")

        assert prompt.quality_score is not None
        assert prompt.quality_score > 0

    def test_registry_report_usage_updates_last_used(self, mock_prompts_dir):
        """Test that reporting usage updates the last_used timestamp."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)
        prompt = registry.get("test1")
        assert prompt.last_used is None

        before = datetime.now()
        registry.report_usage("test1", success=True)
        after = datetime.now()

        prompt = registry.get("test1")
        assert prompt.last_used is not None
        assert before <= prompt.last_used <= after

    def test_registry_report_usage_missing_prompt_raises_error(self, mock_prompts_dir):
        """Test that reporting usage for missing prompt raises ValueError."""
        registry = PromptRegistry(prompts_dir=mock_prompts_dir)

        with pytest.raises(ValueError, match="Prompt not found"):
            registry.report_usage("nonexistent", success=True)
