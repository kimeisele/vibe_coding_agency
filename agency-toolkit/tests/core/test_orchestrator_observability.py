"""Tests for Observability features in the Orchestrator.

Tests cover structured logging and progress bar functionality.
"""

import logging
from unittest.mock import MagicMock, patch

from agency_toolkit.core.orchestrator import execute_module


class TestStructuredLogging:
    """Test structured logging of orchestrator events."""

    def test_module_started_logged(self, caplog):
        """Verify module_started event is logged."""
        module = {
            "id": "test_module",
            "title": "Test Module",
            "tasks": [],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch("agency_toolkit.core.orchestrator.get_task_handler"):
                execute_module(module, context, show_progress=False)

        # Check that module_started was logged
        assert any("module_started" in record.message for record in caplog.records)

    def test_task_executing_logged(self, caplog):
        """Verify task_executing event is logged for each task."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
                {"tool": "task2", "params": {}},
            ],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

        # Check that task_executing was logged for both tasks
        task_executing_logs = [
            r for r in caplog.records if "task_executing" in r.message
        ]
        assert len(task_executing_logs) == 2

    def test_task_completed_logged(self, caplog):
        """Verify task_completed event is logged after successful execution."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "output_key": "result1", "params": {}},
            ],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "output1"
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

        # Check that task_completed was logged
        assert any("task_completed" in record.message for record in caplog.records)

    def test_task_failed_logged(self, caplog):
        """Verify task_failed event is logged when task raises exception."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "fail_task", "params": {}},
            ],
        }
        context = {"stop_on_error": True}

        with caplog.at_level(logging.ERROR):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.side_effect = RuntimeError("Task failed!")
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

        # Check that task_failed was logged
        assert any("task_failed" in record.message for record in caplog.records)

    def test_module_completed_logged(self, caplog):
        """Verify module_completed event is logged at end."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
            ],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

        # Check that module_completed was logged
        assert any("module_completed" in record.message for record in caplog.records)

    def test_logging_includes_extra_fields(self, caplog):
        """Verify logging includes extra fields like module_id, tool name."""
        module = {
            "id": "test_module",
            "title": "Test Module",
            "tasks": [
                {"tool": "my_tool", "output_key": "result", "params": {}},
            ],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "output"
                mock_get_handler.return_value = mock_handler

                results = execute_module(module, context, show_progress=False)

        # Check that logs contain module and tool information
        assert any("test_module" in str(record.__dict__) for record in caplog.records)
        assert any("my_tool" in str(record.__dict__) for record in caplog.records)

    def test_logging_duration_tracked(self, caplog):
        """Verify task duration_ms is logged."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
            ],
        }
        context = {}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

        # Check that duration_ms is logged
        completed_logs = [r for r in caplog.records if "task_completed" in r.message]
        assert len(completed_logs) > 0
        # duration_ms should be in the extra fields
        assert any("duration_ms" in str(log.__dict__) for log in completed_logs)


class TestProgressBar:
    """Test progress bar functionality."""

    def test_progress_bar_shown_by_default(self):
        """Verify progress bar is shown by default."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
            ],
        }
        context = {}

        with patch("agency_toolkit.core.orchestrator.Progress") as mock_progress:
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                mock_progress_instance = MagicMock()
                mock_progress.return_value = mock_progress_instance

                execute_module(module, context, show_progress=True)

                # Verify Progress was instantiated
                mock_progress.assert_called_once()

    def test_progress_bar_not_shown_when_disabled(self):
        """Verify progress bar is not shown when show_progress=False."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
            ],
        }
        context = {}

        with patch("agency_toolkit.core.orchestrator.Progress") as mock_progress:
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                execute_module(module, context, show_progress=False)

                # Verify Progress was NOT instantiated
                mock_progress.assert_not_called()

    def test_progress_updated_per_task(self):
        """Verify progress bar is updated after each task."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
                {"tool": "task2", "params": {}},
                {"tool": "task3", "params": {}},
            ],
        }
        context = {}

        with patch("agency_toolkit.core.orchestrator.Progress") as mock_progress_class:
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                mock_progress = MagicMock()
                mock_progress_class.return_value = mock_progress

                execute_module(module, context, show_progress=True)

                # Verify update was called 3 times (once per task)
                update_calls = [call for call in mock_progress.update.call_args_list]
                assert len(update_calls) == 3

    def test_progress_initialized_with_total(self):
        """Verify progress bar is initialized with correct total."""
        module = {
            "id": "test_module",
            "tasks": [
                {"tool": "task1", "params": {}},
                {"tool": "task2", "params": {}},
            ],
        }
        context = {}

        with patch("agency_toolkit.core.orchestrator.Progress") as mock_progress_class:
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.return_value = "result"
                mock_get_handler.return_value = mock_handler

                mock_progress = MagicMock()
                mock_progress_class.return_value = mock_progress

                execute_module(module, context, show_progress=True)

                # Verify add_task was called with total=2
                mock_progress.add_task.assert_called_once()
                call_args = mock_progress.add_task.call_args
                assert call_args[1]["total"] == 2


class TestObservabilityIntegration:
    """Integration tests for observability features."""

    def test_complete_workflow_with_observability(self, caplog):
        """Test that observability is properly integrated in complete workflow."""
        module = {
            "id": "integration_test",
            "title": "Integration Test Module",
            "tasks": [
                {"tool": "task1", "output_key": "result1", "params": {}},
                {"tool": "task2", "output_key": "result2", "params": {}},
            ],
        }
        context = {"project_name": "TestProject"}

        with caplog.at_level(logging.INFO):
            with patch(
                "agency_toolkit.core.orchestrator.get_task_handler"
            ) as mock_get_handler:
                mock_handler = MagicMock()
                mock_handler.execute.side_effect = ["output1", "output2"]
                mock_get_handler.return_value = mock_handler

                with patch("agency_toolkit.core.orchestrator.Progress"):
                    report = execute_module(module, context, show_progress=True)

        # Verify complete workflow logged
        log_messages = [r.message for r in caplog.records]
        assert any("module_started" in msg for msg in log_messages)
        assert any("task_executing" in msg for msg in log_messages)
        assert any("task_completed" in msg for msg in log_messages)
        assert any("module_completed" in msg for msg in log_messages)

        # Verify results are still correct
        assert len(report.task_results) == 2
        assert report.task_results[0].success is True
        assert report.task_results[1].success is True
