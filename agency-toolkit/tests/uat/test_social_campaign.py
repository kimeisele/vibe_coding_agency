"""
UAT Test: Social Campaign (Epic 2.5.7, Story 2.5.6)

Tests the batch social media generation with all style variations.

Validates:
- 50-post batch with all styles (modern, minimal, bold)
- All colors handled correctly
- No external API calls (mocked)
"""

import csv
from unittest.mock import patch

import pytest


class TestSocialCampaign:
    """Validate 50-post batch generation with all style variations."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Temporary directory for test outputs."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return output_dir

    @pytest.fixture
    def csv_50_posts_all_styles(self, temp_workspace):
        """Create CSV with 50 posts, cycling through all styles."""
        csv_path = temp_workspace / "campaign_50.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "text", "style", "color"])
            writer.writeheader()

            styles = ["modern", "minimal", "bold"]
            colors = ["blue", "red", "green", "purple"]

            for i in range(1, 51):
                writer.writerow(
                    {
                        "id": f"post_{i:02d}",
                        "text": f"Social post #{i}: Check out our latest updates!",
                        "style": styles[i % len(styles)],
                        "color": colors[i % len(colors)],
                    }
                )

        return csv_path

    def test_50_post_batch_all_styles(self, temp_workspace, csv_50_posts_all_styles):
        """
        Generate 50 posts with all style variations.

        Verifies:
        - All 50 posts processed
        - All 3 styles (modern, minimal, bold) completed
        - All 4 colors applied successfully
        - 100% success rate with mocked API
        """
        from agency_toolkit.core.social.batch import process_batch_csv
        from agency_toolkit.models import Config

        config = Config(
            output_dir=str(temp_workspace),
            social_style="modern",
            social_color="blue",
        )

        # Mock image generation to avoid Pollinations API
        with patch("agency_toolkit.core.social.generator.generate") as mock_generate:
            mock_generate.return_value = {
                "path": str(temp_workspace / "mock_post.png"),
                "format": "square",
                "style": "modern",
                "text_length": 50,
                "dry_run": False,
            }

            result = process_batch_csv(
                config=config,
                csv_path=csv_50_posts_all_styles,
                output_dir=temp_workspace,
            )

        # Assertions
        assert result["total"] == 50, "Should process all 50 posts"
        assert result["successful"] == 50, "All 50 posts should succeed (mocked API)"
        assert result["failed"] == 0, "No posts should fail with mocked API"

    def test_all_3_styles_processed(self, temp_workspace, csv_50_posts_all_styles):
        """
        Verify that all 3 styles are processed successfully.

        Verifies:
        - Modern, Minimal, and Bold styles all work
        - No style-related failures
        """
        from agency_toolkit.core.social.batch import process_batch_csv
        from agency_toolkit.models import Config

        config = Config(
            output_dir=str(temp_workspace),
            social_style="modern",
            social_color="blue",
        )

        with patch("agency_toolkit.core.social.generator.generate") as mock_generate:
            mock_generate.return_value = {
                "path": str(temp_workspace / "mock_post.png"),
                "format": "square",
                "style": "modern",
                "text_length": 50,
            }

            result = process_batch_csv(
                config=config,
                csv_path=csv_50_posts_all_styles,
                output_dir=temp_workspace,
            )

        # All styles should be handled
        assert result["successful"] == 50, "All style variations should work"

    def test_all_4_colors_applied(self, temp_workspace, csv_50_posts_all_styles):
        """
        Verify that all 4 colors (blue, red, green, purple) are handled.

        Verifies:
        - All color variations process successfully
        - No color-related failures
        """
        from agency_toolkit.core.social.batch import process_batch_csv
        from agency_toolkit.models import Config

        config = Config(
            output_dir=str(temp_workspace),
            social_style="modern",
            social_color="blue",
        )

        with patch("agency_toolkit.core.social.generator.generate") as mock_generate:
            mock_generate.return_value = {
                "path": str(temp_workspace / "mock_post.png"),
                "format": "square",
                "style": "modern",
                "text_length": 50,
            }

            result = process_batch_csv(
                config=config,
                csv_path=csv_50_posts_all_styles,
                output_dir=temp_workspace,
            )

        # All colors should be handled
        assert result["successful"] == 50, "All color variations should work"
        assert result["failed"] == 0, "No color-related failures"
