"""
Unit tests for refactored social.py module.

Tests cover the refactored validation functions and Reporter integration.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agency_toolkit.commands.social import (
    _determine_processing_mode,
    _handle_social_error,
    _validate_at_least_one_input,
    _validate_batch_file_exclusivity,
    _validate_social_arguments,
    _validate_text_batch_exclusivity,
    social,
)
from agency_toolkit.core.reporter import Reporter


class TestSocialValidationFunctions:
    """Test social argument validation functions."""

    def test_validate_batch_file_exclusivity_both_provided(self):
        """Test validation when both CSV and JSON are provided."""
        mock_reporter = Mock(spec=Reporter)

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            _validate_batch_file_exclusivity(
                Path("test.csv"), Path("test.json"), mock_reporter
            )
            mock_reporter.error.assert_called_once_with(
                "Cannot use both --from-csv and --from-json"
            )

    def test_validate_batch_file_exclusivity_csv_only(self):
        """Test validation when only CSV is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_batch_file_exclusivity(Path("test.csv"), None, mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_batch_file_exclusivity_json_only(self):
        """Test validation when only JSON is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_batch_file_exclusivity(None, Path("test.json"), mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_batch_file_exclusivity_neither_provided(self):
        """Test validation when neither batch file is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_batch_file_exclusivity(None, None, mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_text_batch_exclusivity_text_with_csv(self):
        """Test validation when text is provided with CSV."""
        mock_reporter = Mock(spec=Reporter)

        _validate_text_batch_exclusivity(
            "test text", Path("test.csv"), None, mock_reporter
        )
        mock_reporter.error.assert_called_once_with(
            "Cannot use --text with --from-csv or --from-json"
        )

    def test_validate_text_batch_exclusivity_text_with_json(self):
        """Test validation when text is provided with JSON."""
        mock_reporter = Mock(spec=Reporter)

        _validate_text_batch_exclusivity(
            "test text", None, Path("test.json"), mock_reporter
        )
        mock_reporter.error.assert_called_once_with(
            "Cannot use --text with --from-csv or --from-json"
        )

    def test_validate_text_batch_exclusivity_text_only(self):
        """Test validation when only text is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_text_batch_exclusivity("test text", None, None, mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_at_least_one_input_no_input(self):
        """Test validation when no input is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_at_least_one_input(None, None, None, mock_reporter)
        mock_reporter.error.assert_called_once_with(
            "Must provide text argument or use --from-csv/--from-json"
        )

    def test_validate_at_least_one_input_text_provided(self):
        """Test validation when text is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_at_least_one_input("test text", None, None, mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_at_least_one_input_csv_provided(self):
        """Test validation when CSV is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_at_least_one_input(None, Path("test.csv"), None, mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_at_least_one_input_json_provided(self):
        """Test validation when JSON is provided."""
        mock_reporter = Mock(spec=Reporter)

        _validate_at_least_one_input(None, None, Path("test.json"), mock_reporter)
        mock_reporter.error.assert_not_called()

    def test_validate_social_arguments_valid_combinations(self):
        """Test complete validation with valid argument combinations."""
        mock_reporter = Mock(spec=Reporter)

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            # Test text only
            _validate_social_arguments("test text", None, None)
            mock_reporter.error.assert_not_called()

            # Test CSV only
            _validate_social_arguments(None, Path("test.csv"), None)
            mock_reporter.error.assert_not_called()

            # Test JSON only
            _validate_social_arguments(None, None, Path("test.json"))
            mock_reporter.error.assert_not_called()

    def test_validate_social_arguments_invalid_combinations(self):
        """Test complete validation with invalid argument combinations."""
        mock_reporter = Mock(spec=Reporter)

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            # Test both CSV and JSON
            _validate_social_arguments(None, Path("test.csv"), Path("test.json"))
            assert mock_reporter.error.call_count == 1
            mock_reporter.reset_mock()

            # Test text with CSV
            _validate_social_arguments("test text", Path("test.csv"), None)
            assert mock_reporter.error.call_count == 1
            mock_reporter.reset_mock()

            # Test no input
            _validate_social_arguments(None, None, None)
            assert mock_reporter.error.call_count == 1


class TestProcessingMode:
    """Test processing mode determination."""

    def test_determine_processing_mode_csv(self):
        """Test CSV mode determination."""
        mode = _determine_processing_mode(None, Path("test.csv"), None)
        assert mode == "csv"

    def test_determine_processing_mode_json(self):
        """Test JSON mode determination."""
        mode = _determine_processing_mode(None, None, Path("test.json"))
        assert mode == "json"

    def test_determine_processing_mode_single(self):
        """Test single mode determination."""
        mode = _determine_processing_mode("test text", None, None)
        assert mode == "single"


class TestErrorHandling:
    """Test error handling functions."""

    def test_handle_social_error(self):
        """Test social error handling."""
        mock_config = Mock()
        mock_config.json_output = False
        mock_reporter = Mock(spec=Reporter)
        test_error = Exception("Test error")

        _handle_social_error(mock_config, test_error, mock_reporter)
        mock_reporter.error.assert_called_once_with("Test error", {"module": "social"})


class TestSocialCommand:
    """Test the main social command."""

    @patch("agency_toolkit.commands.social._validate_social_arguments")
    @patch("agency_toolkit.commands.social._determine_processing_mode")
    @patch("agency_toolkit.commands.social._handle_single_post")
    def test_social_command_single_mode(
        self, mock_handle_single, mock_determine_mode, mock_validate
    ):
        """Test social command in single mode."""
        mock_ctx = Mock()
        mock_config = Mock()
        mock_config.json_output = False
        mock_ctx.obj = mock_config

        mock_determine_mode.return_value = "single"
        mock_reporter = Mock(spec=Reporter)

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            social(
                ctx=mock_ctx,
                text="test text",
                style="modern",
                color="blue",
                custom_color=None,
                format_type="square",
                bg_concept=None,
                bg_seed=None,
                output_path=None,
                dry_run=False,
                from_csv=None,
                from_json=None,
            )

        mock_validate.assert_called_once_with("test text", None, None)
        mock_determine_mode.assert_called_once_with("test text", None, None)
        mock_handle_single.assert_called_once()

    @patch("agency_toolkit.commands.social._validate_social_arguments")
    @patch("agency_toolkit.commands.social._determine_processing_mode")
    @patch("agency_toolkit.commands.social._handle_batch_csv")
    def test_social_command_csv_mode(
        self, mock_handle_csv, mock_determine_mode, mock_validate
    ):
        """Test social command in CSV mode."""
        mock_ctx = Mock()
        mock_config = Mock()
        mock_config.json_output = False
        mock_ctx.obj = mock_config

        mock_determine_mode.return_value = "csv"
        mock_reporter = Mock(spec=Reporter)
        csv_path = Path("test.csv")

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            social(
                ctx=mock_ctx,
                text=None,
                style="modern",
                color="blue",
                custom_color=None,
                format_type="square",
                bg_concept=None,
                bg_seed=None,
                output_path=None,
                dry_run=False,
                from_csv=csv_path,
                from_json=None,
            )

        mock_validate.assert_called_once_with(None, csv_path, None)
        mock_determine_mode.assert_called_once_with(None, csv_path, None)
        mock_handle_csv.assert_called_once()

    @patch("agency_toolkit.commands.social._validate_social_arguments")
    @patch("agency_toolkit.commands.social._determine_processing_mode")
    @patch("agency_toolkit.commands.social._handle_batch_json")
    def test_social_command_json_mode(
        self, mock_handle_json, mock_determine_mode, mock_validate
    ):
        """Test social command in JSON mode."""
        mock_ctx = Mock()
        mock_config = Mock()
        mock_config.json_output = False
        mock_ctx.obj = mock_config

        mock_determine_mode.return_value = "json"
        mock_reporter = Mock(spec=Reporter)
        json_path = Path("test.json")

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            social(
                ctx=mock_ctx,
                text=None,
                style="modern",
                color="blue",
                custom_color=None,
                format_type="square",
                bg_concept=None,
                bg_seed=None,
                output_path=None,
                dry_run=False,
                from_csv=None,
                from_json=json_path,
            )

        mock_validate.assert_called_once_with(None, None, json_path)
        mock_determine_mode.assert_called_once_with(None, None, json_path)
        mock_handle_json.assert_called_once()

    @patch("agency_toolkit.commands.social._validate_social_arguments")
    @patch("agency_toolkit.commands.social._handle_social_error")
    def test_social_command_error_handling(self, mock_handle_error, mock_validate):
        """Test social command error handling."""
        mock_ctx = Mock()
        mock_config = Mock()
        mock_config.json_output = False
        mock_ctx.obj = mock_config

        mock_validate.side_effect = Exception("Validation error")
        mock_reporter = Mock(spec=Reporter)

        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            social(
                ctx=mock_ctx,
                text="test text",
                style="modern",
                color="blue",
                custom_color=None,
                format_type="square",
                bg_concept=None,
                bg_seed=None,
                output_path=None,
                dry_run=False,
                from_csv=None,
                from_json=None,
            )

        mock_handle_error.assert_called_once()


class TestIntegration:
    """Integration tests for the refactored social module."""

    def test_validation_integration(self):
        """Test that validation functions work together correctly."""
        mock_reporter = Mock(spec=Reporter)

        # Test all validations pass with valid input
        with patch(
            "agency_toolkit.commands.social.get_reporter", return_value=mock_reporter
        ):
            _validate_social_arguments("test text", None, None)
            mock_reporter.error.assert_not_called()

    def test_processing_mode_integration(self):
        """Test processing mode determination with various inputs."""
        test_cases = [
            ("text", None, None, "single"),
            (None, Path("test.csv"), None, "csv"),
            (None, None, Path("test.json"), "json"),
        ]

        for text, csv_path, json_path, expected_mode in test_cases:
            mode = _determine_processing_mode(text, csv_path, json_path)
            assert mode == expected_mode


if __name__ == "__main__":
    pytest.main([__file__])
