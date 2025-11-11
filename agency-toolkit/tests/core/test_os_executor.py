"""Comprehensive tests for the Workflow Executor (os_executor).

Tests cover workflow loading, validation, and end-to-end execution.
"""

from unittest.mock import patch

import pytest

from agency_toolkit.core.orchestrator import TaskResult, WorkflowExecutionReport
from agency_toolkit.core.os_executor import (
    build_execution_context,
    build_execution_summary,
    execute_project_workflow,
    execute_workflow_modules,
    find_archetype,
    find_module,
    find_solution,
)


class TestFindArchetype:
    """Test archetype lookup."""

    def test_find_valid_archetype(self):
        """Find archetype by valid ID."""
        with patch("agency_toolkit.core.os_executor.load_archetypes") as mock_load:
            mock_load.return_value = [
                {"id": "A1", "name": "Archetype 1", "pains": ["pain1"]},
                {"id": "A2", "name": "Archetype 2", "goals": ["goal1"]},
            ]

            result = find_archetype("A1")

            assert result["id"] == "A1"
            assert result["name"] == "Archetype 1"

    def test_find_nonexistent_archetype_raises_error(self):
        """Raise ValueError for invalid archetype ID."""
        with patch("agency_toolkit.core.os_executor.load_archetypes") as mock_load:
            mock_load.return_value = [
                {"id": "A1", "name": "Archetype 1"},
                {"id": "A2", "name": "Archetype 2"},
            ]

            with pytest.raises(ValueError, match="Invalid archetype_id"):
                find_archetype("INVALID")


class TestFindSolution:
    """Test solution lookup."""

    def test_find_valid_solution(self):
        """Find solution by valid ID."""
        with patch("agency_toolkit.core.os_executor.load_solutions") as mock_load:
            mock_load.return_value = [
                {"id": "S1", "name": "Solution 1", "archetype_id": "A1"},
                {"id": "S2", "name": "Solution 2", "archetype_id": "A2"},
            ]

            result = find_solution("S1")

            assert result["id"] == "S1"
            assert result["archetype_id"] == "A1"

    def test_find_solution_nonexistent_raises_error(self):
        """Raise ValueError for invalid solution ID."""
        with patch("agency_toolkit.core.os_executor.load_solutions") as mock_load:
            mock_load.return_value = [
                {"id": "S1", "name": "Solution 1", "archetype_id": "A1"},
            ]

            with pytest.raises(ValueError, match="Invalid solution_id"):
                find_solution("INVALID")

    def test_find_solution_validates_archetype_match(self):
        """Verify solution belongs to correct archetype."""
        with patch("agency_toolkit.core.os_executor.load_solutions") as mock_load:
            mock_load.return_value = [
                {"id": "S1", "name": "Solution 1", "archetype_id": "A1"},
            ]

            # Correct archetype should pass
            result = find_solution("S1", archetype_id="A1")
            assert result["id"] == "S1"

            # Incorrect archetype should raise error
            with pytest.raises(ValueError, match="does not belong to archetype"):
                find_solution("S1", archetype_id="A_WRONG")


class TestFindModule:
    """Test module lookup."""

    def test_find_valid_module(self):
        """Find module by valid ID within solution."""
        solution = {
            "id": "S1",
            "modules": [
                {"id": "M1", "tasks": []},
                {"id": "M2", "tasks": []},
            ],
        }

        result = find_module("M1", solution)

        assert result["id"] == "M1"

    def test_find_nonexistent_module_raises_error(self):
        """Raise ValueError for invalid module ID."""
        solution = {
            "id": "S1",
            "modules": [
                {"id": "M1", "tasks": []},
            ],
        }

        with pytest.raises(ValueError, match="Invalid module_id"):
            find_module("INVALID", solution)


class TestBuildExecutionContext:
    """Test execution context building."""

    def test_build_context_with_required_fields(self):
        """Build context with required fields."""
        archetype = {
            "id": "A1",
            "name": "Archetype 1",
            "pains": ["pain1", "pain2"],
            "goals": ["goal1"],
        }
        solution = {
            "id": "S1",
            "name": "Solution 1",
        }

        context = build_execution_context("MyProject", archetype, solution)

        assert context["project_name"] == "MyProject"
        assert context["archetype_id"] == "A1"
        assert context["archetype_name"] == "Archetype 1"
        assert context["solution_id"] == "S1"
        assert context["pain_points"] == ["pain1", "pain2"]
        assert context["goals"] == ["goal1"]

    def test_build_context_with_optional_fields(self):
        """Build context with optional fields."""
        archetype = {"id": "A1", "name": "Archetype 1"}
        solution = {"id": "S1", "name": "Solution 1"}

        context = build_execution_context(
            "MyProject",
            archetype,
            solution,
            ai_provider="mistral",
            stop_on_error=False,
        )

        assert context["ai_provider"] == "mistral"
        assert context["stop_on_error"] is False

    def test_project_name_safe_sanitization(self):
        """Verify project_name_safe replaces underscores with spaces."""
        archetype = {"id": "A1", "name": "Archetype 1"}
        solution = {"id": "S1", "name": "Solution 1"}

        context = build_execution_context("My_Project_Name", archetype, solution)

        assert context["project_name"] == "My_Project_Name"
        assert context["project_name_safe"] == "My Project Name"


class TestExecuteWorkflowModules:
    """Test module execution."""

    def test_execute_single_module(self):
        """Execute single module successfully."""
        modules = [
            {
                "id": "M1",
                "tasks": [
                    {"tool": "task1", "params": {}},
                ],
            },
        ]
        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.os_executor.execute_module") as mock_exec:
            task_results = [
                TaskResult(tool="task1", success=True, output="result1", error=""),
            ]
            mock_exec.return_value = WorkflowExecutionReport(
                module_id="M1",
                total_tasks=1,
                successful=1,
                failed=0,
                skipped=0,
                errors=[],
                task_results=task_results,
            )

            results = execute_workflow_modules(modules, context)

            assert len(results) == 1
            assert results[0].success is True

    def test_execute_multiple_modules(self):
        """Execute multiple modules in sequence."""
        modules = [
            {"id": "M1", "tasks": []},
            {"id": "M2", "tasks": []},
            {"id": "M3", "tasks": []},
        ]
        context = {}

        with patch("agency_toolkit.core.os_executor.execute_module") as mock_exec:
            mock_exec.side_effect = [
                WorkflowExecutionReport(
                    "M1",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t1", success=True, output="r1", error="")],
                ),
                WorkflowExecutionReport(
                    "M2",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t2", success=True, output="r2", error="")],
                ),
                WorkflowExecutionReport(
                    "M3",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t3", success=True, output="r3", error="")],
                ),
            ]

            results = execute_workflow_modules(modules, context)

            assert len(results) == 3
            assert mock_exec.call_count == 3

    def test_stop_on_error_false_continues_after_failure(self):
        """With stop_on_error=False, all modules execute even if one fails."""
        modules = [
            {"id": "M1", "tasks": []},
            {"id": "M2", "tasks": []},
            {"id": "M3", "tasks": []},
        ]
        context = {"stop_on_error": False}

        with patch("agency_toolkit.core.os_executor.execute_module") as mock_exec:
            mock_exec.side_effect = [
                WorkflowExecutionReport(
                    "M1",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t1", success=True, output="r1", error="")],
                ),
                WorkflowExecutionReport(
                    "M2",
                    1,
                    0,
                    1,
                    0,
                    ["Failed"],
                    [TaskResult(tool="t2", success=False, output=None, error="Failed")],
                ),
                WorkflowExecutionReport(
                    "M3",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t3", success=True, output="r3", error="")],
                ),
            ]

            results = execute_workflow_modules(modules, context)

            assert len(results) == 3
            assert mock_exec.call_count == 3

    def test_stop_on_error_true_stops_after_failure(self):
        """With stop_on_error=True, execution stops after first module failure."""
        modules = [
            {"id": "M1", "tasks": []},
            {"id": "M2", "tasks": []},
            {"id": "M3", "tasks": []},
        ]
        context = {"stop_on_error": True}

        with patch("agency_toolkit.core.os_executor.execute_module") as mock_exec:
            mock_exec.side_effect = [
                WorkflowExecutionReport(
                    "M1",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t1", success=True, output="r1", error="")],
                ),
                WorkflowExecutionReport(
                    "M2",
                    1,
                    0,
                    1,
                    0,
                    ["Failed"],
                    [TaskResult(tool="t2", success=False, output=None, error="Failed")],
                ),
                WorkflowExecutionReport(
                    "M3",
                    1,
                    1,
                    0,
                    0,
                    [],
                    [TaskResult(tool="t3", success=True, output="r3", error="")],
                ),
            ]

            results = execute_workflow_modules(modules, context)

            # Only 2 modules should execute
            assert len(results) == 2
            assert mock_exec.call_count == 2


class TestBuildExecutionSummary:
    """Test execution summary building."""

    def test_build_summary_all_success(self):
        """Build summary when all tasks succeed."""
        modules = [{"id": "M1"}]
        results = [
            TaskResult(tool="t1", success=True, output="r1", error=""),
            TaskResult(tool="t2", success=True, output="r2", error=""),
            TaskResult(tool="t3", success=True, output="r3", error=""),
        ]

        summary = build_execution_summary(
            "MyProject",
            "A1",
            "S1",
            "M1",
            modules,
            results,
        )

        assert summary["project_name"] == "MyProject"
        assert summary["tasks_total"] == 3
        assert summary["tasks_success"] == 3
        assert summary["tasks_failed"] == 0
        assert summary["success"] is True

    def test_build_summary_with_failures(self):
        """Build summary when some tasks fail."""
        modules = [{"id": "M1"}]
        results = [
            TaskResult(tool="t1", success=True, output="r1", error=""),
            TaskResult(tool="t2", success=False, output=None, error="Failed"),
            TaskResult(tool="t3", success=True, output="r3", error=""),
        ]

        summary = build_execution_summary(
            "MyProject",
            "A1",
            "S1",
            "M1",
            modules,
            results,
        )

        assert summary["tasks_total"] == 3
        assert summary["tasks_success"] == 2
        assert summary["tasks_failed"] == 1
        assert summary["success"] is False

    def test_build_summary_modules_executed(self):
        """Verify modules_executed count."""
        modules = [{"id": "M1"}, {"id": "M2"}, {"id": "M3"}]
        results = [TaskResult(tool="t1", success=True, output="r1", error="")]

        summary = build_execution_summary(
            "MyProject",
            "A1",
            "S1",
            "M1",
            modules,
            results,
        )

        assert summary["modules_executed"] == 3


class TestExecuteProjectWorkflow:
    """Integration tests for complete workflow execution."""

    def test_execute_complete_workflow_successfully(self):
        """Execute complete workflow end-to-end."""
        with patch("agency_toolkit.core.os_executor.find_archetype") as mock_find_arch:
            with patch(
                "agency_toolkit.core.os_executor.find_solution"
            ) as mock_find_sol:
                with patch(
                    "agency_toolkit.core.os_executor.find_module"
                ) as mock_find_mod:
                    with patch(
                        "agency_toolkit.core.os_executor.resolve_module_dependencies"
                    ) as mock_resolve:
                        with patch(
                            "agency_toolkit.core.os_executor.execute_workflow_modules"
                        ) as mock_exec:
                            mock_find_arch.return_value = {
                                "id": "A1",
                                "name": "Archetype 1",
                                "pains": [],
                                "goals": [],
                            }
                            mock_find_sol.return_value = {
                                "id": "S1",
                                "name": "Solution 1",
                                "archetype_id": "A1",
                            }
                            mock_find_mod.return_value = {"id": "M1", "tasks": []}
                            mock_resolve.return_value = [{"id": "M1", "tasks": []}]
                            # execute_workflow_modules returns a list of TaskResults
                            mock_exec.return_value = [
                                TaskResult(
                                    tool="t1", success=True, output="result", error=""
                                )
                            ]

                            result = execute_project_workflow(
                                "MyProject",
                                "A1",
                                "S1",
                                "M1",
                            )

                            assert result["success"] is True
                            assert result["project_name"] == "MyProject"
                            assert result["tasks_success"] == 1

    def test_execute_invalid_archetype_raises_error(self):
        """Raise error for invalid archetype."""
        with patch("agency_toolkit.core.os_executor.find_archetype") as mock_find_arch:
            mock_find_arch.side_effect = ValueError("Invalid archetype")

            with pytest.raises(ValueError):
                execute_project_workflow("MyProject", "INVALID", "S1", "M1")

    def test_execute_invalid_solution_raises_error(self):
        """Raise error for invalid solution."""
        with patch("agency_toolkit.core.os_executor.find_archetype") as mock_find_arch:
            with patch(
                "agency_toolkit.core.os_executor.find_solution"
            ) as mock_find_sol:
                mock_find_arch.return_value = {"id": "A1", "name": "A1"}
                mock_find_sol.side_effect = ValueError("Invalid solution")

                with pytest.raises(ValueError):
                    execute_project_workflow("MyProject", "A1", "INVALID", "M1")

    def test_execute_invalid_module_raises_error(self):
        """Raise error for invalid module."""
        with patch("agency_toolkit.core.os_executor.find_archetype") as mock_find_arch:
            with patch(
                "agency_toolkit.core.os_executor.find_solution"
            ) as mock_find_sol:
                with patch(
                    "agency_toolkit.core.os_executor.find_module"
                ) as mock_find_mod:
                    mock_find_arch.return_value = {"id": "A1", "name": "A1"}
                    mock_find_sol.return_value = {"id": "S1", "archetype_id": "A1"}
                    mock_find_mod.side_effect = ValueError("Invalid module")

                    with pytest.raises(ValueError):
                        execute_project_workflow("MyProject", "A1", "S1", "INVALID")
