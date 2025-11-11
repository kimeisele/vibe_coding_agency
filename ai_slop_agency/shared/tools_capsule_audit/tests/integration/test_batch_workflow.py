"""Integration tests for the batch corpus analysis workflow."""

import pytest
import json
import tempfile
from pathlib import Path

from meta_audit.core.models import (
    ProjectCapsule,
    CapsuleFile,
    AnalysisResult,
    Severity,
    AnalysisCategory,
)
from meta_audit.analyzers.batch_processor import BatchProcessor
from meta_audit.generators.report import Report, generate_report
from meta_audit.generators.corpus_report import CorpusAnalysisReport, generate_corpus_report
from meta_audit.cli.commands.capsule import discover_python_files, read_file_content


@pytest.fixture
def sample_python_files():
    """Create sample Python files for testing."""
    return {
        "main.py": """def main():
    '''Main entry point.'''
    return calculate(10)

def calculate(x):
    # High complexity for testing
    if x > 10:
        if x > 20:
            if x > 30:
                return x * 3
            return x * 2
        return x + 1
    return x - 1
""",
        "utils.py": """def helper_func(data):
    '''Helper function.'''
    result = data
    return result

class UtilClass:
    def method(self):
        pass
""",
        "__init__.py": "# Init",
    }


@pytest.fixture
def test_project_with_files(sample_python_files):
    """Create a temporary test project with Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        for filename, content in sample_python_files.items():
            (project_path / filename).write_text(content)
        yield project_path


@pytest.fixture
def sample_findings_for_corpus():
    """Create sample findings for corpus analysis."""
    return [
        AnalysisResult(
            analyzer_name="complexity",
            file_path=Path("main.py"),
            line_start=5,
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.95,
            message="Function calculate has cyclomatic complexity of 8",
            evidence={"complexity": 8},
            remediation=["Break function into smaller pieces"],
            project_name="project_a",
        ),
        AnalysisResult(
            analyzer_name="security",
            file_path=Path("utils.py"),
            line_start=1,
            pattern_type="missing_validation",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            confidence=0.85,
            message="Input not validated",
            evidence={"type": "no_validation"},
            remediation=["Add input validation"],
            project_name="project_a",
        ),
        AnalysisResult(
            analyzer_name="complexity",
            file_path=Path("main.py"),
            line_start=5,
            pattern_type="high_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.92,
            message="High cyclomatic complexity",
            evidence={"complexity": 7},
            remediation=["Refactor"],
            project_name="project_b",
        ),
    ]


# ================================
# Capsule Discovery Integration Tests
# ================================


class TestCapsuleDiscovery:
    """Integration tests for capsule discovery."""

    def test_discover_python_files_in_project(self, test_project_with_files):
        """Test discovering Python files in a project."""
        found = discover_python_files(test_project_with_files)
        found_names = {f.name for f in found}

        assert "main.py" in found_names
        assert "utils.py" in found_names
        assert "__init__.py" in found_names

    def test_skip_venv_directories(self):
        """Test that .venv directories are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "main.py").write_text("print('hello')")
            (project_path / ".venv").mkdir()
            (project_path / ".venv" / "site.py").write_text("# venv file")

            found = discover_python_files(project_path)
            found_names = {f.name for f in found}

            assert "main.py" in found_names
            assert "site.py" not in found_names

    def test_skip_pycache_directories(self):
        """Test that __pycache__ directories are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "main.py").write_text("print('hello')")
            (project_path / "__pycache__").mkdir()
            (project_path / "__pycache__" / "main.cpython-311.pyc").write_text("bytecode")

            found = discover_python_files(project_path)
            found_names = {f.name for f in found}

            assert "main.py" in found_names
            assert len([f for f in found if "__pycache__" in str(f)]) == 0


# ========================
# Capsule Creation Integration Tests
# ========================


class TestCapsuleCreation:
    """Integration tests for capsule creation."""

    def test_create_capsule_from_project(self, test_project_with_files):
        """Test creating a capsule from a real project."""
        files = discover_python_files(test_project_with_files)
        capsule_files = []

        for file_path in files:
            content = read_file_content(file_path)
            size = file_path.stat().st_size if file_path.exists() else 0
            capsule_files.append(
                CapsuleFile(
                    path=file_path.relative_to(test_project_with_files),
                    size_bytes=size,
                    content=content,
                )
            )

        capsule = ProjectCapsule(
            version=2,
            python_version="3.11",
            project_root=test_project_with_files,
            project_name="test_project",
            files_count=len(capsule_files),
            total_size_bytes=sum(f.size_bytes for f in capsule_files),
            files=capsule_files,
        )

        assert capsule.project_name == "test_project"
        assert len(capsule.files) == 3
        assert capsule.files_count == 3

    def test_capsule_roundtrip(self, sample_python_files):
        """Test saving and loading capsule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create capsule
            capsule = ProjectCapsule(
                version=2,
                python_version="3.11",
                project_root=Path("/test"),
                project_name="test_project",
                files_count=len(sample_python_files),
                total_size_bytes=100,
                files=[
                    CapsuleFile(
                        path=Path(name),
                        size_bytes=len(content),
                        content=content,
                    )
                    for name, content in sample_python_files.items()
                ],
            )

            # Save to file
            capsule_path = Path(tmpdir) / "test.capsule.json"
            capsule_path.write_text(capsule.model_dump_json())

            # Load from file
            loaded = BatchProcessor.load_capsule(str(capsule_path))
            assert loaded is not None
            assert loaded.project_name == "test_project"
            assert len(loaded.files) == 3


# =============================
# Batch Processing Integration Tests
# =============================


class TestBatchProcessing:
    """Integration tests for batch processing."""

    def test_discover_multiple_capsules(self):
        """Test discovering multiple capsule files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            capsule_dir = Path(tmpdir)

            # Create multiple capsule files
            for i in range(3):
                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=Path(f"/project_{i}"),
                    project_name=f"project_{i}",
                    files_count=1,
                    total_size_bytes=10,
                    files=[CapsuleFile(path=Path("main.py"), size_bytes=10, content="code")],
                )
                capsule_path = capsule_dir / f"project_{i}.capsule.json"
                capsule_path.write_text(capsule.model_dump_json())

            # Discover capsules
            found = BatchProcessor.discover_capsules(str(capsule_dir))
            assert len(found) == 3

    def test_load_capsule_collection(self):
        """Test loading multiple capsules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            capsule_dir = Path(tmpdir)
            capsule_paths = []

            # Create and save capsules
            for i in range(2):
                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=Path(f"/project_{i}"),
                    project_name=f"project_{i}",
                    files_count=1,
                    total_size_bytes=10,
                    files=[CapsuleFile(path=Path("main.py"), size_bytes=10, content="code")],
                )
                capsule_path = capsule_dir / f"project_{i}.capsule.json"
                capsule_path.write_text(capsule.model_dump_json())
                capsule_paths.append(capsule_path)

            # Load capsules
            loaded_capsules = []
            for path in capsule_paths:
                capsule = BatchProcessor.load_capsule(str(path))
                if capsule:
                    loaded_capsules.append(capsule)

            assert len(loaded_capsules) == 2
            assert loaded_capsules[0].project_name == "project_0"
            assert loaded_capsules[1].project_name == "project_1"


# ================================
# Report Generation Integration Tests
# ================================


class TestReportGeneration:
    """Integration tests for report generation."""

    def test_generate_report_from_findings(self, sample_findings_for_corpus):
        """Test generating a report from findings."""
        project_a_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_a"]

        report = generate_report(project_a_findings, execution_time=1.5)

        assert report.summary["TOTAL"] == 2
        assert report.summary["HIGH"] == 1
        assert report.summary["MEDIUM"] == 1

    def test_corpus_report_aggregation(self, sample_findings_for_corpus):
        """Test aggregating multiple project reports."""
        # Create reports for each project
        project_a_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_a"]
        project_b_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_b"]

        report_a = Report(findings=project_a_findings)
        report_b = Report(findings=project_b_findings)

        # Create corpus report
        project_reports = {
            "project_a": report_a,
            "project_b": report_b,
        }

        corpus_report = generate_corpus_report(
            project_reports=project_reports,
            all_findings=sample_findings_for_corpus,
            execution_time=3.0,
        )

        assert corpus_report.summary["projects_analyzed"] == 2
        assert corpus_report.summary["TOTAL"] == 3
        assert corpus_report.execution_time == 3.0

    def test_corpus_report_json_export(self, sample_findings_for_corpus):
        """Test exporting corpus report to JSON."""
        project_a_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_a"]
        project_b_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_b"]

        project_reports = {
            "project_a": Report(findings=project_a_findings),
            "project_b": Report(findings=project_b_findings),
        }

        corpus_report = generate_corpus_report(
            project_reports=project_reports,
            all_findings=sample_findings_for_corpus,
        )

        json_str = corpus_report.to_json()
        data = json.loads(json_str)

        assert data["summary"]["projects_analyzed"] == 2
        assert data["summary"]["TOTAL"] == 3
        assert "project_summaries" in data
        assert "project_a" in data["project_summaries"]
        assert "project_b" in data["project_summaries"]

    def test_corpus_report_terminal_output(self, sample_findings_for_corpus):
        """Test corpus report terminal output."""
        project_a_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_a"]
        project_b_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_b"]

        project_reports = {
            "project_a": Report(findings=project_a_findings),
            "project_b": Report(findings=project_b_findings),
        }

        corpus_report = generate_corpus_report(
            project_reports=project_reports,
            all_findings=sample_findings_for_corpus,
        )

        output = corpus_report.to_terminal()

        assert "Meta-Audit Corpus Report" in output
        assert "Projects Analyzed: 2" in output
        assert "Total Findings: 3" in output


# =============================
# End-to-End Workflow Tests
# =============================


class TestEndToEndWorkflow:
    """End-to-end tests for complete corpus analysis workflow."""

    def test_complete_corpus_workflow(self, sample_findings_for_corpus):
        """Test complete workflow: findings → reports → corpus report."""
        # Step 1: Create individual project reports
        project_a_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_a"]
        project_b_findings = [f for f in sample_findings_for_corpus if f.project_name == "project_b"]

        report_a = generate_report(project_a_findings, execution_time=1.0)
        report_b = generate_report(project_b_findings, execution_time=1.5)

        # Verify individual reports
        assert report_a.summary["TOTAL"] == 2
        assert report_b.summary["TOTAL"] == 1

        # Step 2: Create corpus report
        corpus_report = generate_corpus_report(
            project_reports={"project_a": report_a, "project_b": report_b},
            all_findings=sample_findings_for_corpus,
            execution_time=2.5,
        )

        # Verify corpus report
        assert corpus_report.summary["projects_analyzed"] == 2
        assert corpus_report.summary["TOTAL"] == 3

        # Step 3: Export to formats
        json_output = corpus_report.to_json()
        terminal_output = corpus_report.to_terminal()

        assert isinstance(json_output, str)
        assert isinstance(terminal_output, str)
        assert json.loads(json_output)  # Valid JSON
        assert "Meta-Audit" in terminal_output

    def test_corpus_with_capsule_storage(self, sample_findings_for_corpus):
        """Test storing and retrieving corpus analysis results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            capsule_dir = Path(tmpdir)
            capsule_files = []

            # Create and store capsules for each project
            for project_name in ["project_a", "project_b"]:
                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=Path(f"/{project_name}"),
                    project_name=project_name,
                    files_count=1,
                    total_size_bytes=10,
                    files=[CapsuleFile(path=Path("main.py"), size_bytes=10, content="code")],
                )
                capsule_path = capsule_dir / f"{project_name}.capsule.json"
                capsule_path.write_text(capsule.model_dump_json())
                capsule_files.append(capsule_path)

            # Discover stored capsules
            discovered = BatchProcessor.discover_capsules(str(capsule_dir))
            assert len(discovered) == 2

            # Load capsules and create reports
            project_reports = {}
            for capsule_path in discovered:
                capsule = BatchProcessor.load_capsule(str(capsule_path))
                if capsule:
                    # Use sample findings for this project
                    findings = [
                        f for f in sample_findings_for_corpus if f.project_name == capsule.project_name
                    ]
                    if findings:
                        project_reports[capsule.project_name] = Report(findings=findings)

            # Create corpus report
            if project_reports:
                all_findings = [
                    f for f in sample_findings_for_corpus if f.project_name in project_reports
                ]
                corpus_report = generate_corpus_report(
                    project_reports=project_reports,
                    all_findings=all_findings,
                )

                assert corpus_report.summary["projects_analyzed"] == len(project_reports)

    def test_error_handling_with_invalid_findings(self):
        """Test error handling with invalid/edge case findings."""
        # Empty findings
        report = Report(findings=[])
        assert report.summary["TOTAL"] == 0

        # Single finding
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path("test.py"),
                line_start=1,
                pattern_type="test_pattern",
                severity=Severity.LOW,
                category=AnalysisCategory.CODE_STRUCTURE,
                message="Test message",
            )
        ]
        report = Report(findings=findings)
        assert report.summary["TOTAL"] == 1
        assert report.summary["LOW"] == 1
