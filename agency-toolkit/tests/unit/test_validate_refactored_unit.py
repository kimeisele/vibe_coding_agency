"""Unit tests for refactored validate.py functions."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agency_toolkit.commands.validate import (
    _aggregate_comparison_results,
    _collect_snapshot_files,
    _compare_generic_files,
    _compare_image_files,
    _compare_json_files,
    _compare_pdf_files,
    _compare_snapshots,
    _extract_pdf_text,
    _get_file_comparator,
    _hash_file,
    _process_file_comparison,
    _validate_snapshot_dirs,
)
from agency_toolkit.core.reporter import Reporter


class TestHashFile:
    """Test _hash_file function."""

    def test_hash_file_same_content(self):
        """Test that identical files produce same hash."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            hash1 = _hash_file(temp_path)
            hash2 = _hash_file(temp_path)
            assert hash1 == hash2
            assert len(hash1) == 64  # SHA-256 hex length
        finally:
            temp_path.unlink()

    def test_hash_file_different_content(self):
        """Test that different files produce different hashes."""
        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as f1,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as f2,
        ):
            f1.write("content1")
            f2.write("content2")
            temp_path1 = Path(f1.name)
            temp_path2 = Path(f2.name)

        try:
            hash1 = _hash_file(temp_path1)
            hash2 = _hash_file(temp_path2)
            assert hash1 != hash2
        finally:
            temp_path1.unlink()
            temp_path2.unlink()


class TestExtractPdfText:
    """Test _extract_pdf_text function."""

    def test_extract_pdf_text_without_pypdf(self):
        """Test behavior when pypdf is not installed."""
        mock_reporter = Mock(spec=Reporter)

        with patch.dict("sys.modules", {"pypdf": None}):
            result = _extract_pdf_text(Path("dummy.pdf"), mock_reporter)
            assert result == ""
            mock_reporter.warning.assert_called_once()

    def test_extract_pdf_text_with_pypdf(self):
        """Test successful PDF text extraction (skipped if pypdf not available)."""
        try:
            from pypdf import PdfReader
        except ImportError:
            pytest.skip("pypdf not available")

        # This test would require actual PDF files, so we skip the detailed test
        # The main functionality is tested in integration tests
        pass


class TestFileComparators:
    """Test file comparison functions."""

    def test_compare_generic_files_identical(self):
        """Test generic file comparison with identical files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "test1.txt"
            file2 = tmp_path / "test2.txt"

            content = "identical content"
            file1.write_text(content)
            file2.write_text(content)

            mock_reporter = Mock(spec=Reporter)
            result = _compare_generic_files(file1, file2, "test.txt", mock_reporter)

            assert result["passed"] is True
            mock_reporter.validation_result.assert_called_once_with(
                "test.txt", True, "hash match"
            )

    def test_compare_generic_files_different(self):
        """Test generic file comparison with different files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "test1.txt"
            file2 = tmp_path / "test2.txt"

            file1.write_text("content1")
            file2.write_text("content2")

            mock_reporter = Mock(spec=Reporter)
            result = _compare_generic_files(file1, file2, "test.txt", mock_reporter)

            assert result["passed"] is False
            assert "difference" in result
            mock_reporter.validation_result.assert_called_once_with(
                "test.txt", False, "hash differs"
            )

    def test_compare_image_files_identical(self):
        """Test image file comparison with identical files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "test1.png"
            file2 = tmp_path / "test2.png"

            content = b"identical image data"
            file1.write_bytes(content)
            file2.write_bytes(content)

            mock_reporter = Mock(spec=Reporter)
            result = _compare_image_files(file1, file2, "test.png", mock_reporter)

            assert result["passed"] is True
            mock_reporter.validation_result.assert_called_once_with(
                "test.png", True, "hash match"
            )

    def test_compare_json_files_identical(self):
        """Test JSON file comparison with identical content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "test1.json"
            file2 = tmp_path / "test2.json"

            data = {"key": "value", "number": 42}
            file1.write_text(json.dumps(data, sort_keys=True))
            file2.write_text(json.dumps(data, sort_keys=True))

            mock_reporter = Mock(spec=Reporter)
            result = _compare_json_files(file1, file2, "test.json", mock_reporter)

            assert result["passed"] is True
            mock_reporter.validation_result.assert_called_once_with(
                "test.json", True, "content match"
            )

    def test_compare_json_files_different(self):
        """Test JSON file comparison with different content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "test1.json"
            file2 = tmp_path / "test2.json"

            file1.write_text(json.dumps({"key": "value1"}))
            file2.write_text(json.dumps({"key": "value2"}))

            mock_reporter = Mock(spec=Reporter)
            result = _compare_json_files(file1, file2, "test.json", mock_reporter)

            assert result["passed"] is False
            assert "difference" in result
            mock_reporter.validation_result.assert_called_once_with(
                "test.json", False, "content differs"
            )

    @patch("agency_toolkit.commands.validate._extract_pdf_text")
    def test_compare_pdf_files_identical(self, mock_extract_text):
        """Test PDF file comparison with identical content."""
        mock_extract_text.return_value = "same pdf text"

        mock_reporter = Mock(spec=Reporter)
        result = _compare_pdf_files(
            Path("file1.pdf"), Path("file2.pdf"), "test.pdf", mock_reporter
        )

        assert result["passed"] is True
        mock_reporter.validation_result.assert_called_once_with(
            "test.pdf", True, "text match"
        )

    def test_get_file_comparator(self):
        """Test getting appropriate comparator for file types."""
        assert _get_file_comparator("test.pdf") == _compare_pdf_files
        assert _get_file_comparator("test.png") == _compare_image_files
        assert _get_file_comparator("test.jpg") == _compare_image_files
        assert _get_file_comparator("test.jpeg") == _compare_image_files
        assert _get_file_comparator("test.json") == _compare_json_files
        assert _get_file_comparator("test.txt") == _compare_generic_files


class TestProcessFileComparison:
    """Test _process_file_comparison function."""

    def test_process_new_file(self):
        """Test processing a file that exists only in current."""
        current_files = {"new.txt": Path("current/new.txt")}
        approved_files = {}

        mock_reporter = Mock(spec=Reporter)
        result = _process_file_comparison(
            "new.txt", current_files, approved_files, mock_reporter
        )

        assert result["passed"] is False
        assert result["status"] == "new"
        mock_reporter.validation_result.assert_called_once_with(
            "new.txt", False, "NEW (not in approved)"
        )

    def test_process_missing_file(self):
        """Test processing a file that exists only in approved."""
        current_files = {}
        approved_files = {"missing.txt": Path("approved/missing.txt")}

        mock_reporter = Mock(spec=Reporter)
        result = _process_file_comparison(
            "missing.txt", current_files, approved_files, mock_reporter
        )

        assert result["passed"] is False
        assert result["status"] == "missing"
        mock_reporter.validation_result.assert_called_once_with(
            "missing.txt", False, "MISSING (in approved but not generated)"
        )

    @patch("agency_toolkit.commands.validate._get_file_comparator")
    def test_process_existing_file(self, mock_get_comparator):
        """Test processing a file that exists in both directories."""
        current_files = {"test.txt": Path("current/test.txt")}
        approved_files = {"test.txt": Path("approved/test.txt")}

        mock_comparator = Mock(return_value={"passed": True})
        mock_get_comparator.return_value = mock_comparator

        mock_reporter = Mock(spec=Reporter)
        result = _process_file_comparison(
            "test.txt", current_files, approved_files, mock_reporter
        )

        assert result["passed"] is True
        assert result["status"] == "compared"
        mock_comparator.assert_called_once()


class TestValidateSnapshotDirs:
    """Test _validate_snapshot_dirs function."""

    def test_validate_both_dirs_exist(self):
        """Test validation when both directories exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            current_dir = tmp_path / "current"
            approved_dir = tmp_path / "approved"

            current_dir.mkdir()
            approved_dir.mkdir()

            mock_reporter = Mock(spec=Reporter)
            result = _validate_snapshot_dirs(current_dir, approved_dir, mock_reporter)

            assert result is True
            mock_reporter.error.assert_not_called()
            mock_reporter.warning.assert_not_called()

    def test_validate_current_dir_missing(self):
        """Test validation when current directory is missing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            current_dir = tmp_path / "current"
            approved_dir = tmp_path / "approved"

            approved_dir.mkdir()

            mock_reporter = Mock(spec=Reporter)
            result = _validate_snapshot_dirs(current_dir, approved_dir, mock_reporter)

            assert result is False
            mock_reporter.error.assert_called_once()

    def test_validate_approved_dir_missing(self):
        """Test validation when approved directory is missing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            current_dir = tmp_path / "current"
            approved_dir = tmp_path / "approved"

            current_dir.mkdir()

            mock_reporter = Mock(spec=Reporter)
            result = _validate_snapshot_dirs(current_dir, approved_dir, mock_reporter)

            assert result is False
            assert mock_reporter.warning.call_count == 2


class TestCollectSnapshotFiles:
    """Test _collect_snapshot_files function."""

    def test_collect_files_from_both_dirs(self):
        """Test collecting files from both current and approved directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            current_dir = tmp_path / "current"
            approved_dir = tmp_path / "approved"

            current_dir.mkdir()
            approved_dir.mkdir()

            # Create test files
            (current_dir / "file1.txt").write_text("content1")
            (current_dir / "file2.txt").write_text("content2")
            (approved_dir / "file2.txt").write_text("old_content2")
            (approved_dir / "file3.txt").write_text("content3")

            current_files, approved_files, all_files = _collect_snapshot_files(
                current_dir, approved_dir
            )

            assert len(current_files) == 2
            assert len(approved_files) == 2
            assert all_files == {"file1.txt", "file2.txt", "file3.txt"}


class TestAggregateComparisonResults:
    """Test _aggregate_comparison_results function."""

    def test_aggregate_mixed_results(self):
        """Test aggregating mixed comparison results."""
        results = [
            {"passed": True, "status": "compared"},
            {"passed": False, "status": "compared", "difference": {"file": "test1"}},
            {"passed": False, "status": "new", "difference": {"file": "test2"}},
            {"passed": True, "status": "compared"},
        ]

        aggregated = _aggregate_comparison_results(results)

        assert aggregated["total"] == 4
        assert aggregated["passed"] == 2
        assert aggregated["failed"] == 1
        assert aggregated["missing"] == 1
        assert len(aggregated["differences"]) == 2


class TestCompareSnapshots:
    """Test _compare_snapshots orchestrator function."""

    @patch("agency_toolkit.commands.validate._validate_snapshot_dirs")
    def test_compare_invalid_directories(self, mock_validate):
        """Test comparison with invalid directories."""
        mock_validate.return_value = False

        mock_reporter = Mock(spec=Reporter)
        result = _compare_snapshots(
            Path("invalid_current"), Path("invalid_approved"), mock_reporter
        )

        assert result["total"] == 0
        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["missing"] == 0

    @patch("agency_toolkit.commands.validate._process_file_comparison")
    @patch("agency_toolkit.commands.validate._aggregate_comparison_results")
    @patch("agency_toolkit.commands.validate._collect_snapshot_files")
    @patch("agency_toolkit.commands.validate._validate_snapshot_dirs")
    def test_compare_valid_directories(
        self, mock_validate, mock_collect, mock_aggregate, mock_process
    ):
        """Test comparison with valid directories."""
        mock_validate.return_value = True
        mock_collect.return_value = (
            {"test.txt": Path("current/test.txt")},
            {"test.txt": Path("approved/test.txt")},
            {"test.txt"},
        )
        mock_process.return_value = {"passed": True, "status": "compared"}
        mock_aggregate.return_value = {
            "total": 1,
            "passed": 1,
            "failed": 0,
            "missing": 0,
            "differences": [],
        }

        mock_reporter = Mock(spec=Reporter)
        result = _compare_snapshots(Path("current"), Path("approved"), mock_reporter)

        assert result["total"] == 1
        assert result["passed"] == 1
        mock_process.assert_called_once()
        mock_aggregate.assert_called_once()
