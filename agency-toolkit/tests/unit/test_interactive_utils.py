"""Unit tests for interactive CLI utilities."""

import questionary

from agency_toolkit.core.interactive_utils import (
    confirm_action,
    display_summary,
    prompt_for_briefing_type,
    prompt_for_social_post,
    prompt_for_structure_type,
    prompt_with_fallback,
)


class TestSocialPostPrompt:
    """Tests for interactive social post prompt."""

    def test_prompt_for_social_post_returns_dict_with_required_keys(self, monkeypatch):
        """Verify prompt returns dict with all required keys."""
        # Mock questionary responses
        responses = [
            "Hello World",  # text
            "modern",  # style
            "blue",  # color
            "square",  # format
            False,  # add_bg (confirm)
        ]
        call_count = [0]

        def mock_text(prompt_text, validate=None):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        def mock_select(prompt_text, choices, default=None):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        def mock_confirm(prompt_text, default=False):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        monkeypatch.setattr(questionary, "text", mock_text)
        monkeypatch.setattr(questionary, "select", mock_select)
        monkeypatch.setattr(questionary, "confirm", mock_confirm)

        result = prompt_for_social_post()

        assert result is not None
        assert result["text"] == "Hello World"
        assert result["style"] == "modern"
        assert result["color"] == "blue"
        assert result["format"] == "square"
        assert result["bg_concept"] is None  # Since we said no to AI background

    def test_prompt_returns_none_if_text_empty(self, monkeypatch):
        """Verify prompt returns None if user doesn't enter text."""

        def mock_text(prompt_text, validate=None):
            class MockQuestionary:
                def ask(self):
                    return None

            return MockQuestionary()

        monkeypatch.setattr(questionary, "text", mock_text)

        result = prompt_for_social_post()
        assert result is None


class TestBriefingTypePrompt:
    """Tests for briefing type prompt."""

    def test_prompt_for_briefing_type_returns_valid_type(self, monkeypatch):
        """Verify briefing type prompt returns valid choice."""

        def mock_select(prompt_text, choices, default=None):
            class MockQuestionary:
                def ask(self):
                    return "web"

            return MockQuestionary()

        monkeypatch.setattr(questionary, "select", mock_select)

        result = prompt_for_briefing_type()
        assert result == "web"
        assert result in ["web", "video", "brand", "campaign"]

    def test_briefing_type_choices_are_correct(self, monkeypatch):
        """Verify briefing type prompt shows correct choices."""
        choices_received = []

        def mock_select(prompt_text, choices, default=None):
            choices_received.append(choices)

            class MockQuestionary:
                def ask(self):
                    # Return the value from first choice dict
                    return (
                        choices[0]["value"]
                        if isinstance(choices[0], dict)
                        else choices[0]
                    )

            return MockQuestionary()

        monkeypatch.setattr(questionary, "select", mock_select)

        prompt_for_briefing_type()

        # Choices are now dicts with 'name' and 'value' keys
        assert isinstance(choices_received[0], list)
        assert len(choices_received[0]) == 4  # web, video, brand, campaign

        # Check that all expected types are present
        choice_values = [c["value"] for c in choices_received[0]]
        assert "web" in choice_values
        assert "video" in choice_values
        assert "brand" in choice_values
        assert "campaign" in choice_values


class TestStructureTypePrompt:
    """Tests for folder structure type prompt."""

    def test_prompt_for_structure_type_returns_valid_type(self, monkeypatch):
        """Verify structure type prompt returns valid choice."""

        def mock_select(prompt_text, choices, default=None):
            class MockQuestionary:
                def ask(self):
                    return "video"

            return MockQuestionary()

        monkeypatch.setattr(questionary, "select", mock_select)

        result = prompt_for_structure_type()
        assert result == "video"
        assert result in ["web", "video", "brand", "campaign"]


class TestConfirmAction:
    """Tests for confirmation prompt."""

    def test_confirm_action_returns_true_when_confirmed(self, monkeypatch):
        """Verify confirm returns True when user confirms."""

        def mock_confirm(prompt_text, auto_enter=False):
            class MockQuestionary:
                def ask(self):
                    return True

            return MockQuestionary()

        monkeypatch.setattr(questionary, "confirm", mock_confirm)

        result = confirm_action("Proceed?")
        assert result is True

    def test_confirm_action_returns_false_when_declined(self, monkeypatch):
        """Verify confirm returns False when user declines."""

        def mock_confirm(prompt_text, auto_enter=False):
            class MockQuestionary:
                def ask(self):
                    return False

            return MockQuestionary()

        monkeypatch.setattr(questionary, "confirm", mock_confirm)

        result = confirm_action("Proceed?")
        assert result is False


class TestDisplaySummary:
    """Tests for summary display."""

    def test_display_summary_prints_title_and_items(self, capsys):
        """Verify summary displays title and items."""
        items = {
            "Name": "Test Project",
            "Status": "Active",
            "Owner": "John Doe",
        }

        display_summary("Summary", items)

        captured = capsys.readouterr()
        assert "Summary" in captured.out
        assert "Test Project" in captured.out
        assert "Active" in captured.out
        assert "John Doe" in captured.out

    def test_display_summary_formats_with_separators(self, capsys):
        """Verify summary is formatted with separators."""
        display_summary("Test", {"key": "value"})

        captured = capsys.readouterr()
        assert "=" * 50 in captured.out


class TestPromptWithFallback:
    """Tests for prompt with fallback."""

    def test_prompt_with_fallback_interactive_mode(self, monkeypatch):
        """Verify fallback prompt works in interactive mode."""

        def mock_text(prompt_text, default=None):
            class MockQuestionary:
                def ask(self):
                    return "user input"

            return MockQuestionary()

        monkeypatch.setattr(questionary, "text", mock_text)

        result = prompt_with_fallback(
            "Enter value:", interactive=True, default="default"
        )
        assert result == "user input"

    def test_prompt_with_fallback_returns_default_if_empty(self, monkeypatch):
        """Verify fallback returns default if user doesn't input."""

        def mock_text(prompt_text, default=None):
            class MockQuestionary:
                def ask(self):
                    return None

            return MockQuestionary()

        monkeypatch.setattr(questionary, "text", mock_text)

        result = prompt_with_fallback(
            "Enter value:", interactive=True, default="default"
        )
        # None is returned from questionary, not default
        assert result is None


class TestInteractiveUtilsIntegration:
    """Integration tests for interactive utilities."""

    def test_social_post_flow_collects_all_information(self, monkeypatch):
        """Verify complete social post collection flow."""
        responses = [
            "Check this out!",
            "bold",
            "red",
            "landscape",
            False,  # add background
        ]
        call_count = [0]

        def mock_text(prompt_text, validate=None):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        def mock_select(prompt_text, choices, default=None):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        def mock_confirm(prompt_text, default=False):
            class MockQuestionary:
                def ask(self):
                    result = responses[call_count[0]]
                    call_count[0] += 1
                    return result

            return MockQuestionary()

        monkeypatch.setattr(questionary, "text", mock_text)
        monkeypatch.setattr(questionary, "select", mock_select)
        monkeypatch.setattr(questionary, "confirm", mock_confirm)

        result = prompt_for_social_post()

        # Verify all fields were collected
        assert result["text"] == "Check this out!"
        assert result["style"] == "bold"
        assert result["color"] == "red"
        assert result["format"] == "landscape"
