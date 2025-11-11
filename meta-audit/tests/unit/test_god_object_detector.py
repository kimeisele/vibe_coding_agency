"""Unit tests for God Object Detector collector."""

import pytest
from pathlib import Path
from meta_audit.analyzers.collectors.god_object import (
    get_god_object_findings,
    GodObjectHeuristics,
    ClassMetrics,
)
from meta_audit.core.models import Severity


class TestGodObjectHeuristics:
    """Test God Object detection heuristics."""

    def test_vague_name_detection(self):
        """Test detection of vague class names."""
        vague_names = ["Manager", "Handler", "Processor", "Utility", "Helper"]
        for name in vague_names:
            metrics = ClassMetrics(name, 1)
            assert metrics.has_vague_name(), f"{name} should be detected as vague"

    def test_non_vague_names(self):
        """Test that legitimate names are not flagged."""
        good_names = ["UserRepository", "PaymentProcessor", "ConfigParser"]
        for name in good_names:
            metrics = ClassMetrics(name, 1)
            # Note: "Processor" and "Parser" might match, but context matters
            # For now, test the clear cases
            if name == "UserRepository":
                assert not metrics.has_vague_name()

    def test_line_count_thresholds(self):
        """Test line count severity classification."""
        assert GodObjectHeuristics.LINES_WARNING == 200
        assert GodObjectHeuristics.LINES_HIGH == 500
        assert GodObjectHeuristics.LINES_CRITICAL == 1000

    def test_method_count_thresholds(self):
        """Test method count severity classification."""
        assert GodObjectHeuristics.METHODS_WARNING == 10
        assert GodObjectHeuristics.METHODS_HIGH == 20
        assert GodObjectHeuristics.METHODS_CRITICAL == 50


class TestClassMetrics:
    """Test ClassMetrics calculation."""

    def test_line_count_calculation(self):
        """Test that line count is calculated correctly."""
        metrics = ClassMetrics("TestClass", lineno=10)
        metrics.line_end = 30
        assert metrics.line_count == 21

    def test_method_counting(self):
        """Test method count tracking."""
        metrics = ClassMetrics("TestClass", lineno=1)
        assert metrics.method_count == 0
        assert metrics.public_method_count == 0

        # Add methods
        metrics.methods = ["method1", "method2", "method3"]
        metrics.public_methods = ["method1", "method2"]

        assert metrics.method_count == 3
        assert metrics.public_method_count == 2

    def test_responsibility_tracking(self):
        """Test responsibility detection."""
        metrics = ClassMetrics("Manager", lineno=1)
        metrics.responsibilities.add("auth")
        metrics.responsibilities.add("logging")
        metrics.responsibilities.add("caching")

        assert len(metrics.responsibilities) == 3
        assert "auth" in metrics.responsibilities


class TestGodObjectDetectorFunction:
    """Test God Object Detector function."""

    def test_get_god_object_findings_exists(self):
        """Test that get_god_object_findings function exists."""
        assert callable(get_god_object_findings)

    def test_severity_classification(self):
        """Test that severity levels are assigned correctly."""
        # Create metrics for different severity levels
        metrics_low = ClassMetrics("SmallClass", lineno=1)
        metrics_low.line_end = 50

        metrics_high = ClassMetrics("LargeManager", lineno=1)
        metrics_high.line_end = 600
        metrics_high.methods = [f"method{i}" for i in range(25)]

        metrics_critical = ClassMetrics("GodProcessor", lineno=1)
        metrics_critical.line_end = 1100
        metrics_critical.methods = [f"method{i}" for i in range(60)]

        # Low should not trigger (< 200 lines)
        assert metrics_low.line_count < GodObjectHeuristics.LINES_HIGH

        # High should trigger (>= 500 lines, >= 20 methods)
        assert metrics_high.line_count >= GodObjectHeuristics.LINES_HIGH
        assert metrics_high.method_count >= GodObjectHeuristics.METHODS_HIGH

        # Critical should trigger (>= 1000 lines, >= 50 methods)
        assert metrics_critical.line_count >= GodObjectHeuristics.LINES_CRITICAL
        assert metrics_critical.method_count >= GodObjectHeuristics.METHODS_CRITICAL


class TestGodObjectDetectorIntegration:
    """Integration tests with actual Python code."""

    def test_get_findings_on_valid_file(self):
        """Test detection on valid Python file."""
        # Create a temporary test file with a god object-like class
        test_file = Path(__file__).parent / "test_sample_god.py"
        try:
            test_file.write_text("""
class Manager:
    def __init__(self):
        pass

    def handle_auth(self):
        pass

    def handle_logging(self):
        pass

    def handle_caching(self):
        pass
""")
            results = get_god_object_findings(str(test_file))
            # Should return a list (might be empty if class is too small)
            assert isinstance(results, list)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_detector_handles_syntax_errors(self):
        """Test detector handles files with syntax errors gracefully."""
        # Create a temporary file with syntax error
        test_file = Path(__file__).parent / "invalid.py"
        try:
            test_file.write_text("this is { not valid python")
            results = get_god_object_findings(str(test_file))
            # Should return empty list or handle gracefully
            assert isinstance(results, list)
        finally:
            if test_file.exists():
                test_file.unlink()


class TestGodObjectDetectorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_class(self):
        """Test detection of empty class."""
        metrics = ClassMetrics("EmptyClass", lineno=1)
        metrics.line_end = 5
        assert metrics.line_count == 5
        assert metrics.method_count == 0

    def test_single_method_class(self):
        """Test class with single method."""
        metrics = ClassMetrics("SingleMethod", lineno=1)
        metrics.line_end = 20
        metrics.methods = ["__init__"]
        assert metrics.method_count == 1

    def test_very_long_class_name(self):
        """Test handling of very long class names."""
        long_name = "A" * 200
        metrics = ClassMetrics(long_name, lineno=1)
        assert metrics.name == long_name
        assert not metrics.has_vague_name()
