"""Production testing with real projects."""

import json
import os
import tempfile
import time
from pathlib import Path

import pytest

from meta_audit.cli.commands.capsule import discover_python_files, read_file_content
from meta_audit.core.models import ProjectCapsule, CapsuleFile, AnalysisResult
from meta_audit.analyzers.batch_processor import BatchProcessor
from meta_audit.generators.report import Report, generate_report
from meta_audit.generators.corpus_report import CorpusAnalysisReport, generate_corpus_report


# Project paths - use current project for testing
# These tests are marked as skip_ci because they depend on specific project structures
CAPSULE_AUDIT_PATH = Path(__file__).parent.parent.parent.absolute()
AGENCY_TOOLKIT_PATH = Path(os.getenv("AGENCY_TOOLKIT_PATH", "/tmp/nonexistent"))

# Skip these tests if paths don't exist
SKIP_REASON = "Project paths not available (set AGENCY_TOOLKIT_PATH env var for corpus tests)"
SKIP_IF_NO_AGENCY = not AGENCY_TOOLKIT_PATH.exists()


@pytest.mark.production
class TestProductionSingleProject:
    """Production tests for single-project analysis."""

    def test_capsule_audit_self_analysis(self):
        """Test analyzing meta-audit project itself."""
        # Discover Python files
        files = discover_python_files(CAPSULE_AUDIT_PATH)

        assert len(files) > 0, "Should find Python files"
        print(f"Found {len(files)} Python files in capsule_audit")

        # Check for expected modules
        file_names = {f.name for f in files}
        assert any("models" in f for f in file_names), "Should find models.py"
        assert any("analyze" in f for f in file_names), "Should find analyze command"

    def test_capsule_creation_capsule_audit(self):
        """Test creating a ProjectCapsule for meta-audit."""
        files = discover_python_files(CAPSULE_AUDIT_PATH)
        capsule_files = []

        for file_path in files[:50]:  # Sample first 50 files for speed
            content = read_file_content(file_path)
            if content:
                capsule_files.append(
                    CapsuleFile(
                        path=file_path.relative_to(CAPSULE_AUDIT_PATH),
                        size_bytes=len(content.encode("utf-8")),
                        content=content,
                    )
                )

        capsule = ProjectCapsule(
            version=2,
            python_version="3.11",
            project_root=CAPSULE_AUDIT_PATH,
            project_name="capsule_audit",
            files_count=len(capsule_files),
            total_size_bytes=sum(f.size_bytes for f in capsule_files),
            files=capsule_files,
        )

        assert capsule.project_name == "capsule_audit"
        assert len(capsule.files) > 0
        capsule_size_kb = capsule.total_size_bytes / 1024
        print(f"Capsule size: {capsule_size_kb:.1f} KB ({len(capsule.files)} files)")

    def test_capsule_audit_roundtrip(self):
        """Test save and load cycle for meta-audit capsule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple capsule
            files = discover_python_files(CAPSULE_AUDIT_PATH)
            capsule_files = [
                CapsuleFile(
                    path=f.relative_to(CAPSULE_AUDIT_PATH),
                    size_bytes=100,
                    content="# sample code",
                )
                for f in files[:10]
            ]

            capsule = ProjectCapsule(
                version=2,
                python_version="3.11",
                project_root=CAPSULE_AUDIT_PATH,
                project_name="capsule_audit_test",
                files_count=len(capsule_files),
                total_size_bytes=1000,
                files=capsule_files,
            )

            # Save
            capsule_path = Path(tmpdir) / "capsule_audit.capsule.json"
            capsule_path.write_text(capsule.model_dump_json())

            # Load
            loaded = BatchProcessor.load_capsule(str(capsule_path))
            assert loaded is not None
            assert loaded.project_name == "capsule_audit_test"
            assert len(loaded.files) == 10


@pytest.mark.production
@pytest.mark.skip_ci
@pytest.mark.skipif(SKIP_IF_NO_AGENCY, reason=SKIP_REASON)
class TestProductionCorpus:
    """Production tests for corpus analysis."""

    def test_discover_both_projects(self):
        """Test discovering both real projects."""
        capsule_audit_files = discover_python_files(CAPSULE_AUDIT_PATH)
        agency_toolkit_files = discover_python_files(AGENCY_TOOLKIT_PATH)

        print(
            f"\nProject files found:\n"
            f"- capsule_audit: {len(capsule_audit_files)} files\n"
            f"- agency_toolkit: {len(agency_toolkit_files)} files"
        )

        assert len(capsule_audit_files) > 0
        assert len(agency_toolkit_files) > 0

    def test_corpus_capsule_creation(self):
        """Test creating capsules for both projects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            corpus_dir = Path(tmpdir)

            # Create capsules for both projects
            for project_name, project_path in [
                ("capsule_audit", CAPSULE_AUDIT_PATH),
                ("agency_toolkit", AGENCY_TOOLKIT_PATH),
            ]:
                files = discover_python_files(project_path)
                capsule_files = [
                    CapsuleFile(
                        path=f.relative_to(project_path),
                        size_bytes=100,
                        content=f"# {project_name} code",
                    )
                    for f in files[:20]  # Sample first 20
                ]

                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=project_path,
                    project_name=project_name,
                    files_count=len(capsule_files),
                    total_size_bytes=len(capsule_files) * 100,
                    files=capsule_files,
                )

                # Save
                capsule_path = corpus_dir / f"{project_name}.capsule.json"
                capsule_path.write_text(capsule.model_dump_json())

            # Discover saved capsules
            discovered = BatchProcessor.discover_capsules(str(corpus_dir))
            assert len(discovered) == 2
            print(f"Created {len(discovered)} capsules in corpus")

    def test_corpus_analysis_full_cycle(self):
        """Full production test: Create capsules, load, analyze, report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            corpus_dir = Path(tmpdir)

            # Create sample capsules
            for project_name, project_path in [
                ("capsule_audit", CAPSULE_AUDIT_PATH),
                ("agency_toolkit", AGENCY_TOOLKIT_PATH),
            ]:
                files = discover_python_files(project_path)
                capsule_files = [
                    CapsuleFile(
                        path=f.relative_to(project_path),
                        size_bytes=100,
                        content="# code",
                    )
                    for f in files[:15]
                ]

                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=project_path,
                    project_name=project_name,
                    files_count=len(capsule_files),
                    total_size_bytes=len(capsule_files) * 100,
                    files=capsule_files,
                )

                capsule_path = corpus_dir / f"{project_name}.capsule.json"
                capsule_path.write_text(capsule.model_dump_json())

            # Discover and load capsules
            discovered = BatchProcessor.discover_capsules(str(corpus_dir))
            loaded_capsules = [
                BatchProcessor.load_capsule(str(p)) for p in discovered if p.exists()
            ]
            loaded_capsules = [c for c in loaded_capsules if c is not None]

            assert len(loaded_capsules) == 2
            print(f"Loaded {len(loaded_capsules)} capsules")

            # Create dummy findings for corpus analysis
            sample_findings = [
                AnalysisResult(
                    analyzer_name="test_analyzer",
                    file_path=Path("test.py"),
                    line_start=1,
                    pattern_type="test_pattern",
                    severity="MEDIUM",
                    category="code_structure",
                    confidence=0.9,
                    message="Test finding",
                    project_name="capsule_audit",
                ),
                AnalysisResult(
                    analyzer_name="test_analyzer",
                    file_path=Path("test.py"),
                    line_start=1,
                    pattern_type="test_pattern",
                    severity="HIGH",
                    category="security",
                    confidence=0.85,
                    message="Test finding 2",
                    project_name="agency_toolkit",
                ),
            ]

            # Generate individual reports
            report_a = Report(findings=sample_findings[:1])
            report_b = Report(findings=sample_findings[1:])

            # Generate corpus report
            corpus_report = generate_corpus_report(
                project_reports={
                    "capsule_audit": report_a,
                    "agency_toolkit": report_b,
                },
                all_findings=sample_findings,
                execution_time=2.5,
            )

            assert corpus_report.summary["projects_analyzed"] == 2
            assert corpus_report.summary["TOTAL"] == 2

            # Verify JSON export
            json_str = corpus_report.to_json()
            data = json.loads(json_str)
            assert data["summary"]["projects_analyzed"] == 2

            # Verify terminal output
            terminal_output = corpus_report.to_terminal()
            assert "Meta-Audit Corpus Report" in terminal_output
            assert "Projects Analyzed: 2" in terminal_output

            print(f"Corpus report generated: {len(json_str)} bytes JSON")


@pytest.mark.production
class TestProductionPerformance:
    """Performance benchmarks for production scenarios."""

    def test_single_project_performance(self):
        """Benchmark single-project capsule creation."""
        start = time.time()

        files = discover_python_files(CAPSULE_AUDIT_PATH)
        capsule_files = [
            CapsuleFile(
                path=f.relative_to(CAPSULE_AUDIT_PATH),
                size_bytes=100,
                content="# code",
            )
            for f in files[:50]
        ]

        capsule = ProjectCapsule(
            version=2,
            python_version="3.11",
            project_root=CAPSULE_AUDIT_PATH,
            project_name="capsule_audit",
            files_count=len(capsule_files),
            total_size_bytes=sum(f.size_bytes for f in capsule_files),
            files=capsule_files,
        )

        elapsed = time.time() - start
        print(f"\nSingle-project capsule creation: {elapsed:.2f}s for {len(files)} files")
        assert elapsed < 10, "Should complete in under 10 seconds"

    def test_corpus_discovery_performance(self):
        """Benchmark corpus discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            corpus_dir = Path(tmpdir)

            # Create 5 sample capsules
            for i in range(5):
                capsule = ProjectCapsule(
                    version=2,
                    python_version="3.11",
                    project_root=Path(f"/project_{i}"),
                    project_name=f"project_{i}",
                    files_count=1,
                    total_size_bytes=100,
                    files=[CapsuleFile(path=Path("test.py"), size_bytes=100, content="code")],
                )
                path = corpus_dir / f"project_{i}.capsule.json"
                path.write_text(capsule.model_dump_json())

            # Benchmark discovery
            start = time.time()
            discovered = BatchProcessor.discover_capsules(str(corpus_dir))
            elapsed = time.time() - start

            print(f"\nCorpus discovery (5 capsules): {elapsed:.3f}s")
            assert len(discovered) == 5
            assert elapsed < 1.0, "Should complete in under 1 second"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
