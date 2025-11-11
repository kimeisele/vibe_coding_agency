"""Integration tests for workflow error handling and recovery.

Tests error handling patterns:
- `on_error: stop` halts workflow
- `on_error: continue` logs and continues
- Graceful degradation for non-critical failures
- Error tracking and reporting
"""

from unittest.mock import MagicMock, patch

from agency_toolkit.core.orchestrator import execute_module


class TestWorkflowErrorHandling:
    """Integration tests for error handling in workflows."""

    def test_workflow_stops_on_critical_task_failure(self):
        """Task 2 fails with on_error: stop. Workflow halts.

        Note: The actual behavior is that on_error: stop only stops the workflow
        if stop_on_error context variable is True. When not set, all tasks execute
        but failures are recorded. This test verifies that behavior.

        Verifies:
        - Workflow executes all tasks
        - Failed tasks are recorded in report
        - Report shows correct failed/successful counts
        """
        workflow = {
            "id": "STOP_ON_ERROR",
            "modules": [
                {
                    "id": "M1",
                    "title": "Test Stop on Error",
                    "tasks": [
                        {
                            "tool": "structure",
                            "on_error": "stop",
                            "params": {},
                        },
                        {
                            "tool": "ai",
                            "on_error": "stop",  # This will fail
                            "params": {"prompt": "test"},
                        },
                        {
                            "tool": "social",
                            "on_error": "stop",
                            "params": {"text": "test"},
                        },
                        {
                            "tool": "briefing",
                            "on_error": "stop",
                            "params": {},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test", "stop_on_error": True}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_handler_factory:
            call_count = {"count": 0}

            def get_mock_handler(tool_name):
                handler = MagicMock()
                if tool_name == "ai":
                    # AI task fails
                    handler.execute.side_effect = RuntimeError("AI service unavailable")
                else:

                    def track_success(*args, **kwargs):
                        call_count["count"] += 1
                        return "Success"

                    handler.execute.side_effect = track_success
                return handler

            mock_handler_factory.side_effect = get_mock_handler

            report = execute_module(workflow["modules"][0], context)

            # With stop_on_error=True, workflow stops after failure
            assert report.total_tasks == 4
            assert report.successful == 1  # Only structure succeeded
            assert report.failed == 1  # AI failed
            assert report.skipped == 2  # Tasks 3 and 4 didn't execute
            assert len(report.errors) > 0

    def test_workflow_continues_after_non_critical_failure(self):
        """Task 2 fails with on_error: continue. Workflow continues.

        Verifies:
        - Workflow continues executing after non-critical failure
        - Subsequent tasks still execute
        - All tasks are attempted
        - Report shows success + failure counts
        """
        workflow = {
            "id": "CONTINUE_ON_ERROR",
            "modules": [
                {
                    "id": "M1",
                    "title": "Test Continue on Error",
                    "tasks": [
                        {
                            "tool": "structure",
                            "on_error": "continue",
                            "params": {},
                        },
                        {
                            "tool": "ai",
                            "on_error": "continue",  # This will fail
                            "params": {"prompt": "test"},
                        },
                        {
                            "tool": "social",
                            "on_error": "continue",  # Executes despite previous failure
                            "params": {"text": "test"},
                        },
                        {
                            "tool": "briefing",
                            "on_error": "continue",  # Executes
                            "params": {},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_handler_factory:
            call_count = {"count": 0}

            def get_mock_handler(tool_name):
                handler = MagicMock()
                if tool_name == "ai":
                    # AI task fails but workflow continues
                    handler.execute.side_effect = RuntimeError("API error")
                else:

                    def track_call(*args, **kwargs):
                        call_count["count"] += 1
                        return f"Success: {tool_name}"

                    handler.execute.side_effect = track_call
                return handler

            mock_handler_factory.side_effect = get_mock_handler

            report = execute_module(workflow["modules"][0], context)

            # All 4 tasks attempted
            assert report.total_tasks == 4
            assert report.successful == 3  # structure, social, briefing
            assert report.failed == 1  # ai
            assert report.skipped == 0  # All tasks executed
            assert len(report.task_results) == 4

    def test_mixed_error_modes_in_single_workflow(self):
        """Workflow with mixed on_error modes.

        Verifies:
        - Critical tasks with on_error: stop halt on failure
        - Optional tasks with on_error: continue don't halt
        - Workflow executes correctly with mixed modes
        """
        workflow = {
            "id": "MIXED_ERROR_MODES",
            "modules": [
                {
                    "id": "M1",
                    "tasks": [
                        {
                            "tool": "structure",
                            "on_error": "stop",  # Critical
                            "params": {},
                        },
                        {
                            "tool": "ai",
                            "on_error": "continue",  # Optional - fails but continues
                            "params": {"prompt": "test"},
                        },
                        {
                            "tool": "social",
                            "on_error": "stop",  # Critical - executes after optional failure
                            "params": {"text": "test"},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_handler_factory:

            def get_mock_handler(tool_name):
                handler = MagicMock()
                if tool_name == "ai":
                    handler.execute.side_effect = RuntimeError("AI failed")
                else:
                    handler.execute.return_value = f"{tool_name} succeeded"
                return handler

            mock_handler_factory.side_effect = get_mock_handler

            report = execute_module(workflow["modules"][0], context)

            # Structure succeeds, AI fails but continues, Social succeeds
            assert report.successful == 2  # structure, social
            assert report.failed == 1  # ai
            assert report.skipped == 0  # All tasks attempted

    def test_error_messages_are_captured(self):
        """Verify error messages are properly captured and reported.

        Verifies:
        - Error details are captured
        - Error messages are descriptive
        - Errors list contains all failures
        """
        workflow = {
            "id": "ERROR_MESSAGES",
            "modules": [
                {
                    "id": "M1",
                    "tasks": [
                        {
                            "tool": "ai",
                            "on_error": "continue",
                            "params": {"prompt": "test"},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}
        error_message = "API rate limit exceeded"

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = RuntimeError(error_message)
            mock_handler.return_value = handler

            report = execute_module(workflow["modules"][0], context)

            assert len(report.errors) > 0
            assert any(error_message in str(e) for e in report.errors)

    def test_task_result_has_error_details(self):
        """Verify TaskResult objects contain error information.

        Verifies:
        - Failed tasks have error field populated
        - Success field is False
        - Output is None for failures
        """
        workflow = {
            "id": "TASK_ERROR_DETAILS",
            "modules": [
                {
                    "id": "M1",
                    "tasks": [
                        {
                            "tool": "ai",
                            "on_error": "continue",
                            "params": {"prompt": "test"},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = RuntimeError("Task failed")
            mock_handler.return_value = handler

            report = execute_module(workflow["modules"][0], context)

            # Check failed task result
            failed_result = report.task_results[0]
            assert failed_result.success is False
            assert failed_result.error != ""
            assert failed_result.output is None
            assert failed_result.tool == "ai"

    def test_successful_task_result_structure(self):
        """Verify successful TaskResult has correct structure.

        Verifies:
        - Success field is True
        - Error field is empty
        - Output contains the task result
        """
        workflow = {
            "id": "TASK_SUCCESS_DETAILS",
            "modules": [
                {
                    "id": "M1",
                    "tasks": [
                        {
                            "tool": "structure",
                            "params": {},
                        },
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.return_value = {"status": "created"}
            mock_handler.return_value = handler

            report = execute_module(workflow["modules"][0], context)

            # Check successful task result
            success_result = report.task_results[0]
            assert success_result.success is True
            assert success_result.error == ""
            assert success_result.output is not None
            assert success_result.tool == "structure"

    def test_workflow_execution_report_aggregates_statistics(self):
        """Verify WorkflowExecutionReport correctly aggregates task statistics.

        Verifies:
        - successful count is accurate
        - failed count is accurate
        - skipped count is accurate
        - total_tasks matches actual count
        """
        workflow = {
            "id": "STATS_TEST",
            "modules": [
                {
                    "id": "M1",
                    "tasks": [
                        {"tool": "structure", "on_error": "stop", "params": {}},
                        {"tool": "ai", "on_error": "continue", "params": {}},
                        {"tool": "social", "on_error": "continue", "params": {}},
                        {"tool": "briefing", "on_error": "stop", "params": {}},
                        {"tool": "structure", "on_error": "continue", "params": {}},
                    ],
                }
            ],
        }

        context = {"project_name": "Test"}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_handler_factory:

            def get_mock_handler(tool_name):
                handler = MagicMock()
                # Make AI fail, briefing fail, others succeed
                if tool_name in ["ai", "briefing"]:
                    handler.execute.side_effect = RuntimeError(f"{tool_name} failed")
                else:
                    handler.execute.return_value = "success"
                return handler

            mock_handler_factory.side_effect = get_mock_handler

            report = execute_module(workflow["modules"][0], context)

            # Verify statistics
            assert report.total_tasks == 5
            assert report.successful == 3
            assert report.failed == 2
            assert report.skipped == 0
            assert len(report.task_results) == 5
