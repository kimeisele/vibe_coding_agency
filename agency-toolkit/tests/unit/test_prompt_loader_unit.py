"""Unit tests for the Prompt Loader system."""

from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.core.prompt_loader import (
    get_profile,
    get_prompt,
    get_registry,
    list_profiles,
    list_prompts,
    render_prompt,
)
from agency_toolkit.core.prompt_registry import Prompt


class TestPromptLoaderGlobalRegistry:
    """Test the global PromptRegistry instance management."""

    def test_get_registry_returns_singleton(self):
        """Test that get_registry returns the same instance on multiple calls."""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_get_registry_initializes_correctly(self):
        """Test that the global registry is properly initialized."""
        registry = get_registry()

        # The registry should have loaded some prompts from the prompts directory
        assert registry is not None
        assert hasattr(registry, "prompts")
        assert hasattr(registry, "get")
        assert hasattr(registry, "list")
        assert hasattr(registry, "search")


class TestPromptLoaderGetPrompt:
    """Test the get_prompt function."""

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_get_prompt_returns_dict(self, mock_get_registry):
        """Test that get_prompt returns a dictionary."""
        # Create a real Prompt object instead of a mock
        mock_registry = MagicMock()
        test_prompt = Prompt(
            id="test",
            category="templates",
            prompt="Test prompt content",
            description="Test description",
        )

        mock_registry.get.return_value = test_prompt
        mock_get_registry.return_value = mock_registry

        result = get_prompt("test")

        assert isinstance(result, dict)
        assert result["id"] == "test"
        assert result["prompt"] == "Test prompt content"
        assert result["description"] == "Test description"

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_get_prompt_returns_none_for_missing_prompt(self, mock_get_registry):
        """Test that get_prompt returns None for non-existent prompts."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None
        mock_get_registry.return_value = mock_registry

        result = get_prompt("nonexistent")

        assert result is None


class TestPromptLoaderGetProfile:
    """Test the get_profile function."""

    @patch("agency_toolkit.core.prompt_loader.get_prompt")
    def test_get_profile_calls_get_prompt(self, mock_get_prompt):
        """Test that get_profile delegates to get_prompt."""
        mock_profile_data = {
            "id": "code",
            "model": "mistral-small-latest",
            "temperature": 0.2,
            "prompt": "You are a code expert",
        }
        mock_get_prompt.return_value = mock_profile_data

        result = get_profile("code")

        assert result == mock_profile_data
        mock_get_prompt.assert_called_once_with("code")

    @patch("agency_toolkit.core.prompt_loader.get_prompt")
    def test_get_profile_returns_none_for_missing_profile(self, mock_get_prompt):
        """Test that get_profile returns None for missing profiles."""
        mock_get_prompt.return_value = None

        result = get_profile("nonexistent")

        assert result is None


class TestPromptLoaderListProfiles:
    """Test the list_profiles function."""

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_list_profiles_returns_list(self, mock_get_registry):
        """Test that list_profiles returns a list of profile dictionaries."""
        mock_registry = MagicMock()

        # Create real Prompt objects instead of mocks
        prompt1 = Prompt(id="default", category="profiles", prompt="Default profile")
        prompt2 = Prompt(id="code", category="profiles", prompt="Code profile")

        mock_registry.list.return_value = [prompt1, prompt2]
        mock_get_registry.return_value = mock_registry

        result = list_profiles()

        assert isinstance(result, list)
        assert len(result) == 2
        mock_registry.list.assert_called_once_with(category="profiles")

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_list_profiles_returns_empty_list_when_no_profiles(self, mock_get_registry):
        """Test that list_profiles returns empty list when no profiles exist."""
        mock_registry = MagicMock()
        mock_registry.list.return_value = []
        mock_get_registry.return_value = mock_registry

        result = list_profiles()

        assert isinstance(result, list)
        assert len(result) == 0


class TestPromptLoaderListPrompts:
    """Test the list_prompts function."""

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_list_prompts_returns_all_prompts_by_default(self, mock_get_registry):
        """Test that list_prompts returns all prompts when no category specified."""
        mock_registry = MagicMock()

        prompt1 = Prompt(id="template1", category="templates", prompt="Template 1")
        prompt2 = Prompt(id="template2", category="templates", prompt="Template 2")

        mock_registry.list.return_value = [prompt1, prompt2]
        mock_get_registry.return_value = mock_registry

        result = list_prompts()

        assert len(result) == 2
        mock_registry.list.assert_called_once_with(category=None)

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_list_prompts_filters_by_category(self, mock_get_registry):
        """Test that list_prompts filters by category when specified."""
        mock_registry = MagicMock()

        prompt = Prompt(
            id="code_template", category="templates", prompt="Code template"
        )

        mock_registry.list.return_value = [prompt]
        mock_get_registry.return_value = mock_registry

        result = list_prompts(category="templates")

        assert len(result) == 1
        mock_registry.list.assert_called_once_with(category="templates")

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_list_prompts_returns_empty_list_when_no_matches(self, mock_get_registry):
        """Test that list_prompts returns empty list when no prompts match filter."""
        mock_registry = MagicMock()
        mock_registry.list.return_value = []
        mock_get_registry.return_value = mock_registry

        result = list_prompts(category="nonexistent")

        assert result == []


class TestPromptLoaderRenderPrompt:
    """Test the render_prompt function."""

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_render_prompt_with_variables(self, mock_get_registry):
        """Test rendering a prompt with variable substitution."""
        mock_registry = MagicMock()
        mock_registry.render.return_value = "Rendered prompt with substituted values"
        mock_get_registry.return_value = mock_registry

        result = render_prompt("template", {"var1": "value1", "var2": "value2"})

        assert result == "Rendered prompt with substituted values"
        mock_registry.render.assert_called_once_with(
            "template", {"var1": "value1", "var2": "value2"}
        )

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_render_prompt_without_variables(self, mock_get_registry):
        """Test rendering a prompt without variables."""
        mock_registry = MagicMock()
        mock_registry.render.return_value = "Static prompt content"
        mock_get_registry.return_value = mock_registry

        result = render_prompt("static_prompt", {})

        assert result == "Static prompt content"

    @patch("agency_toolkit.core.prompt_loader.get_registry")
    def test_render_prompt_raises_error_for_missing_prompt(self, mock_get_registry):
        """Test that rendering a missing prompt raises an error."""
        mock_registry = MagicMock()
        mock_registry.render.side_effect = ValueError("Prompt not found: nonexistent")
        mock_get_registry.return_value = mock_registry

        with pytest.raises(ValueError, match="Prompt not found"):
            render_prompt("nonexistent", {})
