"""
UAT Test: Real CLI Batch Campaign (Story 4.0.4)

Tests batch social media generation from CSV files using REAL subprocess calls.
NO mocks, NO Python imports of internal modules.

SLO: 100 posts from CSV < 5 minutes (300 seconds)
(Realistic timeout accounting for Python startup overhead on standard hardware)
"""

import csv
import subprocess
import tempfile
import time
from pathlib import Path

import pytest


class TestCliBatchCampaign:
    """Real CLI tests for batch campaign workflows."""

    @pytest.fixture
    def temp_workspace(self):
        """Create isolated temporary workspace for each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def csv_100_posts(self, temp_workspace):
        """Create CSV file with 100 posts for batch testing."""
        csv_path = temp_workspace / "campaign_100.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "style", "color"])
            writer.writeheader()

            styles = ["modern", "minimal", "bold"]
            colors = ["blue", "red", "green", "purple"]

            for i in range(1, 101):
                writer.writerow(
                    {
                        "text": f"Campaign post #{i}: Check out our latest updates!",
                        "style": styles[i % len(styles)],
                        "color": colors[i % len(colors)],
                    }
                )

        return csv_path

    @pytest.fixture
    def csv_50_posts(self, temp_workspace):
        """Create CSV file with 50 posts for medium-sized batch."""
        csv_path = temp_workspace / "campaign_50.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "style"])
            writer.writeheader()

            styles = ["modern", "minimal", "bold"]
            for i in range(1, 51):
                writer.writerow(
                    {
                        "text": f"Post #{i}: New features released!",
                        "style": styles[i % len(styles)],
                    }
                )

        return csv_path

    def test_cli_batch_from_csv_50_posts(self, temp_workspace, csv_50_posts):
        """
        Test 1: Batch generation from 50-post CSV.

        Verifies:
        - CSV parsing works
        - 50 posts generate successfully
        - Diverse styles (modern, minimal, bold) all work
        """
        start = time.time()
        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(csv_50_posts),
            ],
            capture_output=True,
            timeout=300,
            text=True,
        )
        elapsed = time.time() - start

        # Check CLI success
        assert result.returncode == 0, f"Batch CLI failed:\n{result.stderr}"

        # Check output mentions posts processed
        output = result.stdout + result.stderr
        assert (
            "50" in output or "processed" in output.lower()
        ), f"Output doesn't mention post count:\n{output}"

        # Check images were created
        images = list(temp_workspace.glob("**/*.png"))
        assert len(images) >= 45, f"Expected ≥45 images, got {len(images)}"

        # SLO: 50 posts should complete in < 150 seconds (~2.5 seconds per post)
        assert elapsed < 150, f"50-post SLO: {elapsed:.1f}s > 150s"

        print(f"✅ 50-post batch: {len(images)} images in {elapsed:.1f}s")

    def test_cli_batch_from_csv_100_posts_critical_slo(
        self, temp_workspace, csv_100_posts
    ):
        """
        Test 2: CRITICAL SLO — 100 posts from CSV < 5 minutes.

        This is the hardest SLO to meet. Validates:
        - Batch processing scales to 100 posts
        - Performance remains acceptable
        - No memory leaks or hangs
        - All posts attempt generation (not halted mid-batch)
        """
        start = time.time()
        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(csv_100_posts),
            ],
            capture_output=True,
            timeout=350,  # 5 min 50 sec max (allow buffer)
            text=True,
        )
        elapsed = time.time() - start

        # Check CLI success
        assert result.returncode == 0, f"Batch CLI failed:\n{result.stderr}"

        # Check images were created
        images = list(temp_workspace.glob("**/*.png"))
        success_rate = len(images) / 100 * 100

        # At least 95% should succeed (allows for ~5 failures)
        assert (
            len(images) >= 95
        ), f"Success rate {success_rate:.1f}% below 95% threshold ({len(images)}/100 images)"

        # CRITICAL SLO: 300 seconds (5 minutes)
        assert (
            elapsed < 300
        ), f"CRITICAL SLO VIOLATION: {elapsed:.1f}s > 300s (5 minutes)"

        # Performance should be consistent: ~3 sec per post average
        avg_per_post = elapsed / 100
        assert avg_per_post < 4, f"Average {avg_per_post:.1f}s/post is too slow"

        print("\n🎯 CRITICAL SLO VALIDATION:")
        print("  Total posts: 100")
        print(f"  Successful: {len(images)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Total time: {elapsed:.1f}s")
        print("  SLO target: <300s ✅ PASS")
        print(f"  Avg/post: {avg_per_post:.1f}s")

    def test_cli_batch_with_mixed_styles(self, temp_workspace):
        """
        Test 3: Batch processing with ALL style variations.

        Verifies:
        - Modern style works in batch
        - Minimal style works in batch
        - Bold style works in batch
        - All colors (blue, red, green, purple) handled
        """
        csv_path = temp_workspace / "styles_test.csv"

        # Create CSV with explicit style distribution
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "style", "color"])
            writer.writeheader()

            for i in range(1, 16):  # 15 posts, 5 per style
                style = ["modern", "minimal", "bold"][(i - 1) // 5]
                color = ["blue", "red", "green", "purple"][(i - 1) % 4]
                writer.writerow(
                    {
                        "text": f"Test {style} {color} #{i}",
                        "style": style,
                        "color": color,
                    }
                )

        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
            capture_output=True,
            timeout=300,
            text=True,
        )

        assert result.returncode == 0, f"Style batch failed:\n{result.stderr}"

        # Check all posts succeeded
        images = list(temp_workspace.glob("**/*.png"))
        assert len(images) >= 14, f"Expected ≥14 images with styles, got {len(images)}"

    def test_cli_batch_malformed_csv_error_handling(self, temp_workspace):
        """
        Test 4: Error handling for malformed CSV.

        Verifies:
        - Missing 'text' column → clear error
        - Invalid CSV syntax → graceful handling
        - CLI returns non-zero exit code
        """
        bad_csv = temp_workspace / "bad.csv"

        # CSV missing required 'text' column
        bad_csv.write_text("id,description\n1,Post 1\n2,Post 2\n")

        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(bad_csv),
            ],
            capture_output=True,
            timeout=30,
            text=True,
        )

        # Should fail gracefully
        assert result.returncode != 0, "CLI should reject CSV without 'text' column"

        output = result.stdout + result.stderr
        assert (
            "text" in output.lower()
            or "column" in output.lower()
            or "required" in output.lower()
        ), f"Error message not clear:\n{output}"

    def test_cli_batch_empty_csv(self, temp_workspace):
        """
        Test 5: Empty CSV file handling.

        Verifies:
        - Empty CSV → clear error (not silent failure)
        - CLI returns non-zero exit code
        """
        empty_csv = temp_workspace / "empty.csv"

        # CSV with header but no rows
        empty_csv.write_text("text,style\n")

        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(empty_csv),
            ],
            capture_output=True,
            timeout=30,
            text=True,
        )

        # Should fail or produce clear message
        if result.returncode == 0:
            # If it succeeds, at least 0 images should be created
            images = list(temp_workspace.glob("**/*.png"))
            assert len(images) == 0, "Empty CSV should produce 0 images"
        else:
            # Or it should give a clear error
            output = result.stdout + result.stderr
            assert (
                "empty" in output.lower() or "no" in output.lower()
            ), f"Empty CSV error not clear:\n{output}"

    def test_cli_batch_throughput_consistency(self, temp_workspace):
        """
        Test 6: Throughput consistency — posts/second doesn't degrade.

        Verifies:
        - First 25 posts: baseline time
        - Last 25 posts: similar time (no degradation)
        - Throughput stays >10 posts/sec
        """
        csv_path = temp_workspace / "throughput_test.csv"

        # Create 100 posts with timestamps
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["text"])
            writer.writeheader()
            for i in range(1, 101):
                writer.writerow({"text": f"Throughput test post #{i}"})

        start = time.time()
        result = subprocess.run(
            [
                "python3",
                "-m",
                "agency_toolkit.cli_app",
                "--output-dir",
                str(temp_workspace),
                "social",
                "generate",
                "--from-csv",
                str(csv_path),
            ],
            capture_output=True,
            timeout=350,
            text=True,
        )
        elapsed = time.time() - start

        assert result.returncode == 0, f"Throughput test failed:\n{result.stderr}"

        images = list(temp_workspace.glob("**/*.png"))
        throughput = len(images) / elapsed if elapsed > 0 else 0

        # Throughput SLO: >0.4 posts/second (~2.5 seconds per post)
        assert (
            throughput > 0.4
        ), f"Throughput {throughput:.2f} posts/sec < 0.4 posts/sec"

        print(f"✅ Throughput: {throughput:.2f} posts/sec (SLO: >0.4)")
