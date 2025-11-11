"""Unit tests for dependency resolution."""

import pytest

from agency_toolkit.core.dependency_resolver import (
    CircularDependencyError,
    resolve_module_dependencies,
)


class TestDependencyResolver:
    """Test suite for module dependency resolution."""

    def test_single_module_no_dependencies(self):
        """Test resolution of module with no dependencies."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": []},
            ],
        }

        result = resolve_module_dependencies(solution["modules"][0], solution)

        assert len(result) == 1
        assert result[0]["id"] == "M1"

    def test_linear_dependency_chain(self):
        """Test resolution of linear dependency chain A <- B <- C."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": []},
                {"id": "M2", "title": "Module 2", "dependencies": ["M1"]},
                {"id": "M3", "title": "Module 3", "dependencies": ["M2"]},
            ],
        }

        result = resolve_module_dependencies(solution["modules"][2], solution)

        assert len(result) == 3
        assert [m["id"] for m in result] == ["M1", "M2", "M3"]

    def test_multiple_dependencies(self):
        """Test resolution with multiple dependencies (diamond pattern)."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": []},
                {"id": "M2", "title": "Module 2", "dependencies": ["M1"]},
                {"id": "M3", "title": "Module 3", "dependencies": ["M1"]},
                {"id": "M4", "title": "Module 4", "dependencies": ["M2", "M3"]},
            ],
        }

        result = resolve_module_dependencies(solution["modules"][3], solution)

        assert len(result) == 4
        assert result[0]["id"] == "M1"  # M1 must be first
        assert result[-1]["id"] == "M4"  # M4 must be last
        # M2 and M3 can be in any order, but both after M1
        middle_ids = {result[1]["id"], result[2]["id"]}
        assert middle_ids == {"M2", "M3"}

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": ["M2"]},
                {"id": "M2", "title": "Module 2", "dependencies": ["M1"]},
            ],
        }

        with pytest.raises(CircularDependencyError) as exc_info:
            resolve_module_dependencies(solution["modules"][0], solution)

        assert "Circular dependency" in str(exc_info.value)

    def test_self_circular_dependency(self):
        """Test that self-referencing modules are detected."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": ["M1"]},
            ],
        }

        with pytest.raises(CircularDependencyError):
            resolve_module_dependencies(solution["modules"][0], solution)

    def test_missing_dependency(self):
        """Test that missing dependencies raise ValueError."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": ["M_MISSING"]},
            ],
        }

        with pytest.raises(ValueError) as exc_info:
            resolve_module_dependencies(solution["modules"][0], solution)

        assert "not found" in str(exc_info.value)

    def test_partial_dependency_tree(self):
        """Test that only required dependencies are included."""
        solution = {
            "id": "TEST",
            "modules": [
                {"id": "M1", "title": "Module 1", "dependencies": []},
                {"id": "M2", "title": "Module 2", "dependencies": ["M1"]},
                {"id": "M3", "title": "Module 3", "dependencies": []},  # Independent
                {"id": "M4", "title": "Module 4", "dependencies": ["M2"]},
            ],
        }

        result = resolve_module_dependencies(solution["modules"][3], solution)

        # Should include M1, M2, M4 but NOT M3
        assert len(result) == 3
        assert [m["id"] for m in result] == ["M1", "M2", "M4"]

    def test_realistic_agency_workflow(self):
        """Test realistic agency workflow dependencies."""
        solution = {
            "id": "A1",
            "modules": [
                {"id": "A1_M1", "title": "Corporate Design", "dependencies": []},
                {"id": "A1_M2", "title": "Website", "dependencies": ["A1_M1"]},
                {"id": "A1_M3", "title": "SEO", "dependencies": ["A1_M2"]},
                {
                    "id": "A1_M4",
                    "title": "Social Campaign",
                    "dependencies": ["A1_M1", "A1_M2"],
                },
            ],
        }

        # Test selecting final module with complex dependencies
        result = resolve_module_dependencies(solution["modules"][3], solution)

        assert len(result) == 3  # M1, M2, M4 (not M3)
        assert result[0]["id"] == "A1_M1"  # Design must be first
        assert result[1]["id"] == "A1_M2"  # Website depends on design
        assert result[2]["id"] == "A1_M4"  # Campaign last
