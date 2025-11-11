"""Unit tests for briefing interactive module (Epic 1.4.1)."""

from unittest.mock import patch

from agency_toolkit.core.briefing.interactive import collect_interactive


class TestCollectInteractiveRequiredFields:
    """Test required field collection."""

    def test_collect_single_required_field(self) -> None:
        """Should collect a single required field."""
        questions = {
            "required": [
                {
                    "name": "company_name",
                    "label": "Company Name",
                    "help": "Your business name",
                }
            ]
        }

        with patch("builtins.input", return_value="ACME Corp"):
            result = collect_interactive(questions)

        assert result == {"company_name": "ACME Corp"}

    def test_collect_multiple_required_fields(self) -> None:
        """Should collect multiple required fields in order."""
        questions = {
            "required": [
                {"name": "company_name", "label": "Company Name"},
                {"name": "industry", "label": "Industry"},
                {"name": "contact", "label": "Contact Person"},
            ]
        }

        inputs = iter(["TechCorp", "Technology", "John Doe"])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {
            "company_name": "TechCorp",
            "industry": "Technology",
            "contact": "John Doe",
        }

    def test_required_field_cannot_be_empty(self) -> None:
        """Should re-prompt if required field is left empty."""
        questions = {"required": [{"name": "company", "label": "Company Name"}]}

        # First attempt empty, second attempt with value
        inputs = iter(["", "", "ValidCorp"])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {"company": "ValidCorp"}

    def test_required_field_strips_whitespace(self) -> None:
        """Should strip leading/trailing whitespace from input."""
        questions = {"required": [{"name": "name", "label": "Name"}]}

        with patch("builtins.input", return_value="  TechCorp  "):
            result = collect_interactive(questions)

        assert result == {"name": "TechCorp"}

    def test_field_name_generated_from_label_if_not_specified(self) -> None:
        """Should generate field name from label if not explicitly provided."""
        questions = {
            "required": [
                {"label": "Company Name"}  # No explicit 'name' field
            ]
        }

        with patch("builtins.input", return_value="MyCompany"):
            result = collect_interactive(questions)

        assert "company_name" in result
        assert result["company_name"] == "MyCompany"

    def test_display_help_text_in_prompt(self) -> None:
        """Should include help text in prompt if provided."""
        questions = {
            "required": [
                {
                    "name": "company",
                    "label": "Company Name",
                    "help": "Legal business name",
                }
            ]
        }

        with patch("builtins.input", return_value="Corp") as mock_input:
            collect_interactive(questions)

        # Verify help text was included in prompt
        call_args = mock_input.call_args_list[0][0][0]
        assert "help" in call_args.lower() or "Legal business name" in call_args


class TestCollectInteractiveOptionalFields:
    """Test optional field collection."""

    def test_collect_optional_field_with_input(self) -> None:
        """Should collect optional field when user provides input."""
        questions = {"optional": [{"name": "website", "label": "Website"}]}

        with patch("builtins.input", return_value="https://example.com"):
            result = collect_interactive(questions)

        assert result == {"website": "https://example.com"}

    def test_skip_optional_field_when_empty(self) -> None:
        """Should skip optional field if user presses Enter (empty)."""
        questions = {"optional": [{"name": "website", "label": "Website"}]}

        with patch("builtins.input", return_value=""):
            result = collect_interactive(questions)

        assert result == {}

    def test_multiple_optional_fields(self) -> None:
        """Should handle multiple optional fields, some skipped."""
        questions = {
            "optional": [
                {"name": "website", "label": "Website"},
                {"name": "phone", "label": "Phone"},
                {"name": "address", "label": "Address"},
            ]
        }

        # Provide: website, skip phone, provide address
        inputs = iter(["https://example.com", "", "123 Main St"])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {
            "website": "https://example.com",
            "address": "123 Main St",
        }
        assert "phone" not in result

    def test_optional_list_field_splits_comma_separated(self) -> None:
        """Should split comma-separated values for list-type optional fields."""
        questions = {
            "optional": [
                {
                    "name": "keywords",
                    "label": "Keywords",
                    "type": "list",
                }
            ]
        }

        with patch("builtins.input", return_value="python, web, api"):
            result = collect_interactive(questions)

        assert result == {"keywords": ["python", "web", "api"]}

    def test_optional_list_field_strips_whitespace_from_items(self) -> None:
        """Should strip whitespace from each item in list field."""
        questions = {
            "optional": [{"name": "services", "label": "Services", "type": "list"}]
        }

        with patch(
            "builtins.input", return_value="  web design  ,  api dev  ,  devops  "
        ):
            result = collect_interactive(questions)

        assert result == {"services": ["web design", "api dev", "devops"]}

    def test_optional_non_list_field_does_not_split(self) -> None:
        """Should not split comma-separated values for non-list optional fields."""
        questions = {"optional": [{"name": "description", "label": "Description"}]}

        with patch("builtins.input", return_value="api, web, devops services"):
            result = collect_interactive(questions)

        assert result == {"description": "api, web, devops services"}


class TestCollectInteractiveMixed:
    """Test combinations of required and optional fields."""

    def test_required_and_optional_fields_together(self) -> None:
        """Should handle both required and optional fields."""
        questions = {
            "required": [
                {"name": "company", "label": "Company Name"},
            ],
            "optional": [
                {"name": "website", "label": "Website"},
                {"name": "tags", "label": "Tags", "type": "list"},
            ],
        }

        inputs = iter(["TechCorp", "https://techcorp.com", "startup, ai, ml"])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {
            "company": "TechCorp",
            "website": "https://techcorp.com",
            "tags": ["startup", "ai", "ml"],
        }

    def test_skip_all_optional_fields(self) -> None:
        """Should work correctly when all optional fields are skipped."""
        questions = {
            "required": [
                {"name": "company", "label": "Company Name"},
            ],
            "optional": [
                {"name": "website", "label": "Website"},
                {"name": "phone", "label": "Phone"},
            ],
        }

        inputs = iter(["MyCompany", "", ""])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {"company": "MyCompany"}

    def test_no_required_fields_only_optional(self) -> None:
        """Should work with only optional fields."""
        questions = {
            "optional": [
                {"name": "website", "label": "Website"},
            ]
        }

        with patch("builtins.input", return_value="https://example.com"):
            result = collect_interactive(questions)

        assert result == {"website": "https://example.com"}

    def test_empty_questions_dict_returns_empty_answers(self) -> None:
        """Should return empty dict for empty questions."""
        with patch("builtins.input"):
            result = collect_interactive({})

        assert result == {}


class TestCollectInteractiveEdgeCases:
    """Test edge cases and special scenarios."""

    def test_special_characters_in_input(self) -> None:
        """Should preserve special characters in input."""
        questions = {"required": [{"name": "company", "label": "Company Name"}]}

        with patch("builtins.input", return_value="O'Reilly & Associates, Inc."):
            result = collect_interactive(questions)

        assert result == {"company": "O'Reilly & Associates, Inc."}

    def test_unicode_characters_in_input(self) -> None:
        """Should handle Unicode characters."""
        questions = {"required": [{"name": "name", "label": "Name"}]}

        with patch("builtins.input", return_value="José García 中文 مرحبا"):
            result = collect_interactive(questions)

        assert result == {"name": "José García 中文 مرحبا"}

    def test_very_long_input(self) -> None:
        """Should handle very long text input."""
        questions = {"optional": [{"name": "description", "label": "Description"}]}

        long_text = "a" * 10000
        with patch("builtins.input", return_value=long_text):
            result = collect_interactive(questions)

        assert result == {"description": long_text}

    def test_numeric_input_stays_as_string(self) -> None:
        """Should treat numeric input as strings, not convert to int/float."""
        questions = {"required": [{"name": "count", "label": "Count"}]}

        with patch("builtins.input", return_value="42"):
            result = collect_interactive(questions)

        assert result == {"count": "42"}
        assert isinstance(result["count"], str)

    def test_field_name_with_spaces_converted_to_underscores(self) -> None:
        """Should convert spaces to underscores in auto-generated field names."""
        questions = {
            "required": [
                {"label": "Company Website"}  # Will be converted to company_website
            ]
        }

        with patch("builtins.input", return_value="https://example.com"):
            result = collect_interactive(questions)

        assert "company_website" in result

    def test_repeated_empty_input_on_required_field(self) -> None:
        """Should keep re-prompting for required field until non-empty."""
        questions = {"required": [{"name": "field", "label": "Field"}]}

        # Empty 3 times, then provide value
        inputs = iter(["", "", "", "finally"])
        with patch("builtins.input", side_effect=inputs):
            result = collect_interactive(questions)

        assert result == {"field": "finally"}
