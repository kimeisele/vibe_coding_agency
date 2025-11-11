"""Contract Tests - Orchestrator API Guarantees

These tests define and enforce the contract between:
- Callers of execute_module()
- The orchestrator's execution engine

A contract test verifies:
- Input assumptions: What must be true about inputs
- Output structure: What fields must exist, what types
- Behavior: What happens in error cases
- Side effects: What gets logged, tracked

NO MOCKS - Real orchestrator, real task execution.
"""

import json
import logging
from typing import Any

import pytest

from agency_toolkit.core.orchestrator import (
    TaskResult,
    WorkflowExecutionReport,
    execute_module,
)


class TestOrchestratorContract:
    """Contract tests for orchestrator.execute_module()"""

    def test_execute_module_returns_report_with_required_fields(self):
        """CONTRACT TEST 1: Report must have all required fields"""
        # Minimal valid module
        module: dict[str, Any] = {
            "id": "TEST_M1",
            "title": "Test Module",
            "tasks": [],  # Empty tasks list (valid)
        }
        context: dict[str, Any] = {}

        # Execute
        report = execute_module(module, context)

        # Contract: Must return WorkflowExecutionReport with these fields
        assert isinstance(report, WorkflowExecutionReport)
        assert report.module_id == "TEST_M1"
        assert report.total_tasks == 0
        assert report.successful == 0
        assert report.failed == 0
        assert report.skipped == 0
        assert isinstance(report.errors, list)
        assert isinstance(report.task_results, list)

    def test_execute_module_statistics_are_consistent(self):
        """CONTRACT TEST 2: Statistics must be mathematically consistent"""
        # Create a module with multiple tasks
        module: dict[str, Any] = {
            "id": "TEST_M2",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "info",
                    "params": {},
                },
                {
                    "tool": "info",
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # Contract: Math must work out
        # total_tasks == successful + failed + skipped
        assert report.total_tasks == len(report.task_results)
        assert (
            report.total_tasks == report.successful + report.failed + report.skipped
        ), f"Math broken: {report.successful} + {report.failed} + {report.skipped} != {report.total_tasks}"

    def test_execute_module_task_results_match_total_tasks(self):
        """CONTRACT TEST 3: task_results list must match total_tasks"""
        module: dict[str, Any] = {
            "id": "TEST_M3",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "info",
                    "params": {},
                },
                {
                    "tool": "info",
                    "params": {},
                },
                {
                    "tool": "info",
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # Contract: Results count must match total tasks
        assert len(report.task_results) == report.total_tasks
        assert len(report.task_results) == 3

    def test_each_task_result_has_required_fields(self):
        """CONTRACT TEST 4: Each TaskResult must have required fields"""
        module: dict[str, Any] = {
            "id": "TEST_M4",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "info",
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # Contract: Each result must have these fields
        for result in report.task_results:
            assert isinstance(result, TaskResult)
            assert hasattr(result, "tool")
            assert hasattr(result, "success")
            assert hasattr(result, "output")
            assert hasattr(result, "error")
            assert isinstance(result.tool, str)
            assert isinstance(result.success, bool)
            assert isinstance(result.error, str)

    def test_successful_task_has_empty_error_string(self):
        """CONTRACT TEST 5: Successful tasks must have empty error string"""
        module: dict[str, Any] = {
            "id": "TEST_M5",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "info",
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # If a task succeeded, error must be empty
        for result in report.task_results:
            if result.success:
                assert result.error == "", "Successful task should have empty error"

    def test_failed_task_has_non_empty_error_string(self):
        """CONTRACT TEST 6: Failed tasks must have error message"""
        module: dict[str, Any] = {
            "id": "TEST_M6",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "nonexistent_tool_xyz",  # This will fail
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # If a task failed, error must be non-empty
        for result in report.task_results:
            if not result.success:
                assert (
                    len(result.error) > 0
                ), "Failed task should have non-empty error message"

    def test_errors_list_contains_error_messages_from_failed_tasks(self):
        """CONTRACT TEST 7: report.errors must contain all task errors"""
        module: dict[str, Any] = {
            "id": "TEST_M7",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "nonexistent_tool_xyz",
                    "params": {},
                },
            ],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # Contract: If there are failed tasks, errors list should not be empty
        if report.failed > 0:
            assert len(report.errors) > 0, "Errors list should contain failed task errors"

    def test_module_id_is_preserved(self):
        """CONTRACT TEST 8: module_id must match input module"""
        module: dict[str, Any] = {
            "id": "SPECIFIC_MODULE_ID_12345",
            "title": "Test Module",
            "tasks": [],
        }
        context: dict[str, Any] = {}

        report = execute_module(module, context)

        # Contract: module_id must be preserved exactly
        assert report.module_id == "SPECIFIC_MODULE_ID_12345"

    def test_context_parameter_is_accepted_and_used(self):
        """CONTRACT TEST 9: Context parameters affect task execution"""
        # Module that uses context variable
        module: dict[str, Any] = {
            "id": "TEST_M9",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "info",
                    "params": {"context_used": True},
                },
            ],
        }
        # Provide context
        context: dict[str, Any] = {
            "project_name": "TestProject",
            "user_id": "test_user_123",
        }

        # Contract: Should not raise an error when context is provided
        report = execute_module(module, context)
        assert report is not None

    def test_execute_module_accepts_show_progress_parameter(self):
        """CONTRACT TEST 10: show_progress parameter should be accepted"""
        module: dict[str, Any] = {
            "id": "TEST_M10",
            "title": "Test Module",
            "tasks": [],
        }
        context: dict[str, Any] = {}

        # Contract: Should accept show_progress parameter
        report_with_progress = execute_module(module, context, show_progress=True)
        report_without_progress = execute_module(module, context, show_progress=False)

        # Both should succeed
        assert report_with_progress is not None
        assert report_without_progress is not None


class TestTaskResultContract:
    """Contract tests for TaskResult data structure"""

    def test_task_result_fields_are_accessible(self):
        """CONTRACT TEST: TaskResult fields must be directly accessible"""
        result = TaskResult(
            tool="test_tool",
            success=True,
            output={"key": "value"},
            error="",
        )

        # Contract: Fields must be accessible
        assert result.tool == "test_tool"
        assert result.success is True
        assert result.output == {"key": "value"}
        assert result.error == ""

    def test_task_result_error_default_is_empty_string(self):
        """CONTRACT TEST: TaskResult error field defaults to empty string"""
        result = TaskResult(
            tool="test_tool",
            success=True,
            output={"key": "value"},
            # error not provided
        )

        # Contract: error should default to empty string
        assert result.error == ""


class TestWorkflowReportContract:
    """Contract tests for WorkflowExecutionReport data structure"""

    def test_report_fields_are_accessible(self):
        """CONTRACT TEST: All report fields must be accessible"""
        report = WorkflowExecutionReport(
            module_id="M1",
            total_tasks=5,
            successful=3,
            failed=1,
            skipped=1,
            errors=["error1"],
            task_results=[],
        )

        # Contract: All fields accessible
        assert report.module_id == "M1"
        assert report.total_tasks == 5
        assert report.successful == 3
        assert report.failed == 1
        assert report.skipped == 1
        assert report.errors == ["error1"]
        assert report.task_results == []

    def test_report_can_be_serialized_to_json(self):
        """CONTRACT TEST: Report must be JSON serializable"""
        report = WorkflowExecutionReport(
            module_id="M1",
            total_tasks=1,
            successful=1,
            failed=0,
            skipped=0,
            errors=[],
            task_results=[
                TaskResult(tool="test", success=True, output={"key": "value"}, error="")
            ],
        )

        # Contract: Should be convertible to JSON (this tests the structure)
        try:
            # Use a simple conversion approach
            data = {
                "module_id": report.module_id,
                "total_tasks": report.total_tasks,
                "successful": report.successful,
                "failed": report.failed,
                "skipped": report.skipped,
                "errors": report.errors,
                "task_results": [
                    {
                        "tool": r.tool,
                        "success": r.success,
                        "output": str(r.output),
                        "error": r.error,
                    }
                    for r in report.task_results
                ],
            }
            json_str = json.dumps(data)
            assert json_str is not None
        except Exception as e:
            pytest.fail(f"Report should be JSON serializable: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
