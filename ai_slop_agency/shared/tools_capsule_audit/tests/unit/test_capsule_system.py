"""Unit tests for the capsule system (ProjectCapsule, batch processing, reports)."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from meta_audit.core.models import (
    ProjectCapsule,
    CapsuleFile,
    AnalysisResult,
    Severity,
    AnalysisCategory,
    CrossProjectPattern,
)
from meta_audit.analyzers.batch_processor import BatchProcessor
from meta_audit.generators.report import Report, generate_report
from meta_audit.generators.corpus_report import CorpusAnalysisReport, generate_corpus_report
from meta_audit.analyzers.cross_project_analyzer import CrossProjectAnalyzer


@pytest.fixture
def sample_findings():
    """Create sample AnalysisResult findings for testing."""
    return [
        AnalysisResult(
            analyzer_name="complexity",
            file_path=Path("main.py"),
            line_start=1,
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.9,
            message="High cyclomatic complexity",
            evidence={"complexity": 15},
            remediation=["Refactor function into smaller pieces"],
            project_name="test_project",
        ),
        AnalysisResult(
            analyzer_name="security",
            file_path=Path("utils.py"),
            line_start=10,
            pattern_type="sql_injection",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            confidence=0.8,
            message="SQL injection vulnerability",
            evidence={"pattern": "direct_sql"},
            remediation=["Use parameterized queries"],
            project_name="test_project",
        ),
        AnalysisResult(
            analyzer_name="ai_slop",
            file_path=Path("models.py"),
            line_start=5,
            pattern_type="ai_generated",
            severity=Severity.LOW,
            category=AnalysisCategory.MAINTAINABILITY,
            confidence=0.7,
            message="Likely AI-generated code",
            evidence={"indicators": ["generic_naming", "no_docstring"]},
            remediation=["Review and improve code quality"],
            project_name="test_project",
        ),
    ]


@pytest.fixture
def sample_capsule_files():
    """Create sample CapsuleFile objects."""
    return [
        CapsuleFile(
            path=Path("main.py"),
            size_bytes=150,
            content="def hello():\n    return 'world'\n",
        ),
        CapsuleFile(
            path=Path("utils.py"),
            size_bytes=200,
            content="def helper(x):\n    return x * 2\n",
        ),
        CapsuleFile(
            path=Path("__init__.py"),
            size_bytes=50,
            content="# Package init\n",
        ),
    ]


@pytest.fixture
def sample_project_capsule(sample_capsule_files):
    """Create a sample ProjectCapsule."""
    return ProjectCapsule(
        version=2,
        python_version="3.11",
        project_root=Path("/test/project"),
        project_name="test_project",
        files_count=len(sample_capsule_files),
        total_size_bytes=400,
        files=sample_capsule_files,
    )


# =====================
# ProjectCapsule Tests
# =====================


class TestProjectCapsule:
    """Tests for ProjectCapsule model."""

    def test_capsule_creation(self, sample_project_capsule):
        """Test creating a ProjectCapsule."""
        assert sample_project_capsule.project_name == "test_project"
        assert sample_project_capsule.files_count == 3
        assert len(sample_project_capsule.files) == 3

    def test_capsule_version(self, sample_project_capsule):
        """Test capsule version is set correctly."""
        assert sample_project_capsule.version == 2

    def test_capsule_python_version(self, sample_project_capsule):
        """Test capsule stores Python version."""
        assert sample_project_capsule.python_version == "3.11"

    def test_capsule_json_serialization(self, sample_project_capsule):
        """Test ProjectCapsule can be serialized to JSON."""
        json_str = sample_project_capsule.model_dump_json()
        data = json.loads(json_str)

        assert data["project_name"] == "test_project"
        assert data["files_count"] == 3
        assert len(data["files"]) == 3

    def test_capsule_json_deserialization(self, sample_project_capsule):
        """Test ProjectCapsule can be deserialized from JSON."""
        json_str = sample_project_capsule.model_dump_json()
        capsule = ProjectCapsule.model_validate_json(json_str)

        assert capsule.project_name == "test_project"
        assert capsule.files_count == 3
        assert capsule.files[0].path == Path("main.py")


# ===================
# CapsuleFile Tests
# ===================


class TestCapsuleFile:
    """Tests for CapsuleFile model."""

    def test_capsule_file_creation(self):
        """Test creating a CapsuleFile."""
        file = CapsuleFile(
            path=Path("test.py"),
            size_bytes=100,
            content="print('hello')",
        )
        assert file.path == Path("test.py")
        assert file.size_bytes == 100
        assert file.content == "print('hello')"

    def test_capsule_file_without_content(self):
        """Test CapsuleFile with optional content."""
        file = CapsuleFile(
            path=Path("test.py"),
            size_bytes=100,
            content=None,
        )
        assert file.content is None

    def test_capsule_file_json_serialization(self):
        """Test CapsuleFile JSON serialization."""
        file = CapsuleFile(
            path=Path("test.py"),
            size_bytes=100,
            content="code",
        )
        json_str = file.model_dump_json()
        data = json.loads(json_str)

        assert data["path"] == "test.py"
        assert data["size_bytes"] == 100
        assert data["content"] == "code"


# =======================
# BatchProcessor Tests
# =======================


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    def test_discover_capsules_empty_directory(self):
        """Test discovering capsules in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found = BatchProcessor.discover_capsules(tmpdir)
            assert found == []

    def test_discover_capsules_with_files(self, sample_project_capsule):
        """Test discovering capsules in directory with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a capsule file
            capsule_path = Path(tmpdir) / "test.capsule.json"
            capsule_path.write_text(sample_project_capsule.model_dump_json())

            found = BatchProcessor.discover_capsules(tmpdir)
            assert len(found) == 1
            assert found[0].name == "test.capsule.json"

    def test_load_capsule(self, sample_project_capsule):
        """Test loading a capsule from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write capsule to file
            capsule_path = Path(tmpdir) / "test.capsule.json"
            capsule_path.write_text(sample_project_capsule.model_dump_json())

            # Load it back
            loaded = BatchProcessor.load_capsule(str(capsule_path))
            assert loaded is not None
            assert loaded.project_name == "test_project"
            assert len(loaded.files) == 3

    def test_load_capsule_invalid_file(self):
        """Test loading from non-existent file."""
        loaded = BatchProcessor.load_capsule("/nonexistent/path.json")
        assert loaded is None

    def test_load_capsule_malformed_json(self):
        """Test loading malformed JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            capsule_path = Path(tmpdir) / "bad.capsule.json"
            capsule_path.write_text("{invalid json")

            loaded = BatchProcessor.load_capsule(str(capsule_path))
            assert loaded is None


# =================
# Report Tests
# =================


class TestReport:
    """Tests for Report generation."""

    def test_report_creation(self, sample_findings):
        """Test creating a Report."""
        report = Report(findings=sample_findings, execution_time=1.5)

        assert report.execution_time == 1.5
        assert len(report.findings) == 3

    def test_report_summary(self, sample_findings):
        """Test report summary statistics."""
        report = Report(findings=sample_findings)
        summary = report.summary

        assert summary["TOTAL"] == 3
        assert summary["HIGH"] == 1
        assert summary["MEDIUM"] == 1
        assert summary["LOW"] == 1
        assert summary["CRITICAL"] == 0

    def test_report_json_export(self, sample_findings):
        """Test exporting report to JSON."""
        report = Report(findings=sample_findings, execution_time=2.0)
        json_str = report.to_json()
        data = json.loads(json_str) if isinstance(json_str, str) else json_str

        assert data["summary"]["TOTAL"] == 3
        assert len(data["findings"]) == 3
        assert data["execution_time"] == 2.0

    def test_report_terminal_output(self, sample_findings):
        """Test terminal output generation."""
        report = Report(findings=sample_findings)
        output = report.to_terminal()

        assert "Meta-Audit Report" in output
        assert "Critical:" in output
        assert "High:" in output

    def test_generate_report_helper(self, sample_findings):
        """Test generate_report helper function."""
        report = generate_report(sample_findings, execution_time=1.0)

        assert isinstance(report, Report)
        assert len(report.findings) == 3
        assert report.execution_time == 1.0


# ==========================
# CorpusAnalysisReport Tests
# ==========================


class TestCorpusAnalysisReport:
    """Tests for CorpusAnalysisReport."""

    def test_corpus_report_creation(self, sample_findings):
        """Test creating a CorpusAnalysisReport."""
        # Create reports for two projects
        project_findings = {
            "project_a": sample_findings[:2],
            "project_b": sample_findings[2:],
        }

        project_reports = {}
        for proj_name, findings in project_findings.items():
            project_reports[proj_name] = Report(findings=findings)

        corpus_report = CorpusAnalysisReport(
            project_reports=project_reports,
            all_findings=sample_findings,
            execution_time=5.0,
        )

        assert len(corpus_report.project_reports) == 2
        assert len(corpus_report.all_findings) == 3

    def test_corpus_report_summary(self, sample_findings):
        """Test corpus report summary aggregation."""
        project_reports = {
            "project_a": Report(findings=sample_findings[:2]),
            "project_b": Report(findings=sample_findings[2:]),
        }

        corpus_report = CorpusAnalysisReport(
            project_reports=project_reports,
            all_findings=sample_findings,
        )

        summary = corpus_report.summary
        assert summary["TOTAL"] == 3
        assert summary["projects_analyzed"] == 2

    def test_corpus_report_json_export(self, sample_findings):
        """Test corpus report JSON export."""
        project_reports = {
            "project_a": Report(findings=sample_findings[:2]),
            "project_b": Report(findings=sample_findings[2:]),
        }

        corpus_report = CorpusAnalysisReport(
            project_reports=project_reports,
            all_findings=sample_findings,
        )

        json_str = corpus_report.to_json()
        data = json.loads(json_str) if isinstance(json_str, str) else json_str

        assert data["summary"]["TOTAL"] == 3
        assert data["summary"]["projects_analyzed"] == 2
        assert "project_summaries" in data
        assert "cross_project_patterns" in data

    def test_corpus_report_terminal_output(self, sample_findings):
        """Test corpus report terminal output."""
        project_reports = {
            "project_a": Report(findings=sample_findings[:2]),
            "project_b": Report(findings=sample_findings[2:]),
        }

        corpus_report = CorpusAnalysisReport(
            project_reports=project_reports,
            all_findings=sample_findings,
        )

        output = corpus_report.to_terminal()
        assert "Meta-Audit Corpus Report" in output
        assert "Projects Analyzed:" in output

    def test_generate_corpus_report_helper(self, sample_findings):
        """Test generate_corpus_report helper function."""
        project_reports = {
            "project_a": Report(findings=sample_findings[:2]),
        }

        corpus_report = generate_corpus_report(
            project_reports=project_reports,
            all_findings=sample_findings[:2],
            execution_time=3.0,
        )

        assert isinstance(corpus_report, CorpusAnalysisReport)
        assert corpus_report.execution_time == 3.0


# ==============================
# CrossProjectAnalyzer Tests
# ==============================


class TestCrossProjectAnalyzer:
    """Tests for CrossProjectAnalyzer."""

    def test_analyzer_creation(self):
        """Test creating a CrossProjectAnalyzer."""
        analyzer = CrossProjectAnalyzer()
        assert analyzer.patterns == []

    def test_analyze_empty_findings(self):
        """Test analyzer with empty findings."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {}

        patterns = analyzer.analyze(findings_by_project)
        assert patterns == []

    def test_analyze_single_project(self, sample_findings):
        """Test analyzer with single project findings."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {"project_a": sample_findings}

        patterns = analyzer.analyze(findings_by_project)
        # Single project: no cross-project patterns
        assert patterns == []

    def test_analyze_multiple_projects(self, sample_findings):
        """Test analyzer with multiple projects."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {
            "project_a": sample_findings[:2],
            "project_b": sample_findings[1:],  # Overlapping findings
        }

        patterns = analyzer.analyze(findings_by_project)
        # Phase 4: Should find duplicate patterns
        assert len(patterns) > 0
        # Should detect sql_injection appearing in both projects
        pattern_types = [p.pattern_type for p in patterns]
        assert "sql_injection" in pattern_types

    def test_detect_duplicate_issues(self, sample_findings):
        """Test duplicate issue detection method."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {
            "project_a": sample_findings[:2],
            "project_b": sample_findings[1:],
        }

        # Phase 4: Detects duplicates
        patterns = analyzer.detect_duplicate_issues(findings_by_project)
        assert len(patterns) > 0
        # Should find sql_injection in both
        found_sql = any(p.pattern_type == "sql_injection" for p in patterns)
        assert found_sql

    def test_detect_vulnerability_patterns(self, sample_findings):
        """Test vulnerability pattern detection."""
        analyzer = CrossProjectAnalyzer()
        # Create findings with SECURITY category in multiple projects
        sec_findings = [f for f in sample_findings if f.category == AnalysisCategory.SECURITY]

        findings_by_project = {
            "project_a": sec_findings,
            "project_b": sec_findings,  # Same security issue in both
        }

        # Phase 4: Should detect vulnerabilities across projects
        patterns = analyzer.detect_vulnerability_patterns(findings_by_project)
        assert len(patterns) > 0
        # Should be security category
        assert all(p.category == AnalysisCategory.SECURITY for p in patterns)

    def test_detect_code_quality_trends(self, sample_findings):
        """Test code quality trend detection."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {
            "project_a": sample_findings[:2],
            "project_b": sample_findings[1:],  # Overlapping findings
        }

        # Phase 4: Should detect quality trends
        patterns = analyzer.detect_code_quality_trends(findings_by_project)
        # With multiple categories, may detect trends
        assert isinstance(patterns, list)

    def test_get_patterns(self):
        """Test getting patterns after analysis."""
        analyzer = CrossProjectAnalyzer()
        findings_by_project = {"project_a": []}
        analyzer.analyze(findings_by_project)

        patterns = analyzer.get_patterns()
        assert patterns == []


# ==================
# Integration Tests
# ==================


class TestCapsuleSystemIntegration:
    """Integration tests combining multiple components."""

    def test_full_capsule_workflow(self, sample_project_capsule, sample_findings):
        """Test complete capsule creation and analysis workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save capsule
            capsule_path = Path(tmpdir) / "test.capsule.json"
            capsule_path.write_text(sample_project_capsule.model_dump_json())

            # Load capsule
            loaded = BatchProcessor.load_capsule(str(capsule_path))
            assert loaded is not None

            # Create report with sample findings
            report = generate_report(sample_findings)
            assert report.summary["TOTAL"] == 3

            # Export to JSON
            json_str = report.to_json()
            data = json.loads(json_str)
            assert "summary" in data
            assert "findings" in data

    def test_corpus_workflow_with_multiple_capsules(self, sample_findings):
        """Test complete corpus analysis workflow."""
        # Create multiple project reports
        project_reports = {
            "project_a": Report(findings=sample_findings[:2]),
            "project_b": Report(findings=sample_findings[1:]),
        }

        # Create corpus report
        corpus_report = CorpusAnalysisReport(
            project_reports=project_reports,
            all_findings=sample_findings,
            execution_time=5.0,
        )

        # Verify aggregation
        assert corpus_report.summary["projects_analyzed"] == 2
        assert corpus_report.summary["TOTAL"] == 3

        # Verify cross-project analysis ran
        assert isinstance(corpus_report.cross_project_patterns, list)
