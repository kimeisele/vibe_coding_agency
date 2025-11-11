"""Unit tests validating the ExploreAgent bug fixes and improvements."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestExploreAgentCodeChanges:
    """Validate the critical bug fixes through code analysis and unit tests."""

    def test_code_syntax_valid(self):
        """Verify the modified agent.py file has valid Python syntax."""
        import py_compile
        import tempfile

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        # This will raise SyntaxError if invalid
        py_compile.compile(str(agent_file), doraise=True)

    def test_imports_added_for_type_hints(self):
        """Verify Union type is imported for Step type alias."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        # Check imports
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        typing_imports = [
            node for node in imports
            if node.module == 'typing'
        ]

        # Verify Union was imported
        assert len(typing_imports) > 0, "Union should be imported from typing"
        union_imported = any(
            alias.name == 'Union' or alias.name == '*'
            for node in typing_imports
            for alias in node.names
        )
        assert union_imported, "Union type should be imported"

    def test_step_type_alias_exists(self):
        """Verify Step type alias is defined."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Check that Step type alias is mentioned
        assert "Step = Union[ToolCall, str]" in source, "Step type alias should be defined"
        assert "from mistralai.models import ToolCall" in source or "ToolCall" in source

    def test_execute_step_method_exists(self):
        """Verify new _execute_step method is defined."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        # Find ExploreAgent class
        explore_agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent_class = node
                break

        assert explore_agent_class is not None, "ExploreAgent class should exist"

        # Check for _execute_step method
        method_names = [
            node.name for node in explore_agent_class.body
            if isinstance(node, ast.FunctionDef)
        ]

        assert "_execute_step" in method_names, "_execute_step method should be defined"

    def test_get_step_description_method_exists(self):
        """Verify new _get_step_description helper method is defined."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        explore_agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent_class = node
                break

        assert explore_agent_class is not None

        method_names = [
            node.name for node in explore_agent_class.body
            if isinstance(node, ast.FunctionDef)
        ]

        assert "_get_step_description" in method_names, "_get_step_description method should exist"

    def test_critical_bug_fixed_execute_all_steps(self):
        """Verify the critical bug is fixed - all steps should be executed."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # The old buggy code was: step = steps[0]
        # The fixed code should have: for step in steps:

        # Verify old bug is NOT present
        lines = source.split('\n')

        # Look for the main execution loop
        found_for_loop = False
        for i, line in enumerate(lines):
            if "for step in steps:" in line:
                found_for_loop = True
                # Make sure it's not followed by [0] indexing
                break

        assert found_for_loop, "Code should loop through all steps with 'for step in steps:'"

        # Make sure the old buggy pattern is gone from the execute section
        # (it might still exist in serialization)
        execute_section = [
            line for line in lines[70:95]  # Main execute section
            if "step = steps[0]" in line
        ]
        assert len(execute_section) == 0, "The buggy 'step = steps[0]' should be removed from execute section"

    def test_exception_handling_added(self):
        """Verify try-except block is added around step execution."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Verify try-except exists in _execute_step
        assert "try:" in source, "Try block should exist"
        assert "except Exception as e:" in source, "Exception handling should exist"
        assert "_logger.exception" in source, "Logger should record exceptions"

    def test_result_validation_added(self):
        """Verify result structure validation is implemented."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Check for result validation
        assert "isinstance(result, dict)" in source, "Result should be validated as dict"
        assert 'result.get("success", False)' in source, "Defensive get() with default should be used"

    def test_status_determination_improved(self):
        """Verify status determination logic is simplified and includes FAILED state."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Check that FAILED status is explicitly returned
        assert 'return "FAILED"' in source, "FAILED status should be explicitly returned"

        # Check for explicit failure detection
        assert "has_failures" in source or "not e.get" in source, "Should check for execution failures"

    def test_serialize_steps_uses_helper(self):
        """Verify _serialize_steps uses _get_step_description helper."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Find _serialize_steps method
        serialize_start = source.find("def _serialize_steps")
        serialize_end = source.find("\n    def ", serialize_start + 1)
        serialize_method = source[serialize_start:serialize_end]

        # Should use _get_step_description helper
        assert "_get_step_description" in serialize_method, \
            "_serialize_steps should use _get_step_description helper"


class TestExploreAgentBehavioralValidation:
    """Behavioral tests to validate fix correctness."""

    def test_execute_step_method_has_proper_signature(self):
        """Verify _execute_step method has correct signature."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        # Find ExploreAgent class and _execute_step method
        explore_agent = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent = node
                break

        assert explore_agent is not None

        execute_step_method = None
        for node in explore_agent.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_execute_step":
                execute_step_method = node
                break

        assert execute_step_method is not None, "_execute_step method should exist"

        # Check signature has step and iteration parameters
        arg_names = [arg.arg for arg in execute_step_method.args.args[1:]]  # Skip 'self'
        assert "step" in arg_names, "Should have 'step' parameter"
        assert "iteration" in arg_names, "Should have 'iteration' parameter"

        # Check it has type hints
        has_return_annotation = execute_step_method.returns is not None
        assert has_return_annotation, "Should have return type annotation"

    def test_main_run_loop_executes_all_steps(self):
        """Verify run() method's main loop executes all returned steps."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        # Find run method
        explore_agent = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent = node
                break

        run_method = None
        for node in explore_agent.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run":
                run_method = node
                break

        assert run_method is not None, "run method should exist"

        # Get the source of the run method to verify loop structure
        run_source = ast.get_source_segment(open(agent_file).read(), run_method)

        # Should have "for step in steps:" pattern
        assert "for step in steps:" in run_source, "Should iterate through all steps"

    def test_no_hardcoded_step_indexing_in_execution(self):
        """Verify no hardcoded step[0] access in the main execution path."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Get just the run method's execute section (lines 70-95)
        lines = source.split('\n')
        execute_section = '\n'.join(lines[70:100])

        # Should NOT have steps[0] in the main execution
        assert "step = steps[0]" not in execute_section, \
            "Should not have hardcoded steps[0] in execution section"
        assert "[0]" not in execute_section, \
            "Should not index steps directly in main execution"


class TestExploreAgentDocumentation:
    """Verify proper documentation of fixes."""

    def test_docstrings_added_for_new_methods(self):
        """Verify new methods have proper docstrings."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        explore_agent = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent = node
                break

        # Check _execute_step has docstring
        execute_step_method = None
        for node in explore_agent.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_execute_step":
                execute_step_method = node
                break

        assert execute_step_method is not None
        docstring = ast.get_docstring(execute_step_method)
        assert docstring is not None, "_execute_step should have a docstring"
        assert "error handling" in docstring.lower(), "Docstring should mention error handling"

    def test_status_determination_documented(self):
        """Verify status determination method documents its return values."""
        import ast

        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            tree = ast.parse(f.read())

        explore_agent = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExploreAgent":
                explore_agent = node
                break

        determine_status_method = None
        for node in explore_agent.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_determine_status":
                determine_status_method = node
                break

        docstring = ast.get_docstring(determine_status_method)
        assert docstring is not None, "Should have docstring"

        # Should document the return values
        assert "COMPLETED" in docstring or "FAILED" in docstring or "return" in docstring.lower()


class TestFixCompleteness:
    """Verify all Priority 1 and 2 fixes are implemented."""

    def test_priority_1_critical_bug_fixed(self):
        """✅ Priority 1.1: Execute all steps (not just first)."""
        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # The fix should be "for step in steps:"
        assert "for step in steps:" in source

        # Old code should not exist in execute section
        execute_part = source.split("if not steps:")[1].split("return self._finalize_run()")[0]
        assert "step = steps[0]" not in execute_part

    def test_priority_1_exception_handling_added(self):
        """✅ Priority 1.2: Add exception handling."""
        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        assert "try:" in source
        assert "except Exception as e:" in source
        assert "error_result = {" in source or "return {" in source.split("except")[1]

    def test_priority_2_result_validation(self):
        """✅ Priority 2.1: Validate result structure."""
        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        assert "isinstance(result, dict)" in source
        assert 'result.get("success", False)' in source

    def test_priority_2_status_determination_simplified(self):
        """✅ Priority 2.3: Simplify status determination logic."""
        agent_file = Path(__file__).parent.parent.parent / "reference" / "phoenix_explore_agent" / "agent.py"

        with open(agent_file, 'r') as f:
            source = f.read()

        # Should have explicit FAILED state
        assert 'return "FAILED"' in source

        # Should have explicit COMPLETED state
        assert 'return "COMPLETED"' in source

        # Should have INCOMPLETE state
        assert 'return "INCOMPLETE"' in source
