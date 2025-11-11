"""Integration tests for GRAND AGENCY OS (Epic 10)."""

from agency_toolkit.core.orchestrator import TaskResult, execute_module
from agency_toolkit.core.workflow_loader import (
    load_archetypes,
    load_solutions,
    validate_registry,
)


class TestGrandAgencyRegistry:
    """Test suite for GRAND AGENCY registry loading and validation."""

    def test_load_archetypes_returns_list(self):
        """Test that archetypes can be loaded successfully."""
        archetypes = load_archetypes()
        assert isinstance(archetypes, list)
        assert len(archetypes) > 0

    def test_archetypes_have_required_fields(self):
        """Test that all archetypes have required fields."""
        archetypes = load_archetypes()
        required_fields = ["id", "name", "description", "pains", "goals"]

        for archetype in archetypes:
            for field in required_fields:
                assert field in archetype, f"Missing field '{field}' in archetype"

    def test_load_solutions_returns_list(self):
        """Test that solutions can be loaded successfully."""
        solutions = load_solutions()
        assert isinstance(solutions, list)
        assert len(solutions) > 0

    def test_solutions_have_required_fields(self):
        """Test that all solutions have required fields."""
        solutions = load_solutions()
        required_fields = ["id", "name", "archetype_id", "modules"]

        for solution in solutions:
            for field in required_fields:
                assert field in solution, f"Missing field '{field}' in solution"

    def test_solution_modules_have_required_fields(self):
        """Test that all modules have required fields."""
        solutions = load_solutions()
        required_fields = ["id", "title", "description", "tasks", "dependencies"]

        for solution in solutions:
            for module in solution.get("modules", []):
                for field in required_fields:
                    assert field in module, f"Missing field '{field}' in module"

    def test_validate_registry_passes(self):
        """Test that registry validation passes."""
        # Should not raise any exception
        validate_registry()

    def test_all_archetype_solution_references_are_valid(self):
        """Test that archetypes reference existing solutions."""
        archetypes = load_archetypes()
        solutions = load_solutions()
        solution_ids = {sol["id"] for sol in solutions}

        for archetype in archetypes:
            for sol_id in archetype.get("solution_template_ids", []):
                assert (
                    sol_id in solution_ids
                ), f"Archetype {archetype['id']} references non-existent solution {sol_id}"

    def test_all_solution_archetype_references_are_valid(self):
        """Test that solutions reference existing archetypes."""
        archetypes = load_archetypes()
        solutions = load_solutions()
        archetype_ids = {arch["id"] for arch in archetypes}

        for solution in solutions:
            arch_id = solution.get("archetype_id")
            assert (
                arch_id in archetype_ids
            ), f"Solution {solution['id']} references non-existent archetype {arch_id}"


class TestOrchestrator:
    """Test suite for the orchestrator execution engine."""

    def test_execute_module_returns_task_results(self):
        """Test that module execution returns a WorkflowExecutionReport with TaskResult objects."""
        module = {
            "id": "TEST_M1",
            "title": "Test Module",
            "tasks": [
                {"tool": "test_tool_1", "params": {}},
                {"tool": "test_tool_2", "params": {}},
            ],
        }
        context = {"project_name": "Test Project"}

        report = execute_module(module, context)

        assert report.module_id == "TEST_M1"
        assert len(report.task_results) == 2
        assert all(isinstance(r, TaskResult) for r in report.task_results)

    def test_execute_module_with_empty_tasks(self):
        """Test that module with no tasks returns empty results."""
        module = {"id": "EMPTY_M1", "title": "Empty Module", "tasks": []}
        context = {}

        report = execute_module(module, context)

        assert report.module_id == "EMPTY_M1"
        assert len(report.task_results) == 0
        assert report.total_tasks == 0

    def test_task_result_has_correct_structure(self):
        """Test that TaskResult has all required fields."""
        module = {
            "id": "TEST_M1",
            "title": "Test Module",
            "tasks": [{"tool": "test_tool", "params": {}}],
        }
        context = {}

        report = execute_module(module, context)
        result = report.task_results[0]

        assert hasattr(result, "tool")
        assert hasattr(result, "success")
        assert hasattr(result, "output")
        assert hasattr(result, "error")

    def test_execute_module_real_structure_task(self, tmp_path):
        """Test that structure task creates actual project folders."""
        module = {
            "id": "TEST_M1",
            "title": "Test Structure Module",
            "tasks": [
                {
                    "tool": "structure",
                    "params": {
                        "structure_type": "web",
                        "base_path": str(tmp_path),
                        "dry_run": False,
                    },
                }
            ],
        }
        context = {
            "project_name": "TestProject",
            "archetype_name": "TestClient",
            "stop_on_error": True,
        }

        report = execute_module(module, context)

        # Verify task succeeded
        assert len(report.task_results) == 1
        assert report.task_results[0].success
        assert report.task_results[0].tool == "structure"
        assert report.task_results[0].error == ""
        assert report.successful == 1
        assert report.failed == 0

        # Verify actual folders were created
        expected_path = tmp_path / "testclient" / "testproject"
        assert expected_path.exists(), "Project structure was not created"

    def test_execute_module_real_briefing_task(self, tmp_path):
        """Test that briefing task creates actual PDF file."""
        module = {
            "id": "TEST_M2",
            "title": "Test Briefing Module",
            "tasks": [
                {
                    "tool": "briefing",
                    "params": {
                        "format_type": "pdf",
                        "output_dir": str(tmp_path / "briefings"),
                        "deliverables": ["Website", "Logo"],
                        "deadline": "2024-12-31",
                        "budget": "10000",
                    },
                }
            ],
        }
        context = {
            "project_name": "TestProject",
            "archetype_name": "TestClient",
            "solution_name": "Web Development",
            "goals": ["Increase online presence"],
            "stop_on_error": True,
        }

        report = execute_module(module, context)

        # Verify task succeeded
        assert len(report.task_results) == 1
        assert report.task_results[0].success
        assert report.task_results[0].tool == "briefing"
        assert report.successful == 1

        # Verify PDF was created
        briefing_dir = tmp_path / "briefings"
        assert briefing_dir.exists()
        pdf_files = list(briefing_dir.glob("*.pdf"))
        assert len(pdf_files) > 0, "No PDF briefing was created"

    def test_execute_module_real_social_task(self, tmp_path):
        """Test that social task creates actual image file."""
        module = {
            "id": "TEST_M3",
            "title": "Test Social Module",
            "tasks": [
                {
                    "tool": "social",
                    "params": {
                        "text": "Test social post",
                        "style": "modern",
                        "color": "blue",
                        "format": "square",
                        "output_dir": str(tmp_path / "social"),
                        "dry_run": False,
                    },
                }
            ],
        }
        context = {
            "project_name": "TestProject",
            "stop_on_error": True,
        }

        report = execute_module(module, context)

        # Verify task succeeded
        assert len(report.task_results) == 1
        assert report.task_results[0].success
        assert report.task_results[0].tool == "social"
        assert report.successful == 1

        # Verify image was created
        social_dir = tmp_path / "social"
        assert social_dir.exists()
        image_files = list(social_dir.glob("*.png"))
        assert len(image_files) > 0, "No social media image was created"

    def test_execute_module_error_handling_with_invalid_tool(self):
        """Test that unknown tool names are handled gracefully."""
        module = {
            "id": "TEST_M4",
            "title": "Test Error Module",
            "tasks": [
                {"tool": "nonexistent_tool", "params": {}},
            ],
        }
        context = {"stop_on_error": False}

        report = execute_module(module, context)

        # Verify task failed gracefully
        assert len(report.task_results) == 1
        assert not report.task_results[0].success
        assert "Unknown task handler" in report.task_results[0].error
        assert report.failed == 1
        assert report.successful == 0

    def test_execute_module_stop_on_error_behavior(self):
        """Test that stop_on_error halts execution after first failure."""
        module = {
            "id": "TEST_M5",
            "title": "Test Stop on Error",
            "tasks": [
                {"tool": "invalid_tool_1", "params": {}},
                {"tool": "invalid_tool_2", "params": {}},
                {"tool": "invalid_tool_3", "params": {}},
            ],
        }
        context = {"stop_on_error": True}

        report = execute_module(module, context)

        # Should only execute first task, then stop
        assert len(report.task_results) == 1
        assert not report.task_results[0].success
        assert report.failed == 1
        assert report.skipped == 2

    def test_execute_module_continue_on_error_behavior(self):
        """Test that execution continues when stop_on_error is False."""
        module = {
            "id": "TEST_M6",
            "title": "Test Continue on Error",
            "tasks": [
                {"tool": "invalid_tool_1", "params": {}},
                {"tool": "invalid_tool_2", "params": {}},
                {"tool": "invalid_tool_3", "params": {}},
            ],
        }
        context = {"stop_on_error": False}

        report = execute_module(module, context)

        # Should execute all tasks despite failures
        assert len(report.task_results) == 3
        assert all(not r.success for r in report.task_results)
        assert report.failed == 3
        assert report.successful == 0

    def test_dependency_resolution_executes_in_order(self, tmp_path):
        """Test that modules with dependencies execute in correct order."""
        from agency_toolkit.core.dependency_resolver import resolve_module_dependencies

        # Create solution with dependencies
        solution = {
            "id": "TEST_SOL",
            "modules": [
                {
                    "id": "BASE",
                    "title": "Base Module",
                    "dependencies": [],
                    "tasks": [
                        {
                            "tool": "structure",
                            "params": {
                                "structure_type": "web",
                                "base_path": str(tmp_path),
                            },
                        }
                    ],
                },
                {
                    "id": "DEPENDENT",
                    "title": "Dependent Module",
                    "dependencies": ["BASE"],
                    "tasks": [
                        {
                            "tool": "social",
                            "params": {
                                "text": "Test post",
                                "output_dir": str(tmp_path / "social"),
                            },
                        }
                    ],
                },
            ],
        }

        # Resolve dependencies for DEPENDENT module
        modules_to_execute = resolve_module_dependencies(
            solution["modules"][1], solution
        )

        # Should return both modules in order
        assert len(modules_to_execute) == 2
        assert modules_to_execute[0]["id"] == "BASE"
        assert modules_to_execute[1]["id"] == "DEPENDENT"

        # Execute all modules
        context = {
            "project_name": "TestProject",
            "archetype_name": "TestClient",
            "stop_on_error": True,
        }

        all_results = []
        for module in modules_to_execute:
            report = execute_module(module, context)
            all_results.extend(report.task_results)

        # Verify all tasks succeeded
        assert len(all_results) == 2
        assert all(r.success for r in all_results)

        # Verify files were created in order
        assert (tmp_path / "testclient" / "testproject").exists()
        assert (tmp_path / "social").exists()

    def test_execute_module_placeholder_tasks_succeed(self):
        """Test that placeholder tasks execute successfully (Phase 1)."""
        module = {
            "id": "TEST_M1",
            "title": "Test Module",
            "tasks": [
                {"tool": "create_briefing"},
                {"tool": "generate_content"},
            ],
        }
        context = {"stop_on_error": False}

        report = execute_module(module, context)

        # Unknown tools should fail (no longer placeholders)
        assert all(not r.success for r in report.task_results)
        assert report.failed == 2


class TestRegistryDataIntegrity:
    """Test suite for registry data quality and consistency."""

    def test_all_archetypes_have_unique_ids(self):
        """Test that all archetype IDs are unique."""
        archetypes = load_archetypes()
        ids = [arch["id"] for arch in archetypes]
        assert len(ids) == len(set(ids)), "Duplicate archetype IDs found"

    def test_all_solutions_have_unique_ids(self):
        """Test that all solution IDs are unique."""
        solutions = load_solutions()
        ids = [sol["id"] for sol in solutions]
        assert len(ids) == len(set(ids)), "Duplicate solution IDs found"

    def test_all_modules_have_unique_ids(self):
        """Test that all module IDs are unique across all solutions."""
        solutions = load_solutions()
        module_ids = [mod["id"] for sol in solutions for mod in sol.get("modules", [])]
        assert len(module_ids) == len(set(module_ids)), "Duplicate module IDs found"

    def test_expected_archetypes_exist(self):
        """Test that the expected 6 archetypes exist."""
        archetypes = load_archetypes()
        expected_ids = ["I", "II", "III", "IV", "V", "VI"]

        archetype_ids = [arch["id"] for arch in archetypes]
        for expected_id in expected_ids:
            assert (
                expected_id in archetype_ids
            ), f"Expected archetype {expected_id} not found"

    def test_expected_solutions_exist(self):
        """Test that the expected solution templates exist."""
        solutions = load_solutions()
        expected_ids = ["A1", "A2", "B1", "C1", "C2", "D1"]

        solution_ids = [sol["id"] for sol in solutions]
        for expected_id in expected_ids:
            assert (
                expected_id in solution_ids
            ), f"Expected solution {expected_id} not found"
