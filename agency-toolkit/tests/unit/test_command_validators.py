"""Unit tests for CLI command validators (Epic 1.3.3)."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer

from agency_toolkit.commands.validators import (
    ValidationError,
    handle_validation_error,
    validate_at_least_one,
    validate_directory_exists,
    validate_enum_choice,
    validate_file_exists,
    validate_file_extension,
    validate_mutually_exclusive,
    validate_non_empty_string,
    validate_numerical_range,
)


class TestValidateFileExists:
    """Test file existence validation."""

    def test_validate_file_exists_with_valid_file(self, tmp_path: Path) -> None:
        """Should pass for existing readable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Should not raise
        validate_file_exists(test_file)

    def test_validate_file_exists_returns_none_for_none_path(self) -> None:
        """Should allow None path (optional argument)."""
        # Should not raise
        validate_file_exists(None)

    def test_validate_file_exists_raises_for_missing_file(self) -> None:
        """Should raise for non-existent file."""
        with pytest.raises(ValidationError, match="not found"):
            validate_file_exists(Path("/nonexistent/file.txt"))

    def test_validate_file_exists_raises_for_directory(self, tmp_path: Path) -> None:
        """Should raise if path is a directory."""
        with pytest.raises(ValidationError, match="is not a file"):
            validate_file_exists(tmp_path)

    def test_validate_file_exists_includes_custom_name_in_error(
        self, tmp_path: Path
    ) -> None:
        """Error message should include custom argument name."""
        with pytest.raises(ValidationError, match="config file"):
            validate_file_exists(Path("/nonexistent/config.json"), name="config file")


class TestValidateDirectoryExists:
    """Test directory existence validation."""

    def test_validate_directory_exists_with_valid_directory(
        self, tmp_path: Path
    ) -> None:
        """Should pass for existing accessible directory."""
        # Should not raise
        validate_directory_exists(tmp_path)

    def test_validate_directory_exists_returns_none_for_none_path(self) -> None:
        """Should allow None path (optional argument)."""
        # Should not raise
        validate_directory_exists(None)

    def test_validate_directory_exists_raises_for_missing_directory(self) -> None:
        """Should raise for non-existent directory."""
        with pytest.raises(ValidationError, match="not found"):
            validate_directory_exists(Path("/nonexistent/directory"))

    def test_validate_directory_exists_raises_for_file(self, tmp_path: Path) -> None:
        """Should raise if path is a file, not directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValidationError, match="is not a directory"):
            validate_directory_exists(test_file)


class TestValidateFileExtension:
    """Test file extension validation."""

    def test_validate_file_extension_with_valid_extension(self, tmp_path: Path) -> None:
        """Should pass for files with allowed extensions."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("a,b\n1,2")

        # Should not raise
        validate_file_extension(test_file, {".csv", ".json"})

    def test_validate_file_extension_case_insensitive(self, tmp_path: Path) -> None:
        """Should handle uppercase extensions."""
        test_file = tmp_path / "data.CSV"
        test_file.write_text("a,b\n1,2")

        # Should not raise (should handle .CSV as .csv)
        validate_file_extension(test_file, {".csv"})

    def test_validate_file_extension_raises_for_wrong_extension(
        self, tmp_path: Path
    ) -> None:
        """Should raise for extensions not in allowed set."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("content")

        with pytest.raises(ValidationError, match="must have extension"):
            validate_file_extension(test_file, {".csv", ".json"})

    def test_validate_file_extension_error_lists_allowed(self, tmp_path: Path) -> None:
        """Error message should list allowed extensions."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("content")

        with pytest.raises(ValidationError, match=r"\[\.csv, \.json\]"):
            validate_file_extension(test_file, {".csv", ".json"}, "data file")


class TestValidateEnumChoice:
    """Test enum/choice validation."""

    def test_validate_enum_choice_with_valid_choice(self) -> None:
        """Should pass for value in allowed set."""
        # Should not raise
        validate_enum_choice("bold", {"bold", "modern", "minimal"})

    def test_validate_enum_choice_raises_for_invalid_choice(self) -> None:
        """Should raise for value not in allowed set."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_enum_choice("invalid", {"bold", "modern", "minimal"})

    def test_validate_enum_choice_includes_custom_name(self) -> None:
        """Error message should include custom argument name."""
        with pytest.raises(ValidationError, match="style"):
            validate_enum_choice("invalid", {"bold", "modern"}, "style")

    def test_validate_enum_choice_lists_options(self) -> None:
        """Error message should list available options."""
        with pytest.raises(ValidationError, match=r"\[bold, minimal, modern\]"):
            validate_enum_choice("invalid", {"bold", "modern", "minimal"})


class TestValidateNumericalRange:
    """Test numerical range validation."""

    def test_validate_numerical_range_with_valid_value(self) -> None:
        """Should pass for value within range."""
        # Should not raise
        validate_numerical_range(0.5, min_value=0.0, max_value=1.0)

    def test_validate_numerical_range_no_constraints(self) -> None:
        """Should pass with no constraints."""
        # Should not raise
        validate_numerical_range(999)

    def test_validate_numerical_range_raises_below_minimum(self) -> None:
        """Should raise if value below minimum."""
        with pytest.raises(ValidationError, match="must be >="):
            validate_numerical_range(-1, min_value=0)

    def test_validate_numerical_range_raises_above_maximum(self) -> None:
        """Should raise if value above maximum."""
        with pytest.raises(ValidationError, match="must be <="):
            validate_numerical_range(2.5, max_value=2.0)

    def test_validate_numerical_range_includes_custom_name(self) -> None:
        """Error message should include custom argument name."""
        with pytest.raises(ValidationError, match="temperature"):
            validate_numerical_range(3.0, max_value=2.0, name="temperature")

    def test_validate_numerical_range_with_integers(self) -> None:
        """Should work with integer values."""
        # Should not raise
        validate_numerical_range(50, min_value=0, max_value=100)

        with pytest.raises(ValidationError):
            validate_numerical_range(101, min_value=0, max_value=100)


class TestValidateMutuallyExclusive:
    """Test mutual exclusivity validation."""

    def test_validate_mutually_exclusive_with_none(self) -> None:
        """Should pass when all arguments are None."""
        # Should not raise
        validate_mutually_exclusive(None, None, arg_names=["--from-csv", "--from-json"])

    def test_validate_mutually_exclusive_with_one_arg(self) -> None:
        """Should pass when only one argument is provided."""
        # Should not raise
        validate_mutually_exclusive(
            "value", None, arg_names=["--from-csv", "--from-json"]
        )

    def test_validate_mutually_exclusive_raises_with_multiple_args(self) -> None:
        """Should raise when multiple arguments provided."""
        with pytest.raises(ValidationError, match="Only one"):
            validate_mutually_exclusive(
                "value1", "value2", arg_names=["--from-csv", "--from-json"]
            )

    def test_validate_mutually_exclusive_error_lists_provided_args(self) -> None:
        """Error should list which arguments were provided."""
        with pytest.raises(ValidationError, match="--from-csv.*--from-json"):
            validate_mutually_exclusive(
                "csv_value", "json_value", arg_names=["--from-csv", "--from-json"]
            )


class TestValidateAtLeastOne:
    """Test 'at least one' validation."""

    def test_validate_at_least_one_with_one_arg(self) -> None:
        """Should pass when at least one argument provided."""
        # Should not raise
        validate_at_least_one("value", None, arg_names=["--prompt", "--prompt-file"])

    def test_validate_at_least_one_with_multiple_args(self) -> None:
        """Should pass when multiple arguments provided."""
        # Should not raise
        validate_at_least_one(
            "value1", "value2", arg_names=["--prompt", "--prompt-file"]
        )

    def test_validate_at_least_one_raises_with_no_args(self) -> None:
        """Should raise when all arguments are None."""
        with pytest.raises(ValidationError, match="at least one"):
            validate_at_least_one(None, None, arg_names=["--prompt", "--prompt-file"])

    def test_validate_at_least_one_error_lists_options(self) -> None:
        """Error should list available options."""
        with pytest.raises(ValidationError, match="--prompt.*--prompt-file"):
            validate_at_least_one(None, None, arg_names=["--prompt", "--prompt-file"])


class TestValidateNonEmptyString:
    """Test non-empty string validation."""

    def test_validate_non_empty_string_with_valid_string(self) -> None:
        """Should pass for non-empty string."""
        # Should not raise
        validate_non_empty_string("hello")

    def test_validate_non_empty_string_raises_for_empty_string(self) -> None:
        """Should raise for empty string."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_non_empty_string("")

    def test_validate_non_empty_string_raises_for_whitespace_only(self) -> None:
        """Should raise for whitespace-only string."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_non_empty_string("   ")

    def test_validate_non_empty_string_raises_for_none_by_default(self) -> None:
        """Should raise for None by default."""
        with pytest.raises(ValidationError, match="cannot be None"):
            validate_non_empty_string(None)

    def test_validate_non_empty_string_allows_none_if_specified(self) -> None:
        """Should allow None if allow_none=True."""
        # Should not raise
        validate_non_empty_string(None, allow_none=True)

    def test_validate_non_empty_string_includes_custom_name(self) -> None:
        """Error message should include custom argument name."""
        with pytest.raises(ValidationError, match="prompt"):
            validate_non_empty_string("", name="prompt")


class TestHandleValidationError:
    """Test validation error handling."""

    def test_handle_validation_error_raises_typer_exit(self) -> None:
        """Should raise typer.Exit."""
        error = ValidationError("Test error message")
        reporter = MagicMock()
        reporter.config.json_output = False

        with pytest.raises(typer.Exit):
            handle_validation_error(error, reporter)

    def test_handle_validation_error_exits_with_code_1(self) -> None:
        """Should exit with code 1."""
        error = ValidationError("Test error")
        reporter = MagicMock()
        reporter.config.json_output = False

        with pytest.raises(typer.Exit) as exc_info:
            handle_validation_error(error, reporter)

        assert exc_info.value.exit_code == 1
