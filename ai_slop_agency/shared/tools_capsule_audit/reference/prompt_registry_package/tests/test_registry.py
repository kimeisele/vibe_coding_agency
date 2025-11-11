"""Tests for Prompt Registry."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from prompt_registry import PromptRegistry, Prompt


class TestPromptRegistry:
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_dir = Path(self.temp_dir)
        
        # Create test prompt
        test_prompt = {
            "id": "test_prompt",
            "category": "test_category",
            "prompt": "Test prompt with ${variable}",
            "description": "Test prompt description",
            "variables": ["variable"],
            "tags": ["test"],
            "usage_count": 0,
            "version": "1.0"
        }
        
        prompt_file = self.prompts_dir / "test_prompt.json"
        with open(prompt_file, 'w') as f:
            json.dump(test_prompt, f)
        
        self.registry = PromptRegistry(self.prompts_dir)
    
    def test_load_prompts(self):
        """Test loading prompts from directory."""
        assert len(self.registry.prompts) == 1
        assert "test_prompt" in self.registry.prompts
    
    def test_get_prompt(self):
        """Test getting prompt by ID."""
        prompt = self.registry.get("test_prompt")
        assert prompt is not None
        assert prompt.id == "test_prompt"
        assert prompt.category == "test_category"
    
    def test_get_nonexistent_prompt(self):
        """Test getting non-existent prompt."""
        prompt = self.registry.get("nonexistent")
        assert prompt is None
    
    def test_list_prompts(self):
        """Test listing all prompts."""
        prompts = self.registry.list()
        assert len(prompts) == 1
        assert prompts[0].id == "test_prompt"
    
    def test_list_prompts_filtered(self):
        """Test listing prompts with filters."""
        # Filter by category
        prompts = self.registry.list(category="test_category")
        assert len(prompts) == 1
        
        # Filter by non-matching category
        prompts = self.registry.list(category="other_category")
        assert len(prompts) == 0
        
        # Filter by tag
        prompts = self.registry.list(tag="test")
        assert len(prompts) == 1
        
        # Filter by non-matching tag
        prompts = self.registry.list(tag="other_tag")
        assert len(prompts) == 0
    
    def test_search_prompts(self):
        """Test searching prompts."""
        # Search by ID
        results = self.registry.search("test")
        assert len(results) == 1
        
        # Search by description
        results = self.registry.search("description")
        assert len(results) == 1
        
        # Search with no matches
        results = self.registry.search("nonexistent")
        assert len(results) == 0
    
    def test_render_prompt(self):
        """Test rendering prompt with variables."""
        rendered = self.registry.render("test_prompt", {"variable": "value"})
        assert "value" in rendered
        assert "Test prompt with value" == rendered
    
    def test_render_nonexistent_prompt(self):
        """Test rendering non-existent prompt."""
        with pytest.raises(ValueError, match="Prompt not found"):
            self.registry.render("nonexistent", {})
    
    def test_report_usage(self):
        """Test reporting prompt usage."""
        # Report successful usage
        self.registry.report_usage("test_prompt", success=True, tokens_used=100)
        
        prompt = self.registry.get("test_prompt")
        assert prompt.usage_count == 1
        assert prompt.success_rate == 1.0
        assert prompt.avg_tokens_used == 100
        assert prompt.last_used is not None
    
    def test_report_usage_multiple(self):
        """Test reporting multiple usages."""
        # First usage
        self.registry.report_usage("test_prompt", success=True, tokens_used=100)
        
        # Second usage (failed)
        self.registry.report_usage("test_prompt", success=False, tokens_used=150)
        
        prompt = self.registry.get("test_prompt")
        assert prompt.usage_count == 2
        assert prompt.success_rate == 0.5  # 1 success out of 2
        assert prompt.avg_tokens_used == 125  # (100 + 150) / 2


class TestPrompt:
    def test_prompt_from_json(self):
        """Test creating prompt from JSON data."""
        data = {
            "id": "test",
            "category": "test_category",
            "prompt": "Test prompt",
            "description": "Test description",
            "variables": ["var1", "var2"],
            "tags": ["tag1", "tag2"],
            "usage_count": 5,
            "version": "2.0"
        }
        
        prompt = Prompt.from_json(data)
        
        assert prompt.id == "test"
        assert prompt.category == "test_category"
        assert prompt.prompt == "Test prompt"
        assert prompt.description == "Test description"
        assert prompt.variables == ["var1", "var2"]
        assert prompt.tags == ["tag1", "tag2"]
        assert prompt.usage_count == 5
        assert prompt.version == "2.0"
    
    def test_prompt_to_json(self):
        """Test converting prompt to JSON data."""
        prompt = Prompt(
            id="test",
            category="test_category",
            prompt="Test prompt",
            description="Test description",
            variables=["var1"],
            tags=["tag1"],
            usage_count=3
        )
        
        data = prompt.to_json()
        
        assert data["id"] == "test"
        assert data["category"] == "test_category"
        assert data["prompt"] == "Test prompt"
        assert data["description"] == "Test description"
        assert data["variables"] == ["var1"]
        assert data["tags"] == ["tag1"]
        assert data["usage_count"] == 3
