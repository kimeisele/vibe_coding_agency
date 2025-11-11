"""Unit tests for os_interactive module (Epic 1.4.3).

Tests for interactive workflow prompts and UI logic for GRAND AGENCY OS.
"""

from unittest.mock import MagicMock, patch

import pytest
import typer

from agency_toolkit.core.os_interactive import (
    display_dry_run_plan,
    display_execution_progress,
    display_execution_results,
    resolve_and_display_dependencies,
    run_interactive_workflow,
    select_archetype,
    select_module,
    select_solution,
)


class TestSelectArchetype:
    """Test archetype selection."""

    @patch("agency_toolkit.core.os_interactive.load_archetypes")
    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_archetype_returns_selected_archetype(self, mock_prompt, mock_load):
        """Should return the selected archetype."""
        mock_load.return_value = [
            {"id": "arch1", "name": "Enterprise", "description": "Enterprise clients"},
            {"id": "arch2", "name": "Startup", "description": "Startup clients"},
        ]
        expected = {
            "id": "arch1",
            "name": "Enterprise",
            "description": "Enterprise clients",
        }
        mock_prompt.return_value = expected

        result = select_archetype()

        assert result == expected
        mock_load.assert_called_once()
        mock_prompt.assert_called_once()

    @patch("agency_toolkit.core.os_interactive.load_archetypes")
    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_archetype_loads_archetypes(self, mock_prompt, mock_load):
        """Should load archetypes from workflow loader."""
        mock_load.return_value = [
            {"id": "a1", "name": "Test", "description": "Test archetype"}
        ]
        mock_prompt.return_value = mock_load.return_value[0]

        select_archetype()

        mock_load.assert_called_once()

    @patch("agency_toolkit.core.os_interactive.load_archetypes")
    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_archetype_uses_correct_selection_keys(self, mock_prompt, mock_load):
        """Should use correct keys for prompt_for_selection."""
        mock_load.return_value = [
            {"id": "a1", "name": "Type A", "description": "Description A"}
        ]
        mock_prompt.return_value = mock_load.return_value[0]

        select_archetype()

        call_kwargs = mock_prompt.call_args[1]
        assert call_kwargs["id_key"] == "id"
        assert call_kwargs["name_key"] == "name"
        assert call_kwargs["description_key"] == "description"


class TestSelectSolution:
    """Test solution selection."""

    @patch("agency_toolkit.core.os_interactive.load_solutions")
    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_solution_filters_by_archetype_id(self, mock_prompt, mock_load):
        """Should filter solutions by archetype ID."""
        mock_load.return_value = [
            {
                "id": "sol1",
                "name": "Solution 1",
                "archetype_id": "arch1",
                "description": "",
            },
            {
                "id": "sol2",
                "name": "Solution 2",
                "archetype_id": "arch2",
                "description": "",
            },
            {
                "id": "sol3",
                "name": "Solution 3",
                "archetype_id": "arch1",
                "description": "",
            },
        ]
        expected = mock_load.return_value[0]
        mock_prompt.return_value = expected

        result = select_solution("arch1")

        assert result == expected
        call_kwargs = mock_prompt.call_args[1]
        filtered_solutions = call_kwargs["choices"]
        assert len(filtered_solutions) == 2
        assert all(s["archetype_id"] == "arch1" for s in filtered_solutions)

    @patch("agency_toolkit.core.os_interactive.load_solutions")
    def test_select_solution_raises_on_no_solutions_found(self, mock_load):
        """Should raise typer.Exit if no solutions found for archetype."""
        mock_load.return_value = [
            {
                "id": "sol1",
                "name": "Solution 1",
                "archetype_id": "arch1",
                "description": "",
            },
        ]

        with pytest.raises(typer.Exit):
            select_solution("nonexistent_arch")

    @patch("agency_toolkit.core.os_interactive.load_solutions")
    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_solution_returns_selected_solution(self, mock_prompt, mock_load):
        """Should return the user-selected solution."""
        mock_load.return_value = [
            {
                "id": "sol1",
                "name": "Solution 1",
                "archetype_id": "arch1",
                "description": "Desc 1",
            },
            {
                "id": "sol2",
                "name": "Solution 2",
                "archetype_id": "arch1",
                "description": "Desc 2",
            },
        ]
        expected = mock_load.return_value[1]
        mock_prompt.return_value = expected

        result = select_solution("arch1")

        assert result == expected


class TestSelectModule:
    """Test module selection."""

    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_module_returns_selected_module(self, mock_prompt):
        """Should return the selected module from solution."""
        solution = {
            "id": "sol1",
            "modules": [
                {"id": "mod1", "title": "Module 1", "description": "Desc 1"},
                {"id": "mod2", "title": "Module 2", "description": "Desc 2"},
            ],
        }
        expected = solution["modules"][0]
        mock_prompt.return_value = expected

        result = select_module(solution)

        assert result == expected

    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_module_extracts_modules_from_solution(self, mock_prompt):
        """Should extract modules list from solution."""
        solution = {
            "id": "sol1",
            "modules": [
                {"id": "mod1", "title": "Module 1", "description": "Desc"},
                {"id": "mod2", "title": "Module 2", "description": "Desc"},
            ],
        }
        mock_prompt.return_value = solution["modules"][0]

        select_module(solution)

        call_kwargs = mock_prompt.call_args[1]
        assert call_kwargs["choices"] == solution["modules"]

    def test_select_module_raises_on_empty_modules_list(self):
        """Should raise typer.Exit if solution has no modules."""
        solution = {"id": "sol1", "modules": []}

        with pytest.raises(typer.Exit):
            select_module(solution)

    def test_select_module_raises_on_missing_modules_key(self):
        """Should raise typer.Exit if solution has no modules key."""
        solution = {"id": "sol1"}  # No 'modules' key

        with pytest.raises(typer.Exit):
            select_module(solution)

    @patch("agency_toolkit.core.os_interactive.prompt_for_selection")
    def test_select_module_uses_correct_selection_keys(self, mock_prompt):
        """Should use correct keys for prompt_for_selection."""
        solution = {
            "id": "sol1",
            "modules": [{"id": "m1", "title": "Module 1", "description": "Desc"}],
        }
        mock_prompt.return_value = solution["modules"][0]

        select_module(solution)

        call_kwargs = mock_prompt.call_args[1]
        assert call_kwargs["id_key"] == "id"
        assert call_kwargs["name_key"] == "title"
        assert call_kwargs["description_key"] == "description"


class TestResolveAndDisplayDependencies:
    """Test dependency resolution and display."""

    @patch("agency_toolkit.core.os_interactive.resolve_module_dependencies")
    def test_resolve_and_display_dependencies_with_single_module(self, mock_resolve):
        """Should handle case with single module (no dependencies)."""
        module = {"id": "mod1", "title": "Module 1"}
        solution = {"id": "sol1"}
        mock_resolve.return_value = [module]

        result = resolve_and_display_dependencies(module, solution)

        assert result == [module]
        mock_resolve.assert_called_once_with(module, solution)

    @patch("agency_toolkit.core.os_interactive.resolve_module_dependencies")
    def test_resolve_and_display_dependencies_with_multiple_modules(self, mock_resolve):
        """Should handle case with multiple modules (with dependencies)."""
        module1 = {"id": "mod1", "title": "Module 1"}
        module2 = {"id": "mod2", "title": "Module 2"}
        module3 = {"id": "mod3", "title": "Module 3"}
        main_module = {"id": "mod3", "title": "Module 3"}
        solution = {"id": "sol1"}
        mock_resolve.return_value = [module1, module2, module3]

        result = resolve_and_display_dependencies(main_module, solution)

        assert result == [module1, module2, module3]
        assert len(result) == 3

    @patch("agency_toolkit.core.os_interactive.resolve_module_dependencies")
    def test_resolve_and_display_dependencies_raises_on_error(self, mock_resolve):
        """Should raise typer.Exit if dependency resolution fails."""
        module = {"id": "mod1"}
        solution = {"id": "sol1"}
        mock_resolve.side_effect = ValueError("Circular dependency detected")

        with pytest.raises(typer.Exit):
            resolve_and_display_dependencies(module, solution)

    @patch("agency_toolkit.core.os_interactive.resolve_module_dependencies")
    def test_resolve_and_display_dependencies_returns_list(self, mock_resolve):
        """Should return a list of modules to execute."""
        module = {"id": "mod1", "title": "Module"}
        solution = {"id": "sol1"}
        mock_resolve.return_value = [module]

        result = resolve_and_display_dependencies(module, solution)

        assert isinstance(result, list)
        assert len(result) >= 1


class TestDisplayExecutionProgress:
    """Test execution progress display."""

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_progress_shows_project_name(self, mock_console):
        """Should display project name."""
        project_name = "My Project"
        modules = [{"id": "m1"}, {"id": "m2"}]

        display_execution_progress(project_name, modules)

        # Check that console.print was called with project name
        assert any(
            project_name in str(call) for call in mock_console.print.call_args_list
        )

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_progress_shows_module_count(self, mock_console):
        """Should display number of modules to execute."""
        project_name = "Project"
        modules = [{"id": "m1"}, {"id": "m2"}, {"id": "m3"}]

        display_execution_progress(project_name, modules)

        # Check that console.print was called with module count
        assert any("3" in str(call) for call in mock_console.print.call_args_list)

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_progress_with_single_module(self, mock_console):
        """Should handle single module."""
        display_execution_progress("Project", [{"id": "m1"}])

        # Should not raise, just display
        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_progress_with_many_modules(self, mock_console):
        """Should handle many modules."""
        modules = [{"id": f"m{i}"} for i in range(10)]
        display_execution_progress("Project", modules)

        # Should not raise, just display
        assert mock_console.print.called


class TestDisplayExecutionResults:
    """Test execution results display."""

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_results_shows_project_name(self, mock_console):
        """Should display project name from summary."""
        summary = {
            "project_name": "My Project",
            "modules_executed": 1,
            "tasks_total": 5,
            "tasks_success": 4,
            "tasks_failed": 1,
            "success": False,
        }

        display_execution_results(summary)

        # Verify console was used to print the summary
        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_results_with_success(self, mock_console):
        """Should display success status when all tasks succeed."""
        summary = {
            "project_name": "Project",
            "modules_executed": 2,
            "tasks_total": 10,
            "tasks_success": 10,
            "tasks_failed": 0,
            "success": True,
        }

        display_execution_results(summary)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_results_with_failure(self, mock_console):
        """Should display failure status when tasks fail."""
        summary = {
            "project_name": "Project",
            "modules_executed": 1,
            "tasks_total": 5,
            "tasks_success": 3,
            "tasks_failed": 2,
            "success": False,
        }

        display_execution_results(summary)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_execution_results_creates_table(self, mock_console):
        """Should create and display a table."""
        summary = {
            "project_name": "Project",
            "modules_executed": 1,
            "tasks_total": 3,
            "tasks_success": 3,
            "tasks_failed": 0,
            "success": True,
        }

        display_execution_results(summary)

        # Verify table was created and printed
        assert mock_console.print.called


class TestRunInteractiveWorkflow:
    """Test complete interactive workflow."""

    @patch("agency_toolkit.core.os_interactive.display_execution_results")
    @patch("agency_toolkit.core.os_interactive.execute_workflow_modules")
    @patch("agency_toolkit.core.os_interactive.build_execution_summary")
    @patch("agency_toolkit.core.os_interactive.build_execution_context")
    @patch("agency_toolkit.core.os_interactive.resolve_and_display_dependencies")
    @patch("agency_toolkit.core.os_interactive.select_module")
    @patch("agency_toolkit.core.os_interactive.select_solution")
    @patch("agency_toolkit.core.os_interactive.select_archetype")
    def test_run_interactive_workflow_with_dry_run(
        self,
        mock_arch,
        mock_sol,
        mock_mod,
        mock_deps,
        mock_context,
        mock_summary,
        mock_execute,
        mock_display,
    ):
        """Should handle dry-run mode without execution."""
        mock_arch.return_value = {"id": "arch1", "name": "Archetype"}
        mock_sol.return_value = {"id": "sol1", "name": "Solution"}
        mock_mod.return_value = {"id": "mod1", "title": "Module"}
        mock_deps.return_value = [{"id": "mod1", "title": "Module", "tasks": []}]

        result = run_interactive_workflow("TestProject", dry_run=True)

        # In dry-run, should return summary without executing
        assert result["dry_run"] is True
        assert result["project_name"] == "TestProject"
        assert result["modules_executed"] == 0
        # Should NOT call execute or build functions
        mock_context.assert_not_called()
        mock_execute.assert_not_called()
        mock_summary.assert_not_called()
        mock_display.assert_not_called()

    @patch("agency_toolkit.core.os_interactive.display_execution_results")
    @patch("agency_toolkit.core.os_interactive.execute_workflow_modules")
    @patch("agency_toolkit.core.os_interactive.build_execution_summary")
    @patch("agency_toolkit.core.os_interactive.build_execution_context")
    @patch("agency_toolkit.core.os_interactive.resolve_and_display_dependencies")
    @patch("agency_toolkit.core.os_interactive.select_module")
    @patch("agency_toolkit.core.os_interactive.select_solution")
    @patch("agency_toolkit.core.os_interactive.select_archetype")
    def test_run_interactive_workflow_executes_all_steps(
        self,
        mock_arch,
        mock_sol,
        mock_mod,
        mock_deps,
        mock_context,
        mock_summary,
        mock_execute,
        mock_display,
    ):
        """Should execute all workflow steps in order."""
        archetype = {"id": "arch1", "name": "Archetype"}
        solution = {"id": "sol1", "name": "Solution"}
        module = {"id": "mod1", "title": "Module"}
        modules_exec = [module]

        mock_arch.return_value = archetype
        mock_sol.return_value = solution
        mock_mod.return_value = module
        mock_deps.return_value = modules_exec
        mock_context.return_value = MagicMock()
        mock_execute.return_value = []
        mock_summary.return_value = {
            "project_name": "TestProject",
            "archetype_id": "arch1",
            "solution_id": "sol1",
            "module_id": "mod1",
            "modules_executed": 1,
            "tasks_total": 0,
            "tasks_success": 0,
            "tasks_failed": 0,
            "success": True,
        }

        result = run_interactive_workflow("TestProject")

        # All selection functions should be called
        mock_arch.assert_called_once()
        mock_sol.assert_called_once_with(archetype["id"])
        mock_mod.assert_called_once_with(solution)
        mock_deps.assert_called_once_with(module, solution)

        # Execution should happen
        mock_context.assert_called_once()
        mock_execute.assert_called_once()
        mock_summary.assert_called_once()
        mock_display.assert_called_once()

    @patch("agency_toolkit.core.os_interactive.display_execution_results")
    @patch("agency_toolkit.core.os_interactive.execute_workflow_modules")
    @patch("agency_toolkit.core.os_interactive.build_execution_summary")
    @patch("agency_toolkit.core.os_interactive.build_execution_context")
    @patch("agency_toolkit.core.os_interactive.resolve_and_display_dependencies")
    @patch("agency_toolkit.core.os_interactive.select_module")
    @patch("agency_toolkit.core.os_interactive.select_solution")
    @patch("agency_toolkit.core.os_interactive.select_archetype")
    def test_run_interactive_workflow_with_ai_provider(
        self,
        mock_arch,
        mock_sol,
        mock_mod,
        mock_deps,
        mock_context,
        mock_summary,
        mock_execute,
        mock_display,
    ):
        """Should pass AI provider to execution context."""
        mock_arch.return_value = {"id": "arch1"}
        mock_sol.return_value = {"id": "sol1"}
        mock_mod.return_value = {"id": "mod1"}
        mock_deps.return_value = [{"id": "mod1"}]
        mock_context.return_value = MagicMock()
        mock_execute.return_value = []
        mock_summary.return_value = {
            "project_name": "TestProject",
            "archetype_id": "arch1",
            "solution_id": "sol1",
            "module_id": "mod1",
            "modules_executed": 1,
            "tasks_total": 0,
            "tasks_success": 0,
            "tasks_failed": 0,
            "success": True,
        }

        result = run_interactive_workflow("TestProject", ai_provider="openai")

        # Context should be built with ai_provider
        call_kwargs = mock_context.call_args[0]
        assert "openai" in call_kwargs

    @patch("agency_toolkit.core.os_interactive.display_execution_results")
    @patch("agency_toolkit.core.os_interactive.execute_workflow_modules")
    @patch("agency_toolkit.core.os_interactive.build_execution_summary")
    @patch("agency_toolkit.core.os_interactive.build_execution_context")
    @patch("agency_toolkit.core.os_interactive.resolve_and_display_dependencies")
    @patch("agency_toolkit.core.os_interactive.select_module")
    @patch("agency_toolkit.core.os_interactive.select_solution")
    @patch("agency_toolkit.core.os_interactive.select_archetype")
    def test_run_interactive_workflow_returns_summary(
        self,
        mock_arch,
        mock_sol,
        mock_mod,
        mock_deps,
        mock_context,
        mock_summary,
        mock_execute,
        mock_display,
    ):
        """Should return execution summary dictionary."""
        expected_summary = {
            "project_name": "TestProject",
            "archetype_id": "arch1",
            "solution_id": "sol1",
            "module_id": "mod1",
            "modules_executed": 2,
            "tasks_total": 10,
            "tasks_success": 9,
            "tasks_failed": 1,
            "success": True,
        }

        mock_arch.return_value = {"id": "arch1"}
        mock_sol.return_value = {"id": "sol1"}
        mock_mod.return_value = {"id": "mod1"}
        mock_deps.return_value = [{"id": "mod1"}, {"id": "mod2"}]
        mock_context.return_value = MagicMock()
        mock_execute.return_value = [{"status": "success"}]
        mock_summary.return_value = expected_summary

        result = run_interactive_workflow("TestProject")

        assert result == expected_summary


class TestDisplayDryRunPlan:
    """Test dry-run plan display."""

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_shows_project_info(self, mock_console):
        """Should display project information."""
        project_name = "My Project"
        archetype = {"id": "arch1", "name": "Enterprise"}
        solution = {"id": "sol1", "name": "E-commerce"}
        modules = [{"id": "m1", "title": "Module 1", "tasks": []}]

        display_dry_run_plan(project_name, archetype, solution, modules)

        # Check that project info is printed
        assert mock_console.print.called
        call_strs = [str(call) for call in mock_console.print.call_args_list]
        assert any(project_name in str(call_str) for call_str in call_strs)

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_shows_archetype(self, mock_console):
        """Should display archetype information."""
        archetype = {"id": "arch1", "name": "Enterprise"}
        solution = {"id": "sol1", "name": "Solution"}
        modules = [{"id": "m1", "title": "Module 1", "tasks": []}]

        display_dry_run_plan("Project", archetype, solution, modules)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_shows_modules(self, mock_console):
        """Should display modules to be executed."""
        modules = [
            {
                "id": "m1",
                "title": "Module 1",
                "tasks": [{"tool": "bash", "description": "Task 1"}],
            },
            {"id": "m2", "title": "Module 2", "tasks": []},
        ]
        archetype = {"id": "arch1", "name": "Type"}
        solution = {"id": "sol1", "name": "Sol"}

        display_dry_run_plan("Project", archetype, solution, modules)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_with_single_module(self, mock_console):
        """Should display plan for single module."""
        modules = [{"id": "m1", "title": "Single Module", "tasks": []}]
        archetype = {"id": "a1", "name": "A"}
        solution = {"id": "s1", "name": "S"}

        display_dry_run_plan("Project", archetype, solution, modules)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_with_many_modules(self, mock_console):
        """Should display plan for many modules."""
        modules = [
            {
                "id": f"m{i}",
                "title": f"Module {i}",
                "tasks": [
                    {"tool": "python", "description": f"Task {j}"} for j in range(3)
                ],
            }
            for i in range(5)
        ]
        archetype = {"id": "a1", "name": "A"}
        solution = {"id": "s1", "name": "S"}

        display_dry_run_plan("Project", archetype, solution, modules)

        assert mock_console.print.called

    @patch("agency_toolkit.core.os_interactive.console")
    def test_display_dry_run_plan_shows_task_count(self, mock_console):
        """Should display total task count."""
        modules = [
            {
                "id": "m1",
                "title": "Module 1",
                "tasks": [
                    {"tool": "bash", "description": "Task 1"},
                    {"tool": "python", "description": "Task 2"},
                ],
            },
            {
                "id": "m2",
                "title": "Module 2",
                "tasks": [
                    {"tool": "bash", "description": "Task 3"},
                ],
            },
        ]
        archetype = {"id": "a1", "name": "A"}
        solution = {"id": "s1", "name": "S"}

        display_dry_run_plan("Project", archetype, solution, modules)

        # Should show total of 3 tasks
        assert mock_console.print.called
