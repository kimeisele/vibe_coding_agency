"""Tests for workflow JSON schema validation.

Tests cover:
- Valid archetype and solution structures
- Invalid JSON structures and missing required fields
- Schema validation error handling
- Edge cases and boundary conditions
"""

from pathlib import Path

import pytest

from agency_toolkit.core.workflow_loader import (
    get_workflow_schema,
    load_archetypes,
    load_solutions,
    validate_workflow_json,
)
from agency_toolkit.exceptions import ValidationError


class TestWorkflowSchemaLoading:
    """Test loading and accessing the workflow schema."""

    def test_get_workflow_schema_loads_successfully(self):
        """Verify workflow schema file loads without errors."""
        schema = get_workflow_schema()
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "definitions" in schema

    def test_workflow_schema_has_required_definitions(self):
        """Verify schema has required type definitions."""
        schema = get_workflow_schema()
        required_defs = ["task", "module", "archetype", "solution"]
        for def_name in required_defs:
            assert def_name in schema["definitions"], f"Missing definition: {def_name}"

    def test_schema_file_exists(self):
        """Verify workflow_schema.json file exists in registry directory."""
        schema_file = (
            Path(__file__).parent.parent.parent / "registry" / "workflow_schema.json"
        )
        assert schema_file.exists(), f"Schema file not found at {schema_file}"


class TestArchetypeValidation:
    """Test validation of archetype JSON structures."""

    def test_valid_archetype_passes_validation(self):
        """Verify valid archetype structure passes schema validation."""
        valid_archetype = [
            {
                "id": "I",
                "name": "Test Archetype",
                "description": "A test archetype",
                "pains": ["Pain 1", "Pain 2"],
                "goals": ["Goal 1", "Goal 2"],
                "solution_template_ids": ["A1", "A2"],
            }
        ]
        # Should not raise
        validate_workflow_json(valid_archetype)

    def test_archetype_missing_required_id_fails(self):
        """Verify archetype without id fails validation."""
        invalid_archetype = [
            {
                "name": "Test Archetype",
                "description": "A test archetype",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_archetype)

    def test_archetype_missing_required_name_fails(self):
        """Verify archetype without name fails validation."""
        invalid_archetype = [
            {
                "id": "I",
                "description": "A test archetype",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_archetype)

    def test_archetype_missing_description_fails(self):
        """Verify archetype without description fails validation."""
        invalid_archetype = [
            {
                "id": "I",
                "name": "Test Archetype",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_archetype)

    def test_archetype_with_invalid_id_pattern_fails(self):
        """Verify archetype with invalid ID pattern fails validation."""
        invalid_archetype = [
            {
                "id": "invalid-id",  # Should only contain A-Z0-9
                "name": "Test Archetype",
                "description": "A test archetype",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_archetype)

    def test_archetype_optional_fields_allowed(self):
        """Verify archetype with only required fields passes."""
        minimal_archetype = [
            {
                "id": "I",
                "name": "Minimal Archetype",
                "description": "Minimal description",
            }
        ]
        # Should not raise
        validate_workflow_json(minimal_archetype)

    def test_archetype_with_extra_fields_fails(self):
        """Verify archetype with extra fields fails validation."""
        invalid_archetype = [
            {
                "id": "I",
                "name": "Test Archetype",
                "description": "A test archetype",
                "extra_field": "should not be here",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_archetype)


class TestTaskValidation:
    """Test validation of task structures within modules."""

    def test_valid_task_passes_validation(self):
        """Verify valid task structure passes schema validation."""
        valid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [
                            {
                                "tool": "ai",
                                "output_key": "result",
                                "on_error": "continue",
                                "params": {"prompt": "Test prompt"},
                            }
                        ],
                    }
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(valid_solution)

    def test_task_missing_required_tool_fails(self):
        """Verify task without tool fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [
                            {
                                "params": {"prompt": "Test prompt"},
                            }
                        ],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_task_with_invalid_on_error_mode_fails(self):
        """Verify task with invalid on_error mode fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [
                            {
                                "tool": "ai",
                                "on_error": "invalid_mode",
                                "params": {"prompt": "Test prompt"},
                            }
                        ],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_task_with_valid_on_error_modes(self):
        """Verify tasks with valid on_error modes pass validation."""
        for on_error_mode in ["stop", "continue"]:
            valid_solution = [
                {
                    "id": "A1",
                    "name": "Test Solution",
                    "archetype_id": "I",
                    "modules": [
                        {
                            "id": "A1_M1",
                            "title": "Module 1",
                            "tasks": [
                                {
                                    "tool": "ai",
                                    "on_error": on_error_mode,
                                    "params": {},
                                }
                            ],
                        }
                    ],
                }
            ]
            # Should not raise
            validate_workflow_json(valid_solution)

    def test_task_without_optional_params_passes(self):
        """Verify task without params passes validation."""
        valid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [
                            {
                                "tool": "ai",
                            }
                        ],
                    }
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(valid_solution)


class TestModuleValidation:
    """Test validation of module structures."""

    def test_valid_module_passes_validation(self):
        """Verify valid module structure passes schema validation."""
        valid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "description": "Test module",
                        "tasks": [],
                        "dependencies": [],
                        "context_variables": [],
                    }
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(valid_solution)

    def test_module_missing_required_id_fails(self):
        """Verify module without id fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "title": "Module 1",
                        "tasks": [],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_module_missing_required_title_fails(self):
        """Verify module without title fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "tasks": [],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_module_missing_required_tasks_fails(self):
        """Verify module without tasks fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_module_with_invalid_id_pattern_fails(self):
        """Verify module with invalid ID pattern fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "invalid-module-id",
                        "title": "Module 1",
                        "tasks": [],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)


class TestSolutionValidation:
    """Test validation of solution structures."""

    def test_valid_solution_passes_validation(self):
        """Verify valid solution structure passes schema validation."""
        valid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "description": "Test description",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [],
                    }
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(valid_solution)

    def test_solution_missing_required_id_fails(self):
        """Verify solution without id fails validation."""
        invalid_solution = [
            {
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_solution_missing_required_name_fails(self):
        """Verify solution without name fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "archetype_id": "I",
                "modules": [],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_solution_missing_required_archetype_id_fails(self):
        """Verify solution without archetype_id fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "modules": [],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_solution_missing_required_modules_fails(self):
        """Verify solution without modules fails validation."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)

    def test_solution_with_invalid_id_pattern_fails(self):
        """Verify solution with invalid ID pattern fails validation."""
        invalid_solution = [
            {
                "id": "invalid-solution",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [],
            }
        ]
        with pytest.raises(ValidationError, match="Invalid workflow JSON"):
            validate_workflow_json(invalid_solution)


class TestRealWorldValidation:
    """Test validation of actual registry files."""

    def test_load_archetypes_validates_successfully(self):
        """Verify actual archetypes.json file passes validation."""
        # This tests that the real registry file is valid
        archetypes = load_archetypes()
        assert isinstance(archetypes, list)
        assert len(archetypes) > 0
        # Verify structure
        for archetype in archetypes:
            assert "id" in archetype
            assert "name" in archetype
            assert "description" in archetype

    def test_load_solutions_validates_successfully(self):
        """Verify actual solutions.json file passes validation."""
        # This tests that the real registry file is valid
        solutions = load_solutions()
        assert isinstance(solutions, list)
        assert len(solutions) > 0
        # Verify structure
        for solution in solutions:
            assert "id" in solution
            assert "name" in solution
            assert "archetype_id" in solution
            assert "modules" in solution


class TestValidationErrorMessages:
    """Test that validation errors provide helpful information."""

    def test_validation_error_includes_path_information(self):
        """Verify validation errors include path to invalid data."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [
                            {
                                "on_error": "invalid",  # Invalid mode
                            }
                        ],
                    }
                ],
            }
        ]
        with pytest.raises(ValidationError) as exc_info:
            validate_workflow_json(invalid_solution)
        error_msg = str(exc_info.value)
        assert "Invalid workflow JSON" in error_msg

    def test_validation_error_is_descriptive(self):
        """Verify validation errors are descriptive."""
        invalid_solution = [
            {
                "id": "A1",
                "name": "Test Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Module 1",
                        "tasks": [],
                    }
                ],
                "extra_field": "invalid",
            }
        ]
        with pytest.raises(ValidationError) as exc_info:
            validate_workflow_json(invalid_solution)
        error_msg = str(exc_info.value)
        assert len(error_msg) > 10  # Should have meaningful error message


class TestComplexWorkflows:
    """Test validation of complex workflow structures."""

    def test_complex_workflow_with_multiple_modules_validates(self):
        """Verify complex workflow with multiple modules validates."""
        complex_solution = [
            {
                "id": "A1",
                "name": "Complex Solution",
                "archetype_id": "I",
                "description": "Solution with multiple modules",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Foundation Module",
                        "description": "First module",
                        "tasks": [
                            {
                                "tool": "structure",
                                "params": {
                                    "client": "{project_name}",
                                    "project": "Corporate Design",
                                },
                            }
                        ],
                        "dependencies": [],
                    },
                    {
                        "id": "A1_M2",
                        "title": "Website Module",
                        "description": "Website creation",
                        "tasks": [
                            {
                                "tool": "briefing",
                                "params": {
                                    "type": "Web",
                                    "client_name": "{project_name_safe}",
                                },
                            }
                        ],
                        "dependencies": ["A1_M1"],
                    },
                    {
                        "id": "A1_M3",
                        "title": "Social Module",
                        "description": "Social content creation",
                        "tasks": [
                            {
                                "tool": "social",
                                "output_key": "social_content",
                                "on_error": "continue",
                                "params": {
                                    "text": "{tagline}",
                                    "style": "bold",
                                },
                            }
                        ],
                        "dependencies": ["A1_M1", "A1_M2"],
                    },
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(complex_solution)

    def test_workflow_with_all_task_types_validates(self):
        """Verify workflow using all task types validates."""
        multi_task_solution = [
            {
                "id": "A1",
                "name": "Multi-Task Solution",
                "archetype_id": "I",
                "modules": [
                    {
                        "id": "A1_M1",
                        "title": "Multi-Task Module",
                        "tasks": [
                            {"tool": "structure", "params": {}},
                            {"tool": "briefing", "params": {}},
                            {
                                "tool": "ai",
                                "output_key": "ai_output",
                                "params": {"prompt": "Generate content"},
                            },
                            {"tool": "social", "params": {}},
                        ],
                    }
                ],
            }
        ]
        # Should not raise
        validate_workflow_json(multi_task_solution)
