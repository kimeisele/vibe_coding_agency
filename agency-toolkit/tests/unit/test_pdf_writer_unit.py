"""Unit tests for PDF writer with timeout mechanism."""

import time
from datetime import date
from pathlib import Path

import pytest

from agency_toolkit.core.briefing import BriefingData
from agency_toolkit.core.briefing.pdf_writer import (
    PDFTimeoutError,
    timeout_handler,
    write_pdf,
)


class TestTimeoutHandler:
    """Tests for the timeout_handler decorator."""

    def test_timeout_handler_completes_fast_function(self):
        """Verify timeout handler allows fast functions to complete."""

        @timeout_handler(timeout_seconds=2)
        def fast_function():
            return "success"

        result = fast_function()
        assert result == "success"

    def test_timeout_handler_raises_on_slow_function(self):
        """Verify timeout handler raises PDFTimeoutError on slow functions."""

        @timeout_handler(timeout_seconds=1)
        def slow_function():
            time.sleep(2)
            return "should not reach"

        with pytest.raises(PDFTimeoutError):
            slow_function()

    def test_timeout_handler_propagates_exceptions(self):
        """Verify timeout handler propagates exceptions from wrapped function."""

        @timeout_handler(timeout_seconds=2)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestWritePDF:
    """Tests for PDF writing with timeout protection."""

    @pytest.fixture
    def sample_briefing_data(self):
        """Provide sample briefing data."""
        return BriefingData(
            client_name="Test Client",
            project_name="Test Project",
            project_type="Web",
            deadline=date(2024, 12, 31),
            deliverables=["Homepage", "Blog"],
        )

    def test_write_pdf_creates_valid_file(self, sample_briefing_data, tmp_path):
        """Verify write_pdf creates a valid PDF file."""
        output_path = tmp_path / "test.pdf"

        # Should not raise
        write_pdf(sample_briefing_data, output_path)

        # File should exist and be non-empty
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Verify it's a PDF (starts with %PDF magic number)
        with open(output_path, "rb") as f:
            content = f.read()
            assert content.startswith(b"%PDF")

    def test_write_pdf_raises_if_output_dir_missing(self, sample_briefing_data):
        """Verify write_pdf raises FileNotFoundError if output directory doesn't exist."""
        output_path = Path("/nonexistent/directory/test.pdf")

        with pytest.raises(FileNotFoundError):
            write_pdf(sample_briefing_data, output_path)

    def test_write_pdf_with_minimal_data(self, tmp_path):
        """Verify write_pdf works with minimal briefing data."""
        briefing = BriefingData(
            client_name="Client",
            project_name="Project",
            deadline=date(2024, 12, 31),
        )
        output_path = tmp_path / "minimal.pdf"

        write_pdf(briefing, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_write_pdf_with_full_data(self, tmp_path):
        """Verify write_pdf works with complete briefing data."""
        briefing = BriefingData(
            client_name="Acme Corp",
            project_name="Website Redesign",
            project_type="Web",
            deadline=date(2024, 12, 31),
            budget=5000.0,
            objectives="Modernize digital presence",
            target_audience="B2B decision makers",
            deliverables=["Homepage", "Blog", "Contact page"],
            notes="Prefer modern design with dark theme",
        )
        output_path = tmp_path / "full.pdf"

        write_pdf(briefing, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 1000  # Should be larger with more content
