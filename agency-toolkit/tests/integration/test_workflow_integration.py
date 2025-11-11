"""Workflow integration tests - validate end-to-end orchestrator functionality.

These tests verify that the refactored orchestrator correctly:
1. Executes multi-step workflows
2. Passes context between tasks
3. Uses the new TASK_REGISTRY dispatcher pattern
"""

from unittest.mock import MagicMock, patch

from agency_toolkit.core.orchestrator import execute_module


class TestWorkflowIntegration:
    """Test complete workflow execution with task chaining."""

    @patch("agency_toolkit.providers.get_text_provider")
    def test_ai_to_briefing_workflow_with_context_passing(
        self, mock_get_provider, tmp_path
    ):
        """Test AI task output is passed to briefing task via context.

        This validates:
        - AI task generates text
        - Output is stored in step_context with output_key
        - Briefing task can reference it via {tagline}
        """
        # Setup AI provider mock
        mock_provider = MagicMock()
        mock_provider.generate.return_value = {"response": "Join our innovative team!"}
        mock_get_provider.return_value = MagicMock(return_value=mock_provider)

        # Define workflow module
        module = {
            "id": "TEST_M1",
            "title": "Social Recruiting Test",
            "tasks": [
                {
                    "tool": "ai",
                    "output_key": "tagline",
                    "params": {
                        "prompt": "Generate recruiting tagline",
                        "provider": "mistral",
                        "temperature": 0.7,
                        "max_tokens": 50,
                    },
                },
                {
                    "tool": "briefing",
                    "params": {
                        "type": "Social",
                        "client_name": "TestCorp",
                        "project_name": "Recruiting Campaign",
                        "format_type": "md",
                        "output_dir": str(tmp_path),
                        "notes": "Tagline: {tagline}",  # Reference AI output
                    },
                },
            ],
        }

        # Execute workflow
        context = {
            "project_name": "TestCorp",
            "ai_provider": "mistral",
            "stop_on_error": True,
        }

        report = execute_module(module, context)

        # Verify execution
        assert len(report.task_results) == 2
        assert report.successful == 2
        assert report.failed == 0

        # Task 1 (AI) should succeed
        assert report.task_results[0].tool == "ai"
        assert report.task_results[0].success is True
        assert report.task_results[0].output == "Join our innovative team!"

        # Task 2 (Briefing) should succeed
        assert report.task_results[1].tool == "briefing"
        assert report.task_results[1].success is True

        # Verify AI output was passed to briefing
        # The briefing notes should contain the AI-generated tagline
        mock_provider.generate.assert_called_once()

    @patch("agency_toolkit.core.structure.generator.generate")
    def test_structure_task_execution_via_registry(
        self, mock_generate_structure, tmp_path
    ):
        """Test structure task uses new registry dispatcher."""
        mock_generate_structure.return_value = {
            "path": str(tmp_path / "test-client" / "test-project"),
            "type": "web",
        }

        module = {
            "id": "TEST_M2",
            "title": "Structure Test",
            "tasks": [
                {
                    "tool": "structure",
                    "params": {
                        "client": "TestClient",
                        "project": "TestProject",
                        "type": "web",
                        "base_path": str(tmp_path),
                        "dry_run": True,
                    },
                }
            ],
        }

        context = {"project_name": "TestProject"}
        report = execute_module(module, context)

        assert len(report.task_results) == 1
        assert report.task_results[0].success is True
        assert report.task_results[0].tool == "structure"
        assert report.successful == 1

        # Verify handler was called via registry
        mock_generate_structure.assert_called_once()
        call_kwargs = mock_generate_structure.call_args[1]
        assert call_kwargs["client"] == "TestClient"
        assert call_kwargs["project"] == "TestProject"
        assert call_kwargs["structure_type"] == "web"

    @patch("agency_toolkit.core.social.generator.generate")
    def test_social_task_with_bg_concept_from_context(
        self, mock_generate_social, tmp_path
    ):
        """Test social task receives bg_concept from workflow context."""
        mock_generate_social.return_value = {
            "path": str(tmp_path / "social_post.png"),
            "format": "square",
        }

        module = {
            "id": "TEST_M3",
            "title": "Social Test",
            "tasks": [
                {
                    "tool": "social",
                    "params": {
                        "text": "Check out our new product!",
                        "style": "modern",
                        "color": "blue",
                        "output_dir": str(tmp_path),
                        "dry_run": True,
                    },
                }
            ],
        }

        context = {
            "project_name": "TestProduct",
            "bg_concept": "moody",  # Background concept in context
        }

        report = execute_module(module, context)

        assert len(report.task_results) == 1
        assert report.task_results[0].success is True
        assert report.successful == 1

        # Verify bg_concept was passed from context
        mock_generate_social.assert_called_once()
        call_kwargs = mock_generate_social.call_args[1]
        assert call_kwargs["bg_concept"] == "moody"

    def test_unknown_tool_raises_clear_error(self):
        """Test that unknown tools produce helpful error messages."""
        module = {
            "id": "TEST_M4",
            "title": "Invalid Tool Test",
            "tasks": [
                {
                    "tool": "nonexistent_tool",
                    "params": {},
                }
            ],
        }

        context = {"project_name": "Test"}
        report = execute_module(module, context)

        assert len(report.task_results) == 1
        assert report.task_results[0].success is False
        assert (
            "Unknown task handler: 'nonexistent_tool'" in report.task_results[0].error
        )
        assert "Available handlers:" in report.task_results[0].error
        assert report.failed == 1

    @patch("agency_toolkit.providers.get_text_provider")
    @patch("agency_toolkit.core.structure.generator.generate")
    def test_multi_task_workflow_with_stop_on_error(
        self, mock_structure, mock_get_provider
    ):
        """Test workflow stops on first error when stop_on_error=True."""
        # First task succeeds
        mock_structure.return_value = {"path": "/test/path", "type": "web"}

        # Second task fails
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = Exception("API Error")
        mock_get_provider.return_value = MagicMock(return_value=mock_provider)

        module = {
            "id": "TEST_M5",
            "title": "Error Handling Test",
            "tasks": [
                {
                    "tool": "structure",
                    "params": {"client": "Test", "project": "Test"},
                },
                {
                    "tool": "ai",
                    "params": {"prompt": "Test prompt"},
                },
                {
                    "tool": "structure",
                    "params": {"client": "Test2", "project": "Test2"},
                },
            ],
        }

        context = {"stop_on_error": True}
        report = execute_module(module, context)

        # Should stop after second task fails
        assert len(report.task_results) == 2
        assert report.task_results[0].success is True
        assert report.task_results[1].success is False
        assert "API Error" in report.task_results[1].error
        assert report.successful == 1
        assert report.failed == 1
        assert report.skipped == 1

    @patch("agency_toolkit.providers.get_text_provider")
    def test_dynamic_prompt_formatting_with_context(self, mock_get_provider):
        """Test that {variable} placeholders are replaced from context."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = {"response": "Generated text"}
        mock_get_provider.return_value = MagicMock(return_value=mock_provider)

        module = {
            "id": "TEST_M6",
            "title": "Dynamic Prompt Test",
            "tasks": [
                {
                    "tool": "ai",
                    "params": {
                        "prompt": "Create ad for {company} targeting {audience}",
                        "provider": "mistral",
                    },
                }
            ],
        }

        context = {
            "company": "TechCorp Inc.",
            "audience": "software engineers",
        }

        report = execute_module(module, context)

        assert report.task_results[0].success is True
        assert report.successful == 1

        # Verify prompt was formatted with context variables
        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args[1]
        assert "TechCorp Inc." in call_args["prompt"]
        assert "software engineers" in call_args["prompt"]


class TestTaskRegistry:
    """Test that the task registry is properly configured."""

    def test_registry_contains_all_core_tools(self):
        """Verify all expected tools are registered."""
        # We need to import the handlers to ensure they are registered
        from agency_toolkit.tasks.registry import (
            get_task_handler,
            list_task_handlers,
        )

        registered_tools = list_task_handlers()
        expected_tools = ["structure", "briefing", "social", "ai"]

        for tool in expected_tools:
            assert tool in registered_tools, f"Tool '{tool}' not in registry"
            handler = get_task_handler(tool)
            assert callable(handler.execute), f"Handler for '{tool}' is not callable"

    def test_registry_handlers_have_correct_signature(self):
        """Verify all handlers accept (params, context) arguments."""
        import inspect

        # We need to import the handlers to ensure they are registered
        from agency_toolkit.tasks.registry import (
            get_task_handler,
            list_task_handlers,
        )

        for tool_name in list_task_handlers():
            handler = get_task_handler(tool_name)
            sig = inspect.signature(handler.execute)
            params = list(sig.parameters.keys())

            assert "params" in params, f"{tool_name} handler missing 'params' arg"
            assert "context" in params, f"{tool_name} handler missing 'context' arg"
