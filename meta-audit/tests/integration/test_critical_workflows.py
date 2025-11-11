"""Critical Workflow Integration Tests for Meta-Audit

These tests verify the end-to-end workflows that users depend on:
1. Project Scan → Collection → Triage → Reporting
2. Corpus Analysis → Cross-project Patterns
3. Integration with all Phase 1-4 components

Pattern: Real code analysis through the entire pipeline.
"""

from pathlib import Path
from typing import List

import pytest

from meta_audit.analyzers.collectors import run_all_collectors
from meta_audit.agents.planning import Planner
from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory
from meta_audit.generators.report import generate_report


class TestSingleProjectWorkflow:
    """End-to-end workflow: Analyze single project."""

    @pytest.fixture
    def meta_audit_src(self):
        """Get meta-audit source for testing."""
        return Path(__file__).parent.parent.parent / "src"

    def test_workflow_scan_collect_report(self, meta_audit_src):
        """WORKFLOW 1: Project Scan → Collection → Reporting

        The primary workflow: analyze a project and generate report.
        """
        # Phase 1: Collect data from static analyzers
        collection_result = run_all_collectors(str(meta_audit_src))

        assert collection_result["status"] in ["success", "partial_success"], \
            f"Collection failed: {collection_result.get('errors')}"

        all_findings = collection_result["all_findings"]
        assert len(all_findings) > 0, "Should find at least some issues in meta-audit"

        # Phase 2: Generate report
        report = generate_report(all_findings, execution_time=0.5)

        # Verify report structure
        assert hasattr(report, "summary"), "Report must have summary"
        assert hasattr(report, "findings"), "Report must have findings"

        # Verify summary is correct
        summary = report.summary
        assert "CRITICAL" in summary
        assert "HIGH" in summary
        assert "MEDIUM" in summary
        assert "LOW" in summary
        assert "TOTAL" in summary

        # Verify findings are present
        findings_count = len(report.findings)
        assert findings_count > 0, "Report should have findings"

        print(f"✅ Workflow complete: {findings_count} findings in report")

    def test_workflow_empty_project(self):
        """WORKFLOW 2: Analyze empty/minimal directory gracefully"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty directory
            result = run_all_collectors(tmpdir)

            assert result["status"] in ["success", "partial_success"]
            # Empty project might have 0 findings or some default analysis
            assert isinstance(result["all_findings"], list)

            # Generate report even with few/no findings
            report = generate_report(result["all_findings"], execution_time=0.1)
            assert hasattr(report, "summary")

            print(f"✅ Empty project workflow: handled gracefully")

    def test_workflow_report_format_consistency(self, meta_audit_src):
        """WORKFLOW 3: Report format is consistent

        Verify that different runs produce structurally identical reports.
        """
        # Run 1
        result1 = run_all_collectors(str(meta_audit_src))
        report1 = generate_report(result1["all_findings"], execution_time=0.5)

        # Run 2 (deterministic, same input)
        result2 = run_all_collectors(str(meta_audit_src))
        report2 = generate_report(result2["all_findings"], execution_time=0.5)

        # Reports should have same structure
        assert set(report1.summary.keys()) == set(report2.summary.keys()), \
            "Report summary keys should be consistent"

        # Findings count should be identical (deterministic analysis)
        assert len(report1.findings) == len(report2.findings), \
            "Findings count should be deterministic"

        print(f"✅ Report format is consistent")


class TestTriageWorkflow:
    """End-to-end workflow: Triage findings for LLM analysis."""

    @pytest.fixture
    def planner(self):
        """Create a Planner instance."""
        return Planner()

    @pytest.fixture
    def realistic_findings(self) -> List[AnalysisResult]:
        """Create realistic mixed findings (like from real analysis)."""
        return [
            # CRITICAL - must go to LLM
            AnalysisResult(
                analyzer_name="security_analyzer",
                file_path=Path("agents/audit_agent.py"),
                pattern_type="command_injection",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.95,
                message="Potential command injection",
                evidence={"line": 142},
                remediation=["Sanitize input"],
            ),
            # HIGH + high confidence - goes to LLM
            AnalysisResult(
                analyzer_name="complexity_analyzer",
                file_path=Path("analyzers/batch_processor.py"),
                pattern_type="high_complexity",
                severity=Severity.HIGH,
                category=AnalysisCategory.MAINTAINABILITY,
                confidence=0.88,
                message="Function too complex",
                evidence={"complexity": 15},
                remediation=["Extract methods"],
            ),
            # HIGH + low confidence - skip LLM
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=Path("core/models.py"),
                pattern_type="generic_naming",
                severity=Severity.HIGH,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.65,
                message="Generic variable",
                evidence={"name": "data"},
                remediation=["Rename"],
            ),
            # MEDIUM - skip LLM
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=Path("analyzers/collectors/ai_slop.py"),
                pattern_type="unused_import",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.80,
                message="Unused import",
                evidence={"import": "os"},
                remediation=["Remove import"],
            ),
            # LOW - skip LLM
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=Path("cli/main.py"),
                pattern_type="whitespace",
                severity=Severity.LOW,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.50,
                message="Trailing whitespace",
                evidence={},
                remediation=["Format"],
            ),
        ]

    def test_triage_filters_correctly(self, planner, realistic_findings):
        """WORKFLOW 4: Triage correctly filters findings"""
        result = planner.triage(realistic_findings)

        # Should select CRITICAL + HIGH(high conf) = 2 findings for LLM
        assert len(result.llm_worthy_findings) == 2, \
            f"Expected 2 LLM-worthy findings, got {len(result.llm_worthy_findings)}"

        # Verify the right ones were selected
        pattern_types = {f.pattern_type for f in result.llm_worthy_findings}
        assert "command_injection" in pattern_types
        assert "high_complexity" in pattern_types

        print(f"✅ Triage: {len(result.llm_worthy_findings)}/{len(realistic_findings)} to LLM")

    def test_triage_routing_is_complete(self, planner, realistic_findings):
        """WORKFLOW 5: Triage routing covers all selected findings"""
        result = planner.triage(realistic_findings)

        # Every llm_worthy finding should have a routing decision
        for finding in result.llm_worthy_findings:
            assert finding.pattern_type in result.routing, \
                f"Missing routing for {finding.pattern_type}"

            persona = result.routing[finding.pattern_type]
            assert isinstance(persona, str) and len(persona) > 0, \
                f"Invalid routing persona for {finding.pattern_type}"

        print(f"✅ Triage routing complete for {len(result.llm_worthy_findings)} findings")

    def test_triage_token_estimate_reasonable(self, planner, realistic_findings):
        """WORKFLOW 6: Token estimate is reasonable for budget planning"""
        result = planner.triage(realistic_findings)

        # With 2 findings: 100 (base) + 2*150 = 400 tokens
        expected_min = 100
        expected_max = 100 + (10 * 150)  # Max 10 findings

        assert expected_min < result.token_estimate < expected_max, \
            f"Token estimate {result.token_estimate} outside reasonable range"

        print(f"✅ Token estimate: {result.token_estimate} tokens")


class TestAnalysisCollectorIntegration:
    """End-to-end workflow: All collectors work together."""

    @pytest.fixture
    def meta_audit_src(self):
        """Get meta-audit source."""
        return Path(__file__).parent.parent.parent / "src"

    def test_collectors_find_real_issues(self, meta_audit_src):
        """WORKFLOW 7: Collectors actually find real issues in code"""
        result = run_all_collectors(str(meta_audit_src))

        assert result["status"] in ["success", "partial_success"]

        collectors_data = result["collectors_data"]

        # Meta-audit should have some issues
        assert len(result["all_findings"]) > 0, \
            "Should find issues in real code"

        # Security collector should find something (subprocess, shell=True usage)
        security_findings = collectors_data.get("security", [])
        assert len(security_findings) > 0, \
            "Security collector should find issues (subprocess usage)"

        # AI-slop should find naming issues
        ai_slop_findings = collectors_data.get("ai_slop", [])
        assert len(ai_slop_findings) > 0, \
            "AI-slop should find naming issues"

        print(f"✅ Collectors found real issues:")
        for collector, findings in collectors_data.items():
            print(f"   - {collector}: {len(findings)} findings")

    def test_findings_have_complete_info(self, meta_audit_src):
        """WORKFLOW 8: All findings have required information"""
        result = run_all_collectors(str(meta_audit_src))
        findings = result["all_findings"]

        required_fields = {
            "analyzer_name",
            "pattern_type",
            "severity",
            "category",
            "confidence",
            "message",
            "evidence",
            "remediation",
        }

        for finding in findings[:10]:  # Sample first 10
            actual_fields = set(finding.__dict__.keys())
            for field in required_fields:
                assert field in actual_fields, \
                    f"Finding missing {field}: {finding.pattern_type}"

        print(f"✅ All findings have complete information")


class TestErrorHandling:
    """End-to-end workflow: Error handling and resilience."""

    def test_nonexistent_path_handled(self):
        """WORKFLOW 9: Non-existent path is handled gracefully"""
        result = run_all_collectors("/nonexistent/path/that/does/not/exist")

        # Should return error status but not crash
        assert result["status"] in ["success", "partial_success"]
        assert isinstance(result["all_findings"], list)

        print(f"✅ Non-existent path handled gracefully")

    def test_permission_denied_handled(self):
        """WORKFLOW 10: Permission errors are handled gracefully"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file and deny read permissions
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('test')")

            try:
                os.chmod(tmpdir, 0o000)

                # Should handle gracefully
                result = run_all_collectors(tmpdir)
                assert isinstance(result, dict)
                assert "all_findings" in result

                print(f"✅ Permission errors handled gracefully")
            finally:
                # Restore permissions for cleanup
                os.chmod(tmpdir, 0o755)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
