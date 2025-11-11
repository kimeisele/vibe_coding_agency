"""Integration tests for batch social media post generation (WU 9.2)."""

from pathlib import Path

from typer.testing import CliRunner

from agency_toolkit.cli_app import app

runner = CliRunner()


class TestSocialBatch:
    """Test batch social post generation."""

    def test_social_from_csv_generates_multiple_files(self, tmp_path, monkeypatch):
        """Test that --from-csv generates all posts from CSV file."""
        # Setup
        output_dir = tmp_path / "output"
        csv_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.csv"

        monkeypatch.chdir(tmp_path)

        # Execute
        result = runner.invoke(
            app,
            [
                "--output-dir",
                str(output_dir),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert
        assert result.exit_code == 0, f"Failed with: {result.stdout}"
        assert "Total: 4" in result.stdout
        assert "Successful: 4" in result.stdout

        # Check that 4 image files were created
        social_dir = output_dir / "social"
        assert social_dir.exists()
        image_files = list(social_dir.glob("*.png"))
        assert len(image_files) == 4

    def test_social_from_json_generates_multiple_files(self, tmp_path, monkeypatch):
        """Test that --from-json generates all posts from JSON file."""
        # Setup
        output_dir = tmp_path / "output"
        json_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.json"

        monkeypatch.chdir(tmp_path)

        # Execute
        result = runner.invoke(
            app,
            [
                "--output-dir",
                str(output_dir),
                "social",
                "generate",
                "--from-json",
                str(json_path),
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "Total: 3" in result.stdout
        assert "Successful: 3" in result.stdout

        # Check that 3 image files were created
        social_dir = output_dir / "social"
        assert social_dir.exists()
        image_files = list(social_dir.glob("*.png"))
        assert len(image_files) == 3

    def test_social_batch_handles_missing_columns(self, tmp_path, monkeypatch):
        """Test that batch processing handles missing optional columns."""
        # Setup: CSV with only required 'text' column
        csv_path = tmp_path / "minimal.csv"
        csv_path.write_text('text\n"Simple Post"\n"Another Post"')
        output_dir = tmp_path / "output"

        monkeypatch.chdir(tmp_path)

        # Execute
        result = runner.invoke(
            app,
            [
                "--output-dir",
                str(output_dir),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert: Should succeed using default values
        assert result.exit_code == 0
        assert "Total: 2" in result.stdout
        assert "Successful: 2" in result.stdout

        social_dir = output_dir / "social"
        image_files = list(social_dir.glob("*.png"))
        assert len(image_files) == 2

    def test_social_batch_fails_with_conflicting_args(self, tmp_path):
        """Test that using --text with --from-csv fails with clear error."""
        csv_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.csv"

        # Execute: Try to use both --text and --from-csv
        result = runner.invoke(
            app,
            [
                "social",
                "generate",
                "Hello",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert: Should fail with informative error
        assert result.exit_code == 1
        assert "Cannot use --text with --from-csv" in result.stdout

    def test_social_batch_fails_with_both_csv_and_json(self, tmp_path):
        """Test that using both --from-csv and --from-json fails."""
        csv_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.csv"
        json_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.json"

        # Execute
        result = runner.invoke(
            app,
            [
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
                "--from-json",
                str(json_path),
            ],
        )

        # Assert
        assert result.exit_code == 1
        assert "Cannot use both --from-csv and --from-json" in result.stdout

    def test_social_batch_csv_dry_run(self, tmp_path, monkeypatch):
        """Test that --dry-run with --from-csv doesn't create files."""
        csv_path = Path(__file__).parent.parent / "fixtures" / "campaign_posts.csv"
        output_dir = tmp_path / "output"

        monkeypatch.chdir(tmp_path)

        # Execute
        result = runner.invoke(
            app,
            [
                "--output-dir",
                str(output_dir),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
                "--dry-run",
            ],
        )

        # Assert
        assert result.exit_code == 0
        assert "Batch complete" in result.stdout

        # No files should be created
        social_dir = output_dir / "social"
        if social_dir.exists():
            image_files = list(social_dir.glob("*.png"))
            assert len(image_files) == 0

    def test_social_batch_handles_empty_csv(self, tmp_path):
        """Test that empty CSV file fails gracefully."""
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("text\n")

        # Execute
        result = runner.invoke(
            app,
            [
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert
        assert result.exit_code == 1
        assert "CSV file is empty" in result.stdout

    def test_social_batch_csv_missing_text_column(self, tmp_path):
        """Test that CSV without 'text' column fails."""
        csv_path = tmp_path / "invalid.csv"
        csv_path.write_text("style,color\nbold,blue\n")

        # Execute
        result = runner.invoke(
            app,
            [
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert
        assert result.exit_code == 1
        assert "CSV file must have a 'text' column." in result.stdout

    def test_social_batch_json_invalid_format(self, tmp_path):
        """Test that non-array JSON fails gracefully."""
        json_path = tmp_path / "invalid.json"
        json_path.write_text('{"text": "Not an array"}')

        # Execute
        result = runner.invoke(
            app,
            [
                "social",
                "generate",
                "--from-json",
                str(json_path),
            ],
        )

        # Assert
        assert result.exit_code == 1
        assert "must be an array" in result.stdout

    def test_batch_skips_row_with_invalid_data(self, tmp_path, monkeypatch):
        """Test that batch processing skips invalid rows and continues with valid ones."""
        # Setup: CSV with 1 invalid style + 3 valid posts
        output_dir = tmp_path / "output"
        csv_path = tmp_path / "posts_with_invalid.csv"
        csv_path.write_text(
            "text,style,color,format\n"
            '"Valid Post 1","modern","blue","square"\n'
            '"Invalid Style Post","mnodern","red","square"\n'  # typo: mnodern
            '"Valid Post 2","bold","green","landscape"\n'
            '"Valid Post 3","minimal","purple","story"\n'
        )

        monkeypatch.chdir(tmp_path)

        # Execute
        result = runner.invoke(
            app,
            [
                "--output-dir",
                str(output_dir),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
        )

        # Assert: Should succeed with 3/4 posts (skipping invalid style)
        assert result.exit_code == 0
        assert "Total: 4" in result.stdout
        assert "Successful: 3" in result.stdout
        assert "Failed: 1" in result.stdout

        # Verify only 3 valid image files were created
        social_dir = output_dir / "social"
        assert social_dir.exists()
        image_files = list(social_dir.glob("*.png"))
        assert len(image_files) == 3
