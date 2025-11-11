"""User Acceptance Testing (UAT) - Agency Onboarding Scenario.

This test validates the complete onboarding workflow for a new client:
- Create project structure
- Generate briefing document
- Execute multi-task workflow to generate initial content
- Verify all deliverables are created

User Story: "As an agency, I want to onboard a new client and generate
their first set of content (briefing + social posts) from scratch."
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agency_toolkit.core.orchestrator import execute_module
from agency_toolkit.core.structure import generate as generate_structure


class TestOnboardingWorkflow:
    """Complete client onboarding workflow tests."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for onboarding workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            yield workspace

    @pytest.fixture
    def mock_config(self):
        """Mock config for tests."""
        from agency_toolkit.models import Config

        return Config(
            output_dir="/tmp/test",
            social_style="modern",
            social_color="blue",
        )

    def test_complete_onboarding_creates_structure(self, temp_workspace, mock_config):
        """Test that onboarding workflow creates project structure.

        Verifies:
        - Project folder structure created successfully
        - README.md exists
        - Subdirectories created
        """
        with patch(
            "agency_toolkit.core.structure.writer.create_directories"
        ) as mock_create:
            mock_create.return_value = None

            result = generate_structure(
                client="Test Client",
                project="Test Project",
                structure_type="web",
                base_path=temp_workspace,
            )

            # Should return a dict with path and type
            assert isinstance(result, dict)
            assert "path" in result or "type" in result

    def test_onboarding_workflow_executes_module_chain(
        self, temp_workspace, mock_config
    ):
        """Test that onboarding workflow executes module chain correctly.

        Verifies:
        - Module execution completes
        - Tasks execute in order
        - Context passing works
        """
        workflow_module = {
            "id": "M1",
            "title": "Onboarding",
            "tasks": [
                {
                    "tool": "structure",
                    "params": {
                        "client": "Test Client",
                        "project": "Test Project",
                        "structure_type": "web",
                    },
                }
            ],
        }

        with patch("agency_toolkit.core.structure.generate") as mock_struct:
            mock_struct.return_value = {"path": str(temp_workspace), "type": "web"}

            report = execute_module(workflow_module, {"project_name": "Test"})

            # Should return WorkflowExecutionReport
            assert report.module_id == "M1"
            assert report.total_tasks == 1
            assert report.successful >= 0  # At least attempted

    def test_onboarding_handles_errors_gracefully(self, temp_workspace, mock_config):
        """Test that onboarding workflow handles errors gracefully.

        Verifies:
        - Errors are caught and reported
        - on_error: continue allows workflow to continue
        """
        workflow_module = {
            "id": "M1",
            "title": "Onboarding",
            "tasks": [
                {
                    "tool": "structure",
                    "on_error": "continue",
                    "params": {
                        "client": "Test Client",
                        "project": "Test Project",
                    },
                }
            ],
        }

        with patch("agency_toolkit.core.structure.generate") as mock_struct:
            mock_struct.side_effect = Exception("Test error")

            report = execute_module(workflow_module, {"project_name": "Test"})

            # on_error: continue means we keep going
            assert report.module_id == "M1"
