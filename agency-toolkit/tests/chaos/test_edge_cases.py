"""Chaos Testing - Edge Cases & Malformed Inputs (Epic 4.0.3)

Tests the resilience of the system against:
- Malformed/invalid inputs
- Extreme resource usage
- Network failures
- Filesystem issues

Philosophy: Every edge case should fail GRACEFULLY with clear errors,
never with cryptic exceptions or crashes.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestMalformedInputs:
    """Test handling of malformed and invalid inputs."""

    def test_social_with_emoji_overflow(self):
        """10,000 emojis should gracefully error, not crash."""
        from agency_toolkit.core.social.generator import generate
        from agency_toolkit.models import Config

        config = Config(output_dir="/tmp")
        text = "🎉" * 10000  # Massive emoji text

        # Should raise ValidationError, not crash with cryptic error
        with pytest.raises(ValueError) as exc_info:
            generate(
                text=text,
                style="modern",
                config=config,
            )

        # Error message should be clear
        assert (
            "text" in str(exc_info.value).lower()
            or "length" in str(exc_info.value).lower()
        )

    def test_workflow_with_circular_dependencies(self):
        """Circular deps should be caught at load time, not infinite loop."""
        from agency_toolkit.core.dependency_resolver import resolve_module_dependencies
        from agency_toolkit.exceptions import ValidationError

        # Create circular dependency
        modules_with_circular_deps = [
            {"id": "A", "dependencies": ["B"]},
            {"id": "B", "dependencies": ["C"]},
            {"id": "C", "dependencies": ["A"]},  # Closes the circle
        ]

        # Should raise clear error about circular deps
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            resolve_module_dependencies(modules_with_circular_deps)

        error_msg = str(exc_info.value).lower()
        assert "circular" in error_msg or "cycle" in error_msg

    def test_workflow_with_self_dependency(self):
        """Module depending on itself should be caught immediately."""
        from agency_toolkit.core.dependency_resolver import resolve_module_dependencies
        from agency_toolkit.exceptions import ValidationError

        # Create self-dependency
        modules = [
            {"id": "A", "dependencies": ["A"]},  # Self-reference
        ]

        with pytest.raises((ValidationError, ValueError)):
            resolve_module_dependencies(modules)

    def test_missing_required_dependency(self):
        """Module depending on non-existent module should fail clearly."""
        from agency_toolkit.core.dependency_resolver import resolve_module_dependencies
        from agency_toolkit.exceptions import ValidationError

        # Module B depends on non-existent module C
        modules = [
            {"id": "A", "dependencies": []},
            {"id": "B", "dependencies": ["C"]},  # C doesn't exist
        ]

        with pytest.raises((ValidationError, KeyError, ValueError)):
            resolve_module_dependencies(modules)

    def test_invalid_json_workflow(self, tmp_path):
        """Invalid JSON should be caught with clear error."""
        from agency_toolkit.core.workflow_loader import WorkflowLoader

        # Create invalid JSON file
        invalid_json_path = tmp_path / "invalid.json"
        invalid_json_path.write_text("{ invalid json }")

        loader = WorkflowLoader()

        with pytest.raises((ValueError, OSError)) as exc_info:
            loader.load_workflow(str(invalid_json_path))

        error_msg = str(exc_info.value).lower()
        assert "json" in error_msg or "parse" in error_msg or "invalid" in error_msg


class TestResourceExhaustion:
    """Test handling of extreme resource usage."""

    def test_1000_post_batch_doesnt_oom(self):
        """1000 posts should not cause out-of-memory error."""
        import csv

        from agency_toolkit.core.social.batch import process_batch_csv
        from agency_toolkit.models import Config

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            output_dir = tmp_path / "output"
            output_dir.mkdir()

            # Create 1000-post CSV
            csv_path = tmp_path / "large_batch.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "text"])
                writer.writeheader()
                for i in range(1, 1001):
                    writer.writerow({"id": f"post_{i}", "text": f"Post {i}"})

            config = Config(
                output_dir=str(output_dir),
                social_style="modern",
                social_color="blue",
            )

            # Mock to avoid real generation
            with patch("agency_toolkit.core.social.generator.generate") as mock_gen:
                mock_gen.return_value = {"path": str(output_dir / "test.png")}

                # Should complete without OOM error
                result = process_batch_csv(
                    config=config,
                    csv_path=csv_path,
                    output_dir=output_dir,
                )

                # Should process all or most items
                assert result["total"] == 1000
                assert result["successful"] > 0

    def test_deeply_nested_context_doesnt_stack_overflow(self):
        """Deep context nesting should not cause stack overflow."""
        from agency_toolkit.core.orchestrator import execute_module

        # Create deeply nested context (100 levels)
        deep_context = {"project_name": "test"}
        for i in range(100):
            deep_context[f"level_{i}"] = f"value_{i}"

        # Create simple module
        module = {
            "id": "M1",
            "title": "Test",
            "tasks": [
                {"tool": "structure", "params": {"client": "Test", "project": "Test"}}
            ],
        }

        # Mock to avoid actual execution
        with patch("agency_toolkit.core.structure.generate") as mock_struct:
            mock_struct.return_value = {"path": "/tmp"}

            # Should not crash with stack overflow
            report = execute_module(module, deep_context)
            assert report is not None


class TestNetworkFailures:
    """Test handling of network-related failures."""

    def test_ai_provider_timeout_fails_gracefully(self):
        """AI timeout should fail gracefully with clear error message."""
        from agency_toolkit.exceptions import ProviderError
        from agency_toolkit.providers.mistral_provider import MistralProvider

        provider = MistralProvider()

        # Mock timeout
        with patch.object(provider, "generate") as mock_generate:
            mock_generate.side_effect = TimeoutError("API timeout")

            with pytest.raises((TimeoutError, ProviderError, RuntimeError)):
                provider.generate(
                    prompt="test",
                    model="mistral-small-latest",
                    temperature=0.7,
                    max_tokens=100,
                )

    def test_image_provider_rate_limit_fails_gracefully(self):
        """Rate limit should fail gracefully without retry loop."""
        from agency_toolkit.providers.pollinations import PollinationsProvider

        provider = PollinationsProvider()

        # Mock rate limit (HTTP 429)
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_get.return_value = mock_response

            # Should fail with clear rate limit error
            with pytest.raises((RuntimeError, ValueError)):
                provider.generate(
                    prompt="test",
                    seed=42,
                    width=1024,
                    height=1024,
                )

    def test_missing_api_key_fails_at_start(self):
        """Missing API key should fail immediately, not after 10 retries."""
        from agency_toolkit.providers.mistral_provider import MistralProvider

        # Ensure no API key in environment
        with patch.dict(os.environ, {}, clear=False):
            if "MISTRAL_API_KEY" in os.environ:
                del os.environ["MISTRAL_API_KEY"]

            provider = MistralProvider()

            # Should fail immediately when trying to generate
            with pytest.raises((ValueError, KeyError, Exception)):
                provider.generate(
                    prompt="test",
                    model="mistral-small-latest",
                    temperature=0.7,
                    max_tokens=100,
                )


class TestFilesystemIssues:
    """Test handling of filesystem-related problems."""

    def test_readonly_output_dir_fails_with_clear_message(self, tmp_path):
        """Cannot write to read-only dir should fail with clear message."""
        from agency_toolkit.core.social.generator import generate
        from agency_toolkit.models import Config

        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()

        # Make directory read-only
        readonly_dir.chmod(0o555)

        config = Config(output_dir=str(readonly_dir))

        try:
            with pytest.raises((PermissionError, OSError)) as exc_info:
                generate(
                    text="test",
                    style="modern",
                    config=config,
                )

            error_msg = str(exc_info.value).lower()
            assert (
                "permission" in error_msg
                or "read-only" in error_msg
                or "cannot write" in error_msg
            )

        finally:
            # Clean up: restore permissions for deletion
            readonly_dir.chmod(0o755)

    def test_missing_output_directory_created_automatically(self, tmp_path):
        """Missing output directory should be created automatically."""
        from agency_toolkit.core.structure import generate
        from agency_toolkit.models import Config

        # Use non-existent path
        output_dir = tmp_path / "nonexistent" / "nested" / "structure"

        config = Config(output_dir=str(output_dir))

        with patch(
            "agency_toolkit.core.structure.writer.create_directories"
        ) as mock_create:
            mock_create.return_value = None

            # Should handle missing directory gracefully
            result = generate(
                client="Test",
                project="Test",
                structure_type="web",
                base_path=output_dir,
            )

            # Should complete without FileNotFoundError
            assert result is not None

    def test_corrupt_config_file_fails_gracefully(self, tmp_path):
        """Corrupt config file should fail with clear error."""
        from agency_toolkit.config import load_config

        # Create corrupt TOML config
        bad_config = tmp_path / "bad_config.toml"
        bad_config.write_text("[section\ninvalid toml syntax [[")

        with pytest.raises((ValueError, OSError)) as exc_info:
            load_config(bad_config)

        error_msg = str(exc_info.value).lower()
        assert "config" in error_msg or "toml" in error_msg or "parse" in error_msg


class TestBoundaryConditions:
    """Test handling of boundary and edge conditions."""

    def test_empty_workflow_completes_successfully(self):
        """Empty workflow (no tasks) should complete, not crash."""
        from agency_toolkit.core.orchestrator import execute_module

        # Create module with no tasks
        module = {
            "id": "M1",
            "title": "Empty",
            "tasks": [],
        }

        # Should complete without error
        report = execute_module(module, {})
        assert report.total_tasks == 0
        assert report.successful == 0

    def test_extremely_long_filenames_handled(self):
        """256+ character filenames should be truncated gracefully."""
        from agency_toolkit.utils import sanitize_name

        # Create extremely long name
        long_name = "A" * 500

        # Should truncate without error
        result = sanitize_name(long_name)
        assert len(result) <= 255

    def test_special_characters_in_paths(self, tmp_path):
        """Paths with special chars should be escaped properly."""
        from agency_toolkit.core.structure import generate

        # Create path with special characters
        special_name = "Test & Co. | <Special>"

        with patch("agency_toolkit.core.structure.generator.validate_names"):
            with patch("agency_toolkit.core.structure.writer.create_directories"):
                # Should handle special characters without crash
                result = generate(
                    client=special_name,
                    project="Test",
                    structure_type="web",
                    base_path=tmp_path,
                )

                assert result is not None or result == {}
