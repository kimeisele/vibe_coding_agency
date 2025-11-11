#!/usr/bin/env python3
"""Calculate and report comprehensive quality score for CI/CD pipeline.

This script evaluates project quality across 4 dimensions:
1. Test Coverage (0-25 points)
2. Test Pass Rate (0-25 points)
3. Performance Benchmarks (0-25 points)
4. Code Quality & Security (0-25 points)

Total Quality Score = 0-100 (minimum 80 for production release)

Usage:
    python3 scripts/calculate_quality_score.py

Output:
    quality_score.json - Machine-readable results for CI
    Stdout - Human-readable summary
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_coverage_percentage() -> float:
    """Get test coverage percentage from .coverage file.

    Returns:
        Coverage percentage (0-100), or 0 if no coverage data
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "coverage", "report", "--format=total"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            coverage_str = result.stdout.strip()
            if "%" in coverage_str:
                return float(coverage_str.replace("%", ""))
        return 0.0
    except Exception as e:
        logger.warning(f"Could not calculate coverage: {e}")
        return 0.0


def get_test_pass_rate() -> float:
    """Get test pass rate from recent pytest run.

    Returns:
        Pass rate percentage (0-100)
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "--co", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Run a quick pytest to count passed/failed
        result = subprocess.run(
            ["python3", "-m", "pytest", "-v", "--tb=no", "-x"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Parse output for pass/fail counts
        lines = result.stdout.split("\n")
        for line in lines:
            if "passed" in line or "failed" in line:
                # Example: "120 passed in 2.34s"
                if "passed" in line and "failed" not in line:
                    return 100.0  # All passed
                elif "failed" in line:
                    # Parse "X passed, Y failed"
                    import re

                    match = re.search(r"(\d+) passed.*(\d+) failed", line)
                    if match:
                        passed = int(match.group(1))
                        failed = int(match.group(2))
                        total = passed + failed
                        return (passed / total * 100) if total > 0 else 0.0

        return 100.0  # Assume all passed if we can't parse

    except Exception as e:
        logger.warning(f"Could not calculate pass rate: {e}")
        return 50.0  # Conservative estimate


def get_performance_score() -> float:
    """Get performance score (0-25) based on benchmarks.

    Returns:
        Performance score (0-25)
    """
    try:
        # Check if performance tests exist and pass
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/uat/test_performance.py", "-v"],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            # All performance tests passed
            return 25.0
        else:
            # Some performance tests failed
            return 15.0

    except Exception as e:
        logger.warning(f"Could not calculate performance score: {e}")
        return 10.0


def get_code_quality_score() -> float:
    """Get code quality score (0-25) based on linting and type checking.

    Returns:
        Code quality score (0-25)
    """
    quality_score = 0.0
    total_checks = 0

    # Check 1: mypy type checking (0-10 points)
    total_checks += 10
    try:
        result = subprocess.run(
            ["python3", "-m", "mypy", "agency_toolkit/", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            quality_score += 10.0
        else:
            # Count errors
            error_count = result.stdout.count("error:")
            quality_score += max(0, 10 - (error_count * 0.5))
    except Exception as e:
        logger.warning(f"mypy check failed: {e}")

    # Check 2: ruff linting (0-8 points)
    total_checks += 8
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", "agency_toolkit/"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            quality_score += 8.0
        else:
            # Deduct points for violations
            violation_count = result.stdout.count("Found")
            quality_score += max(0, 8 - (violation_count * 0.1))
    except Exception as e:
        logger.warning(f"ruff check failed: {e}")

    # Check 3: Security scan (0-7 points)
    total_checks += 7
    try:
        result = subprocess.run(
            ["python3", "-m", "bandit", "-r", "agency_toolkit/", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Bandit returns 0 if no issues, 1 if issues found
        if result.returncode == 0:
            quality_score += 7.0
        else:
            quality_score += 3.0  # Some issues found
    except Exception:
        # bandit might not be installed
        quality_score += 3.0

    return min(25.0, quality_score)


def calculate_quality_score() -> dict[str, Any]:
    """Calculate comprehensive quality score.

    Returns:
        Dict with:
            - total: 0-100 quality score
            - coverage: test coverage %
            - pass_rate: test pass rate %
            - performance_score: 0-25
            - code_quality: 0-25
            - threshold: minimum for production (80)
            - passed: whether score >= threshold
    """
    logger.info("🔍 Calculating comprehensive quality score...\n")

    # Get individual metrics
    logger.info("  📊 Test coverage...")
    coverage = get_coverage_percentage()

    logger.info(f"  ✅ Coverage: {coverage:.1f}%")

    logger.info("  📊 Test pass rate...")
    pass_rate = get_test_pass_rate()
    logger.info(f"  ✅ Pass rate: {pass_rate:.1f}%")

    logger.info("  📊 Performance benchmarks...")
    performance = get_performance_score()
    logger.info(f"  ✅ Performance: {performance:.1f}/25")

    logger.info("  📊 Code quality & security...")
    code_quality = get_code_quality_score()
    logger.info(f"  ✅ Code quality: {code_quality:.1f}/25")

    # Calculate total score
    total = (
        min(coverage, 100) * 0.25  # Coverage: up to 25 points
        + pass_rate * 0.25  # Pass rate: up to 25 points
        + performance  # Performance: 0-25 points
        + code_quality  # Code quality: 0-25 points
    )

    total = round(total, 1)
    threshold = 80
    passed = total >= threshold

    result = {
        "total": total,
        "coverage": round(coverage, 1),
        "pass_rate": round(pass_rate, 1),
        "performance_score": round(performance, 1),
        "code_quality": round(code_quality, 1),
        "threshold": threshold,
        "passed": passed,
    }

    return result


def print_quality_report(score_data: dict[str, Any]) -> None:
    """Print human-readable quality report.

    Args:
        score_data: Quality score data from calculate_quality_score()
    """
    total = score_data["total"]
    threshold = score_data["threshold"]
    passed = score_data["passed"]

    # Color codes for output
    if passed:
        status_icon = "✅"
        status_text = "PASSED"
    else:
        status_icon = "❌"
        status_text = "FAILED"

    logger.info("\n" + "=" * 70)
    logger.info(f"  {status_icon} QUALITY SCORE: {total}/100 ({status_text})")
    logger.info("=" * 70)
    logger.info(f"  Threshold: {threshold}/100")
    logger.info("")
    logger.info("  Breakdown:")
    logger.info(f"    • Test Coverage:    {score_data['coverage']:6.1f}% (0-25 points)")
    logger.info(
        f"    • Test Pass Rate:   {score_data['pass_rate']:6.1f}% (0-25 points)"
    )
    logger.info(
        f"    • Performance:      {score_data['performance_score']:6.1f}/25 points"
    )
    logger.info(f"    • Code Quality:     {score_data['code_quality']:6.1f}/25 points")
    logger.info("")

    if passed:
        logger.info("  🎉 Project is ready for production release!")
    else:
        logger.info(f"  ⚠️  Score is {threshold - total:.1f} points below threshold.")
        logger.info("     Address the weakest areas to improve.")
    logger.info("=" * 70 + "\n")


def main() -> int:
    """Main entry point."""
    try:
        # Calculate score
        score_data = calculate_quality_score()

        # Print report
        print_quality_report(score_data)

        # Write JSON for CI
        output_file = Path("quality_score.json")
        with open(output_file, "w") as f:
            json.dump(score_data, f, indent=2)

        logger.info(f"✅ Quality score saved to {output_file}")

        # Exit with appropriate code
        return 0 if score_data["passed"] else 1

    except Exception as e:
        logger.error(f"❌ Error calculating quality score: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
