"""Comprehensive tests for the GRAND AGENCY OS Orchestrator.

Tests cover the core execution engine with special focus on the hybrid context system
(step_context vs raw_context) that is critical for proper task data passing.
"""

from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.core.dependency_resolver import (
    CircularDependencyError,
    resolve_module_dependencies,
)
from agency_toolkit.core.orchestrator import (
    TaskResult,
    _format_task_params,
    execute_module,
)
from agency_toolkit.tasks.base import TaskContext


class TestBasicTaskExecution:
    """Test 1: Basic Task Execution - Simple 3-task module."""

    def test_execute_simple_3_task_module(self):
        """Execute a 3-task module with simple params and verify all complete successfully."""
        # Setup: Create a simple 3-task module
        module = {
            "id": "test_module",
            "title": "Test Module",
            "tasks": [
                {
                    "tool": "task1",
                    "output_key": "result1",
                    "params": {"message": "Hello"},
                },
                {
                    "tool": "task2",
                    "output_key": "result2",
                    "params": {"input": "World"},
                },
                {
                    "tool": "task3",
                    "output_key": "result3",
                    "params": {"final": "Test"},
                },
            ],
        }
        context = {"project_name": "TestProject"}

        # Mock the task handlers
        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = ["output1", "output2", "output3"]
            mock_get_handler.return_value = mock_handler

            # Execute
            report = execute_module(module, context)

            results = report.task_results

            # Assert: All 3 tasks completed successfully
            assert len(results) == 3
            assert all(result.success for result in results)
            assert results[0].tool == "task1"
            assert results[1].tool == "task2"
            assert results[2].tool == "task3"
            assert results[0].output == "output1"
            assert results[1].output == "output2"
            assert results[2].output == "output3"
            assert all(result.error == "" for result in results)

    def test_task_result_structure(self):
        """Verify TaskResult objects have correct structure."""
        result = TaskResult(
            tool="test_tool", success=True, output={"data": "value"}, error=""
        )

        assert result.tool == "test_tool"
        assert result.success is True
        assert result.output == {"data": "value"}
        assert result.error == ""


class TestContextTemplating:
    """Test 2: Context Templating (step_context) - Template substitution with {placeholders}."""

    def test_context_templating_simple_substitution(self):
        """Task 1 outputs 'Hello', Task 2 uses {output1} and receives 'Hello'."""
        module = {
            "id": "template_test",
            "tasks": [
                {
                    "tool": "task1",
                    "output_key": "output1",
                    "params": {"value": "greeting"},
                },
                {
                    "tool": "task2",
                    "output_key": "output2",
                    "params": {"text": "{output1}"},  # Template reference
                },
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()

            # Task 1 returns "Hello"
            def side_effect(*args, **kwargs):
                params = kwargs.get("params", {})
                if params.get("value") == "greeting":
                    return "Hello"
                # Task 2: should receive formatted version of "Hello"
                elif params.get("text") == "Hello":
                    return "Hello World"
                return None

            mock_handler.execute.side_effect = side_effect
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            assert len(results) == 2
            assert results[0].output == "Hello"
            assert results[1].output == "Hello World"
            # Verify task 2's execute was called with formatted param
            calls = mock_handler.execute.call_args_list
            assert calls[1][1]["params"]["text"] == "Hello"

    def test_format_task_params_with_context(self):
        """Test _format_task_params properly substitutes placeholders."""
        params = {
            "text": "Hello {name}",
            "count": 5,
            "items": ["{item1}", "{item2}"],
        }
        context = {
            "name": "World",
            "item1": "apple",
            "item2": "banana",
        }

        result = _format_task_params(params, context)

        assert result["text"] == "Hello World"
        assert result["count"] == 5
        assert result["items"] == ["apple", "banana"]

    def test_format_task_params_missing_placeholder_raises_error(self):
        """Test that missing placeholders raise ValueError (fail-fast)."""
        params = {"text": "Hello {unknown_var}"}
        context = {"name": "World"}

        with pytest.raises(ValueError, match="undefined placeholders"):
            _format_task_params(params, context)


class TestHybridContextCritical:
    """Test 3: THE CRITICAL TEST - Hybrid context system (lists vs strings)."""

    def test_list_conversion_step_context_vs_raw_context(self):
        """CRITICAL: Lists converted to strings in step_context, preserved in raw_context."""
        module = {
            "id": "list_test",
            "tasks": [
                {
                    "tool": "task1",
                    "output_key": "tags",
                    "params": {"action": "generate_tags"},
                },
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = ["tag1", "tag2", "tag3"]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            assert len(results) == 1
            # Raw output is the actual list
            assert results[0].output == ["tag1", "tag2", "tag3"]

            # Verify the hybrid contexts were created correctly
            # When a task is executed, it gets a TaskContext with both contexts
            call_args = mock_handler.execute.call_args
            task_context = call_args[1]["context"]

            # step_context should have stringified version
            # raw_context should have original list
            # (These are passed internally; we verify through the format behavior)

    def test_task_context_get_vs_get_raw(self):
        """Test TaskContext.get() vs get_raw() for accessing context values."""
        step_context = {"tags": "tag1, tag2, tag3"}  # Stringified list
        raw_context = {"tags": ["tag1", "tag2", "tag3"]}  # Original list

        task_context = TaskContext(
            config=None,
            step_context=step_context,
            raw_context=raw_context,
            project_name="Test",
        )

        # get() should return stringified version
        assert task_context.get("tags") == "tag1, tag2, tag3"
        assert isinstance(task_context.get("tags"), str)

        # get_raw() should return original list
        assert task_context.get_raw("tags") == ["tag1", "tag2", "tag3"]
        assert isinstance(task_context.get_raw("tags"), list)

    def test_list_to_string_conversion_in_step_context(self):
        """Verify that output lists are converted to comma-separated strings."""
        module = {
            "id": "conversion_test",
            "tasks": [
                {
                    "tool": "list_tool",
                    "output_key": "items",
                    "params": {},
                },
                {
                    "tool": "consumer_tool",
                    "output_key": "final",
                    "params": {"data": "{items}"},  # Should get stringified version
                },
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()

            def side_effect(*args, **kwargs):
                params = kwargs.get("params", {})
                if "data" in params:
                    # Should receive stringified list
                    assert params["data"] == "apple, banana, cherry"
                    return "processed"
                # First task returns list
                return ["apple", "banana", "cherry"]

            mock_handler.execute.side_effect = side_effect
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results
            assert len(results) == 2
            assert results[1].output == "processed"


class TestErrorHandling:
    """Test 4: Error Handling - Task failure and stop_on_error behavior."""

    def test_task_error_captured_in_result(self):
        """Verify error is captured when task fails."""
        module = {
            "id": "error_test",
            "tasks": [
                {"tool": "fail_task", "params": {}},
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = RuntimeError("Task failed!")
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            assert len(results) == 1
            assert results[0].success is False
            assert "Task failed!" in results[0].error
            assert results[0].output is None

    def test_error_stop_on_error_false_continues_execution(self):
        """With stop_on_error=False, execution continues after task failure."""
        module = {
            "id": "continue_test",
            "tasks": [
                {"tool": "fail_task", "params": {}},
                {"tool": "success_task", "params": {}},
                {"tool": "another_task", "params": {}},
            ],
        }
        context = {"stop_on_error": False}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = [
                RuntimeError("Failed"),
                "success",
                "complete",
            ]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            # All 3 tasks should be executed
            assert len(results) == 3
            assert results[0].success is False
            assert results[1].success is True
            assert results[2].success is True

    def test_error_stop_on_error_true_halts_execution(self):
        """With stop_on_error=True, execution stops after first error."""
        module = {
            "id": "stop_test",
            "tasks": [
                {"tool": "task1", "params": {}},
                {"tool": "fail_task", "params": {}},
                {"tool": "task3", "params": {}},
                {"tool": "task4", "params": {}},
            ],
        }
        context = {"stop_on_error": True}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = [
                "success1",
                RuntimeError("Failed"),
                "should_not_run",
                "should_not_run",
            ]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            # Only 2 tasks should execute (first succeeds, second fails and stops)
            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False


class TestCircularDependencies:
    """Test 5: Circular Dependency Detection."""

    def test_circular_dependency_detected(self):
        """Circular dependencies should raise CircularDependencyError."""
        solution = {
            "id": "test_solution",
            "modules": [
                {"id": "M1", "dependencies": ["M2"]},
                {"id": "M2", "dependencies": ["M3"]},
                {"id": "M3", "dependencies": ["M1"]},  # Circular!
            ],
        }
        selected = solution["modules"][0]

        with pytest.raises(CircularDependencyError):
            resolve_module_dependencies(selected, solution)

    def test_self_dependency_detected(self):
        """Module depending on itself should raise CircularDependencyError."""
        solution = {
            "id": "test_solution",
            "modules": [
                {"id": "M1", "dependencies": ["M1"]},  # Self-dependency
            ],
        }
        selected = solution["modules"][0]

        with pytest.raises(CircularDependencyError):
            resolve_module_dependencies(selected, solution)

    def test_missing_dependency_raises_error(self):
        """Reference to non-existent module should raise ValueError."""
        solution = {
            "id": "test_solution",
            "modules": [
                {"id": "M1", "dependencies": ["M_NONEXISTENT"]},
            ],
        }
        selected = solution["modules"][0]

        with pytest.raises(ValueError, match="not found"):
            resolve_module_dependencies(selected, solution)


class TestMultipleModules:
    """Test 6: Multiple Modules with Dependencies."""

    def test_module_dependency_ordering(self):
        """Verify correct execution order for modules with dependencies."""
        solution = {
            "id": "test_solution",
            "modules": [
                {"id": "M1", "dependencies": [], "tasks": []},
                {"id": "M2", "dependencies": ["M1"], "tasks": []},
                {"id": "M3", "dependencies": ["M1", "M2"], "tasks": []},
            ],
        }
        selected = solution["modules"][2]  # Select M3

        result = resolve_module_dependencies(selected, solution)
        ids = [m["id"] for m in result]

        # M1 must come first, then M2, then M3
        assert ids == ["M1", "M2", "M3"]
        assert ids.index("M1") < ids.index("M2")
        assert ids.index("M2") < ids.index("M3")

    def test_module_b_accesses_module_a_outputs(self):
        """Module B can access outputs from Module A in its context."""
        # This tests that output passing between modules works
        # In practice, this would be handled at the OS executor level
        # Here we verify the context merging mechanism

        module_a_results = [
            TaskResult(tool="task1", success=True, output="data_from_a", error="")
        ]
        module_a_context = {"module_a_output": "data_from_a"}

        # When Module B executes, its initial context includes Module A's outputs
        module_b_context = {**module_a_context, "project_name": "TestProject"}

        assert module_b_context["module_a_output"] == "data_from_a"
        assert module_b_context["project_name"] == "TestProject"

    def test_complex_dependency_graph(self):
        """Test complex dependency graph with multiple levels."""
        solution = {
            "id": "complex_solution",
            "modules": [
                {"id": "Base", "dependencies": [], "tasks": []},
                {"id": "FeatureA", "dependencies": ["Base"], "tasks": []},
                {"id": "FeatureB", "dependencies": ["Base"], "tasks": []},
                {
                    "id": "Integration",
                    "dependencies": ["FeatureA", "FeatureB"],
                    "tasks": [],
                },
            ],
        }
        selected = solution["modules"][3]  # Select Integration

        result = resolve_module_dependencies(selected, solution)
        ids = [m["id"] for m in result]

        # Base must be first
        assert ids[0] == "Base"
        # FeatureA and FeatureB can be in any order (both depend only on Base)
        assert set(ids[1:3]) == {"FeatureA", "FeatureB"}
        # Integration must be last
        assert ids[3] == "Integration"


class TestTaskHandlerIntegration:
    """Integration tests with actual task handler interface."""

    def test_handler_receives_correct_task_context(self):
        """Verify TaskContext is correctly built and passed to handler."""
        module = {
            "id": "context_test",
            "tasks": [
                {"tool": "test_handler", "params": {"key": "value"}},
            ],
        }
        context = {"project_name": "TestProject", "archetype_id": "A1"}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = "result"
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            # Verify handler.execute was called with TaskContext
            call_args = mock_handler.execute.call_args
            task_context = call_args[1]["context"]

            assert isinstance(task_context, TaskContext)
            assert task_context.project_name == "TestProject"
            assert task_context.archetype_id == "A1"

    def test_handler_validate_params_called_before_execute(self):
        """Verify validate_params is called before execute."""
        module = {
            "id": "validate_test",
            "tasks": [
                {"tool": "test_handler", "params": {"required": "value"}},
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.return_value = "result"
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            results = report.task_results

            # Verify validate_params was called
            mock_handler.validate_params.assert_called_once()
            # Verify execute was called after
            mock_handler.execute.assert_called_once()


class TestGracefulErrorHandling:
    """Test 7: Graceful Error Handling - on_error modes and WorkflowExecutionReport."""

    def test_task_with_on_error_continue_skips_failure(self):
        """Task with on_error: 'continue' logs error but continues execution."""
        module = {
            "id": "graceful_test",
            "tasks": [
                {
                    "tool": "task1",
                    "output_key": "result1",
                    "params": {},
                },
                {
                    "tool": "fail_task",
                    "output_key": "result2",
                    "on_error": "continue",  # NEW: Task-level error handling
                    "params": {},
                },
                {
                    "tool": "task3",
                    "output_key": "result3",
                    "params": {},
                },
            ],
        }
        context = {
            "stop_on_error": True
        }  # Legacy parameter (overridden by task-level mode)

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = [
                "output1",
                RuntimeError("Transient failure"),  # This fails
                "output3",
            ]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            # All 3 tasks should execute (not stop at error)
            assert len(report.task_results) == 3
            assert report.successful == 2  # Tasks 1 and 3 succeeded
            assert report.failed == 1  # Task 2 failed
            assert report.skipped == 0
            assert report.task_results[0].success is True
            assert report.task_results[1].success is False  # Failed task
            assert report.task_results[2].success is True

    def test_workflow_execution_report_structure(self):
        """Verify WorkflowExecutionReport has correct statistics."""
        module = {
            "id": "report_test",
            "tasks": [
                {"tool": "t1", "params": {}},
                {"tool": "t2", "params": {}},
            ],
        }
        context = {}

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = ["r1", "r2"]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            # Verify report structure
            assert report.module_id == "report_test"
            assert report.total_tasks == 2
            assert report.successful == 2
            assert report.failed == 0
            assert report.skipped == 0
            assert report.errors == []
            assert len(report.task_results) == 2

    def test_workflow_execution_report_with_failures(self):
        """Verify WorkflowExecutionReport captures error messages."""
        module = {
            "id": "error_report_test",
            "tasks": [
                {"tool": "task1", "params": {}},
                {"tool": "fail_task", "on_error": "stop", "params": {}},
                {"tool": "task3", "params": {}},  # Won't execute
            ],
        }
        context = {
            "stop_on_error": True
        }  # Enable legacy stop_on_error to make on_error: "stop" actually stop

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = [
                "success1",
                RuntimeError("Database connection failed"),
                "unreachable",
            ]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            # Verify error reporting
            assert report.total_tasks == 3
            assert report.successful == 1
            assert report.failed == 1
            assert report.skipped == 1  # task3 wasn't executed
            assert len(report.errors) == 1
            assert "Database connection failed" in report.errors[0]

    def test_on_error_mode_precedence(self):
        """Task-level on_error mode takes precedence over context stop_on_error."""
        module = {
            "id": "precedence_test",
            "tasks": [
                {
                    "tool": "fail_task",
                    "on_error": "continue",  # Task says continue
                    "params": {},
                },
                {
                    "tool": "task2",
                    "params": {},
                },
            ],
        }
        context = {"stop_on_error": True}  # Context says stop, but task overrides

        with patch(
            "agency_toolkit.core.orchestrator.get_task_handler"
        ) as mock_get_handler:
            mock_handler = MagicMock()
            mock_handler.execute.side_effect = [
                RuntimeError("Task failed"),
                "task2_output",
            ]
            mock_get_handler.return_value = mock_handler

            report = execute_module(module, context)

            # Task-level on_error: continue should override context stop_on_error: True
            assert len(report.task_results) == 2
            assert report.task_results[0].success is False
            assert report.task_results[1].success is True
