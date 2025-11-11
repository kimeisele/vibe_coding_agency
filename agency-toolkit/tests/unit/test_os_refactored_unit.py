"""Unit tests for refactored os.py functions."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agency_toolkit.commands.os import (
    _batch_process_csv,
    _batch_process_json,
    _display_batch_summary,
    _execute_batch,
    _process_batch_scenario,
    _validate_scenario,
)
from agency_toolkit.core.reporter import Reporter


class TestValidateScenario:
    """Test _validate_scenario function."""

    def test_validate_valid_scenario(self):
        """Test validation of a complete scenario."""
        scenario = {
            "project_name": "Test Project",
            "archetype_id": "I",
            "solution_id": "solution-a1",
            "module_id": "mod-a1-4-recruiting",
        }

        is_valid, error = _validate_scenario(scenario, 1)

        assert is_valid is True
        assert error is None

    def test_validate_missing_required_fields(self):
        """Test validation of scenario with missing fields."""
        scenario = {
            "project_name": "Test Project",
            "archetype_id": "I",
            # Missing solution_id and module_id
        }

        is_valid, error = _validate_scenario(scenario, 1)

        assert is_valid is False
        assert error is not None
        assert error["scenario"] == 1
        assert error["status"] == "SKIPPED"
        assert "Missing: solution_id, module_id" in error["reason"]

    def test_validate_empty_required_fields(self):
        """Test validation of scenario with empty required fields."""
        scenario = {
            "project_name": "Test Project",
            "archetype_id": "",
            "solution_id": "solution-a1",
            "module_id": "mod-a1-4-recruiting",
        }

        is_valid, error = _validate_scenario(scenario, 1)

        assert is_valid is False
        assert error is not None
        assert "Missing: archetype_id" in error["reason"]


class TestProcessBatchScenario:
    """Test _process_batch_scenario function."""

    @patch("agency_toolkit.commands.os._execute_single_scenario")
    def test_process_valid_scenario(self, mock_execute):
        """Test processing a valid scenario."""
        scenario = {
            "project_name": "Test Project",
            "archetype_id": "I",
            "solution_id": "solution-a1",
            "module_id": "mod-a1-4-recruiting",
        }

        mock_execute.return_value = {"scenario": 1, "status": "SUCCESS"}
        mock_reporter = Mock(spec=Reporter)

        result = _process_batch_scenario(scenario, 1, 2, mock_reporter)

        assert result["status"] == "SUCCESS"
        mock_execute.assert_called_once_with(scenario, 1)
        mock_reporter.info.assert_any_call("Scenario 1/2")
        mock_reporter.divider.assert_called_once_with(30)

    def test_process_invalid_scenario(self):
        """Test processing an invalid scenario."""
        scenario = {
            "project_name": "Test Project",
            "archetype_id": "",  # Invalid empty field
        }

        mock_reporter = Mock(spec=Reporter)

        result = _process_batch_scenario(scenario, 1, 2, mock_reporter)

        assert result["status"] == "SKIPPED"
        mock_reporter.error.assert_called()
        mock_reporter.info.assert_any_call("")  # Empty line for spacing


class TestExecuteBatch:
    """Test _execute_batch orchestrator function."""

    @patch("agency_toolkit.commands.os._process_batch_scenario")
    @patch("agency_toolkit.commands.os._display_batch_summary")
    def test_execute_batch_multiple_scenarios(self, mock_display, mock_process):
        """Test executing multiple scenarios."""
        scenarios = [
            {
                "project_name": "Test 1",
                "archetype_id": "I",
                "solution_id": "a1",
                "module_id": "m1",
            },
            {
                "project_name": "Test 2",
                "archetype_id": "II",
                "solution_id": "a2",
                "module_id": "m2",
            },
        ]

        mock_process.side_effect = [
            {"scenario": 1, "status": "SUCCESS"},
            {"scenario": 2, "status": "PARTIAL"},
        ]

        mock_reporter = Mock(spec=Reporter)

        _execute_batch(scenarios, mock_reporter)

        assert mock_process.call_count == 2
        mock_display.assert_called_once()
        mock_reporter.info.assert_any_call("Found 2 scenario(s) to process")

    @patch("agency_toolkit.commands.os._process_batch_scenario")
    @patch("agency_toolkit.commands.os._display_batch_summary")
    def test_execute_batch_empty_scenarios(self, mock_display, mock_process):
        """Test executing empty scenarios list."""
        scenarios = []

        mock_reporter = Mock(spec=Reporter)

        _execute_batch(scenarios, mock_reporter)

        mock_process.assert_not_called()
        mock_display.assert_called_once_with([], mock_reporter)
        mock_reporter.info.assert_any_call("Found 0 scenario(s) to process")


class TestDisplayBatchSummary:
    """Test _display_batch_summary function."""

    def test_display_summary_mixed_results(self):
        """Test displaying summary with mixed result types."""
        results = [
            {
                "scenario": 1,
                "project_name": "Project 1",
                "status": "SUCCESS",
                "tasks": "All tasks completed",
            },
            {
                "scenario": 2,
                "project_name": "Project 2",
                "status": "PARTIAL",
                "tasks": "Some tasks completed",
            },
            {
                "scenario": 3,
                "project_name": "Project 3",
                "status": "ERROR",
                "reason": "Validation failed",
            },
            {
                "scenario": 4,
                "project_name": "Project 4",
                "status": "SKIPPED",
                "reason": "Missing fields",
            },
        ]

        mock_reporter = Mock(spec=Reporter)

        _display_batch_summary(results, mock_reporter)

        # Verify stats reporting
        mock_reporter.success.assert_called_once_with("✓ Success: 1")
        mock_reporter.warning.assert_called_once_with("⚠ Partial: 1")
        mock_reporter.error.assert_called_once_with("✗ Failed: 2", exit_code=0)

    def test_display_summary_all_success(self):
        """Test displaying summary with all successful results."""
        results = [
            {
                "scenario": 1,
                "project_name": "Project 1",
                "status": "SUCCESS",
                "tasks": "All tasks completed",
            },
            {
                "scenario": 2,
                "project_name": "Project 2",
                "status": "SUCCESS",
                "tasks": "All tasks completed",
            },
        ]

        mock_reporter = Mock(spec=Reporter)

        _display_batch_summary(results, mock_reporter)

        mock_reporter.success.assert_called_once_with("✓ Success: 2")
        mock_reporter.warning.assert_called_once_with("⚠ Partial: 0")
        mock_reporter.error.assert_called_once_with("✗ Failed: 0", exit_code=0)

    def test_display_summary_empty_results(self):
        """Test displaying summary with empty results."""
        results = []

        mock_reporter = Mock(spec=Reporter)

        _display_batch_summary(results, mock_reporter)

        mock_reporter.success.assert_called_once_with("✓ Success: 0")
        mock_reporter.warning.assert_called_once_with("⚠ Partial: 0")
        mock_reporter.error.assert_called_once_with("✗ Failed: 0", exit_code=0)


class TestBatchProcessCsv:
    """Test _batch_process_csv function."""

    def test_batch_process_csv_success(self):
        """Test successful CSV batch processing."""
        csv_content = """project_name,archetype_id,solution_id,module_id,ai_provider
Project 1,I,solution-a1,mod-a1-4,google
Project 2,II,solution-b2,mod-b2-5,mistral"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)

        try:
            with patch("agency_toolkit.commands.os._execute_batch") as mock_execute:
                mock_reporter = Mock(spec=Reporter)

                _batch_process_csv(csv_path, mock_reporter)

                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                scenarios = args[0]
                assert len(scenarios) == 2
                assert scenarios[0]["project_name"] == "Project 1"
                assert scenarios[1]["archetype_id"] == "II"

                mock_reporter.info.assert_any_call(f"Processing batch from: {csv_path}")

        finally:
            csv_path.unlink()

    def test_batch_process_csv_file_not_found(self):
        """Test CSV processing with non-existent file."""
        csv_path = Path("nonexistent.csv")

        mock_reporter = Mock(spec=Reporter)

        with pytest.raises(Exception):  # Should raise typer.Exit
            _batch_process_csv(csv_path, mock_reporter)

        mock_reporter.error.assert_called_once_with(f"CSV file not found: {csv_path}")

    def test_batch_process_csv_empty_file(self):
        """Test CSV processing with empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")  # Empty CSV
            csv_path = Path(f.name)

        try:
            mock_reporter = Mock(spec=Reporter)

            _batch_process_csv(csv_path, mock_reporter)

            mock_reporter.warning.assert_called_once_with("No scenarios found in CSV")

        finally:
            csv_path.unlink()


class TestBatchProcessJson:
    """Test _batch_process_json function."""

    def test_batch_process_json_success(self):
        """Test successful JSON batch processing."""
        json_content = [
            {
                "project_name": "Project 1",
                "archetype_id": "I",
                "solution_id": "solution-a1",
                "module_id": "mod-a1-4",
                "ai_provider": "google",
            },
            {
                "project_name": "Project 2",
                "archetype_id": "II",
                "solution_id": "solution-b2",
                "module_id": "mod-b2-5",
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_content, f)
            json_path = Path(f.name)

        try:
            with patch("agency_toolkit.commands.os._execute_batch") as mock_execute:
                mock_reporter = Mock(spec=Reporter)

                _batch_process_json(json_path, mock_reporter)

                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                scenarios = args[0]
                assert len(scenarios) == 2
                assert scenarios[0]["project_name"] == "Project 1"
                assert scenarios[1].get("ai_provider") is None  # Optional field

                mock_reporter.info.assert_any_call(
                    f"Processing batch from: {json_path}"
                )

        finally:
            json_path.unlink()

    def test_batch_process_json_file_not_found(self):
        """Test JSON processing with non-existent file."""
        json_path = Path("nonexistent.json")

        mock_reporter = Mock(spec=Reporter)

        with pytest.raises(Exception):  # Should raise typer.Exit
            _batch_process_json(json_path, mock_reporter)

        mock_reporter.error.assert_called_once_with(f"JSON file not found: {json_path}")

    def test_batch_process_json_invalid_format(self):
        """Test JSON processing with invalid format (not array)."""
        json_content = {"project_name": "Project 1"}  # Object instead of array

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_content, f)
            json_path = Path(f.name)

        try:
            mock_reporter = Mock(spec=Reporter)

            with pytest.raises(Exception):  # Should raise typer.Exit
                _batch_process_json(json_path, mock_reporter)

            mock_reporter.error.assert_called_once_with(
                "JSON must contain an array of scenarios"
            )

        finally:
            json_path.unlink()

    def test_batch_process_json_malformed(self):
        """Test JSON processing with malformed JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON syntax
            json_path = Path(f.name)

        try:
            mock_reporter = Mock(spec=Reporter)

            with pytest.raises(Exception):  # Should raise typer.Exit
                _batch_process_json(json_path, mock_reporter)

            mock_reporter.error.assert_called_once()
            assert "Failed to read JSON" in mock_reporter.error.call_args[0][0]

        finally:
            json_path.unlink()
