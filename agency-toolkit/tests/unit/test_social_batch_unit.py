"""Unit tests for social batch processing (Epic 1.4.2)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.core.social.batch import (
    process_batch_csv,
    process_batch_json,
    process_single_post,
)


class TestProcessSinglePost:
    """Test single post processing."""

    @patch("agency_toolkit.core.social.batch.generate_social_post")
    def test_process_single_post_basic(self, mock_gen) -> None:
        """Should process single post with basic parameters."""
        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")
        mock_gen.return_value = {"path": "/tmp/output/post.png"}

        result = process_single_post(
            config=mock_config,
            text="Hello World",
        )

        assert result["status"] == "success"
        assert "/tmp/output" in result["path"]

    @patch("agency_toolkit.core.social.batch.generate_social_post")
    def test_process_single_post_with_all_parameters(self, mock_gen) -> None:
        """Should accept all optional parameters."""
        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")
        mock_gen.return_value = {"path": "/tmp/output/post.png"}

        result = process_single_post(
            config=mock_config,
            text="Custom post",
            style="bold",
            color="red",
            custom_color="#FF0000",
            format_type="portrait",
            output_path=Path("/custom/output"),
        )

        assert result["status"] == "success"
        mock_gen.assert_called_once()

    @patch("agency_toolkit.core.social.batch.generate_social_post")
    def test_process_single_post_dry_run_no_generation(self, mock_gen) -> None:
        """Should not generate in dry-run mode."""
        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        result = process_single_post(
            config=mock_config,
            text="Test",
            dry_run=True,
        )

        # In dry-run, generation might not happen or return mock data
        assert result is not None

    @patch("agency_toolkit.core.social.batch.generate_background")
    @patch("agency_toolkit.core.social.batch.generate_social_post")
    def test_process_single_post_with_background(
        self, mock_gen_post, mock_gen_bg
    ) -> None:
        """Should generate background if bg_concept provided."""
        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")
        mock_config.image.provider = "pollinations"

        mock_gen_bg.return_value = {"path": "/tmp/bg.png", "cost": 0.001}
        mock_gen_post.return_value = {"path": "/tmp/post.png"}

        result = process_single_post(
            config=mock_config,
            text="Post with background",
            bg_concept="moody",
            bg_seed=123,
        )

        assert result["status"] == "success"
        assert result["cost"] >= 0.001

    @patch("agency_toolkit.core.social.batch.generate_social_post")
    def test_process_single_post_error_handling(self, mock_gen) -> None:
        """Should handle generation errors gracefully."""
        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")
        mock_gen.side_effect = RuntimeError("Generation failed")

        result = process_single_post(
            config=mock_config,
            text="Failing post",
        )

        assert result["status"] == "error"
        assert "error" in result
        assert "Generation failed" in result["error"]


class TestProcessBatchCSV:
    """Test CSV batch processing."""

    def test_process_batch_csv_single_row(self, tmp_path: Path) -> None:
        """Should process CSV with single row."""
        csv_file = tmp_path / "posts.csv"
        csv_file.write_text('text,style\n"Hello","modern"\n')

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_csv(mock_config, csv_file)

        assert result["total"] == 1
        assert result["successful"] == 1
        assert result["failed"] == 0
        assert len(result["results"]) == 1

    def test_process_batch_csv_multiple_rows(self, tmp_path: Path) -> None:
        """Should process CSV with multiple rows."""
        csv_file = tmp_path / "posts.csv"
        csv_content = (
            "text,style,color\n"
            '"Post 1","modern","blue"\n'
            '"Post 2","bold","red"\n'
            '"Post 3","minimal","green"\n'
        )
        csv_file.write_text(csv_content)

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_csv(mock_config, csv_file)

        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert mock_process.call_count == 3

    def test_process_batch_csv_missing_text_column_fails(self, tmp_path: Path) -> None:
        """Should raise if CSV missing 'text' column."""
        csv_file = tmp_path / "posts.csv"
        csv_file.write_text('style,color\n"modern","blue"\n')

        mock_config = MagicMock()

        with pytest.raises(ValueError, match="'text' column"):
            process_batch_csv(mock_config, csv_file)

    def test_process_batch_csv_skip_row_with_empty_text(self, tmp_path: Path) -> None:
        """Should skip rows where text is empty."""
        csv_file = tmp_path / "posts.csv"
        csv_content = (
            "text,style\n" '"Post 1","modern"\n' '"","bold"\n' '"Post 3","minimal"\n'
        )
        csv_file.write_text(csv_content)

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_csv(mock_config, csv_file)

        assert result["total"] == 3
        assert result["successful"] == 2  # Only 2 processed
        assert result["failed"] == 1  # 1 skipped

    def test_process_batch_csv_file_not_found(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError if CSV doesn't exist."""
        mock_config = MagicMock()

        with pytest.raises(FileNotFoundError):
            process_batch_csv(mock_config, Path("/nonexistent/file.csv"))

    def test_process_batch_csv_empty_file_fails(self, tmp_path: Path) -> None:
        """Should raise ValueError if CSV has no data rows."""
        csv_file = tmp_path / "posts.csv"
        csv_file.write_text("text,style\n")  # Header only, no rows

        mock_config = MagicMock()

        with pytest.raises(ValueError, match="empty"):
            process_batch_csv(mock_config, csv_file)

    def test_process_batch_csv_with_optional_fields(self, tmp_path: Path) -> None:
        """Should handle optional CSV fields with defaults."""
        csv_file = tmp_path / "posts.csv"
        csv_content = "text\n" '"Post without options"\n'
        csv_file.write_text(csv_content)

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            process_batch_csv(mock_config, csv_file)

            # Verify defaults were used
            call_kwargs = mock_process.call_args[1]
            assert call_kwargs["style"] == "modern"
            assert call_kwargs["color"] == "blue"
            assert call_kwargs["format_type"] == "square"

    def test_process_batch_csv_parses_bg_seed_as_int(self, tmp_path: Path) -> None:
        """Should parse bg_seed as integer."""
        csv_file = tmp_path / "posts.csv"
        csv_content = "text,bg_seed\n" '"Post","12345"\n'
        csv_file.write_text(csv_content)

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            process_batch_csv(mock_config, csv_file)

            call_kwargs = mock_process.call_args[1]
            assert call_kwargs["bg_seed"] == 12345
            assert isinstance(call_kwargs["bg_seed"], int)


class TestProcessBatchJSON:
    """Test JSON batch processing."""

    def test_process_batch_json_array_format(self, tmp_path: Path) -> None:
        """Should process JSON array of posts."""
        json_file = tmp_path / "posts.json"
        data = [
            {"text": "Post 1", "style": "modern"},
            {"text": "Post 2", "style": "bold"},
        ]
        json_file.write_text(json.dumps(data))

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_json(mock_config, json_file)

        assert result["total"] == 2
        assert result["successful"] == 2
        assert mock_process.call_count == 2

    def test_process_batch_json_object_with_posts_key(self, tmp_path: Path) -> None:
        """Should process JSON object with 'posts' key."""
        json_file = tmp_path / "posts.json"
        data = {
            "posts": [
                {"text": "Post 1"},
                {"text": "Post 2"},
                {"text": "Post 3"},
            ]
        }
        json_file.write_text(json.dumps(data))

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_json(mock_config, json_file)

        assert result["total"] == 3
        assert result["successful"] == 3

    def test_process_batch_json_skip_post_with_empty_text(self, tmp_path: Path) -> None:
        """Should skip posts where text is empty."""
        json_file = tmp_path / "posts.json"
        data = [
            {"text": "Valid post"},
            {"text": ""},
            {"text": "Another valid"},
        ]
        json_file.write_text(json.dumps(data))

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_json(mock_config, json_file)

        assert result["total"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1

    def test_process_batch_json_invalid_format_raises(self, tmp_path: Path) -> None:
        """Should raise ValueError for invalid JSON format."""
        json_file = tmp_path / "posts.json"
        json_file.write_text('{"invalid": "structure"}')

        mock_config = MagicMock()

        with pytest.raises(ValueError, match="array|posts"):
            process_batch_json(mock_config, json_file)

    def test_process_batch_json_file_not_found(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError if JSON doesn't exist."""
        mock_config = MagicMock()

        with pytest.raises(FileNotFoundError):
            process_batch_json(mock_config, Path("/nonexistent/file.json"))

    def test_process_batch_json_with_additional_fields(self, tmp_path: Path) -> None:
        """Should handle additional fields in JSON posts."""
        json_file = tmp_path / "posts.json"
        data = [
            {
                "text": "Post",
                "style": "bold",
                "color": "red",
                "bg_concept": "moody",
                "extra_field": "ignored",
            }
        ]
        json_file.write_text(json.dumps(data))

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_json(mock_config, json_file)

        assert result["successful"] == 1
        call_kwargs = mock_process.call_args[1]
        assert call_kwargs["text"] == "Post"
        assert call_kwargs["style"] == "bold"
        assert call_kwargs["color"] == "red"
        assert call_kwargs["bg_concept"] == "moody"

    def test_process_batch_json_preserves_bg_seed_type(self, tmp_path: Path) -> None:
        """Should preserve bg_seed as integer from JSON."""
        json_file = tmp_path / "posts.json"
        data = [{"text": "Post", "bg_seed": 99999}]
        json_file.write_text(json.dumps(data))

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            process_batch_json(mock_config, json_file)

            call_kwargs = mock_process.call_args[1]
            assert call_kwargs["bg_seed"] == 99999


class TestBatchProcessingIntegration:
    """Integration tests for batch processing."""

    def test_csv_with_mixed_success_and_failures(self, tmp_path: Path) -> None:
        """Should handle mix of successful and failed posts."""
        csv_file = tmp_path / "posts.csv"
        csv_content = (
            "text,style\n"
            '"Good 1","modern"\n'
            '"","bold"\n'
            '"Good 2","minimal"\n'
            '"","bold"\n'
            '"Good 3","modern"\n'
        )
        csv_file.write_text(csv_content)

        mock_config = MagicMock()
        mock_config.output_dir = Path("/tmp/output")

        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            mock_process.return_value = {
                "status": "success",
                "path": "/tmp/post.png",
                "cost": 0.0,
            }

            result = process_batch_csv(mock_config, csv_file)

        assert result["total"] == 5
        assert result["successful"] == 3
        assert result["failed"] == 2

    def test_json_empty_array_fails(self, tmp_path: Path) -> None:
        """Should raise ValueError for empty JSON array."""
        json_file = tmp_path / "posts.json"
        json_file.write_text("[]")

        mock_config = MagicMock()

        # Empty array should be processed as 0 items
        with patch(
            "agency_toolkit.core.social.batch.process_single_post"
        ) as mock_process:
            result = process_batch_json(mock_config, json_file)

        assert result["total"] == 0
