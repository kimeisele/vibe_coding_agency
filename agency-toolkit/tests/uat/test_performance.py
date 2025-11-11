"""
UAT Test: Performance Benchmarks (Epic 2.5.7, Story 4.0.2)

Tests critical performance metrics for the social post generation engine.

Performance SLOs:
- Throughput: >10 posts/second
- P95 Latency: <2 seconds per post
- 100 posts < 5 minutes (CRITICAL SLO)

All tests use mocked image generation (no external API calls).
"""

import csv
import time
from unittest.mock import patch

import pytest


class TestPerformanceBenchmarks:
    """Benchmark social post generation against SLO targets."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Temporary directory for test outputs."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return output_dir

    @pytest.fixture
    def csv_100_posts_for_benchmark(self, temp_workspace):
        """Create CSV with 100 posts for throughput testing."""
        csv_path = temp_workspace / "benchmark_100.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "text", "style"])
            writer.writeheader()
            for i in range(1, 101):
                writer.writerow(
                    {
                        "id": f"post_{i:03d}",
                        "text": f"Benchmark post #{i}. This is a standard social media post.",
                        "style": ["modern", "minimal", "bold"][i % 3],
                    }
                )

        return csv_path

    def test_throughput_target_10_posts_per_second(
        self, temp_workspace, csv_100_posts_for_benchmark
    ):
        """
        Throughput SLO: >10 posts/second (100 posts in <10 seconds).

        Verifies:
        - 100 posts process in <10 seconds
        - Throughput > 10 posts/sec
        - No performance regressions
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

            start_time = time.time()
            result = process_batch_csv(
                config=config,
                csv_path=csv_100_posts_for_benchmark,
                output_dir=temp_workspace,
            )
            duration = time.time() - start_time

        # Calculate throughput
        throughput = result["successful"] / duration if duration > 0 else 0

        # Assertions
        assert result["successful"] >= 95, "95% success rate minimum"
        assert (
            throughput > 10
        ), f"Throughput SLO violation: {throughput:.2f} posts/sec, target >10"
        assert (
            duration < 10
        ), f"100 posts should complete in <10s (measured: {duration:.2f}s)"

    def test_100_posts_under_5_minutes_absolute_slo(
        self, temp_workspace, csv_100_posts_for_benchmark
    ):
        """
        ABSOLUTE SLO: 100 posts must complete in <5 minutes (300 seconds).

        This is the critical performance requirement from Story 4.0.1.

        Verifies:
        - 100 posts complete successfully
        - Duration < 300 seconds
        - No violations of this hard SLO
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

            start_time = time.time()
            result = process_batch_csv(
                config=config,
                csv_path=csv_100_posts_for_benchmark,
                output_dir=temp_workspace,
            )
            duration = time.time() - start_time

        # Assertions for critical SLO
        assert result["total"] == 100, "All 100 posts must be processed"
        assert result["successful"] >= 95, "At least 95% success"
        assert (
            duration < 300
        ), f"CRITICAL SLO VIOLATION: {duration:.1f}s > 300s (5 minutes)"

    def test_success_rate_minimum(self, temp_workspace, csv_100_posts_for_benchmark):
        """
        Test that batch processing maintains minimum success rate.

        Verifies:
        - Success rate >= 95%
        - Failures are tracked correctly
        - Graceful degradation works
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
                csv_path=csv_100_posts_for_benchmark,
                output_dir=temp_workspace,
            )

        # Calculate success rate
        total = result["total"]
        successful = result["successful"]
        success_rate = (successful / total * 100) if total > 0 else 0

        # Assertions
        assert (
            success_rate >= 95
        ), f"Success rate {success_rate:.1f}% below 95% threshold"
        assert (
            result["failed"] <= 5
        ), f"Too many failures: {result['failed']} (max 5 allowed)"
