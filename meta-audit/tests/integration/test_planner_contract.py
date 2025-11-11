"""Contract Tests for Planner & TriageResult

These tests define and enforce the API contracts for the Planner component.
The Planner is the "brain" of Phase 5 - it decides which findings deserve LLM analysis.

Contract: All decisions must be deterministic, auditable, and token-efficient.
"""

from typing import List

import pytest

from meta_audit.agents.planning import Planner
from meta_audit.core.models import (
    AnalysisResult,
    CrossProjectPattern,
    TriageResult,
    Severity,
    AnalysisCategory,
)


class TestPlannerContract:
    """Contract tests for Planner - defines API guarantees."""

    @pytest.fixture
    def planner(self):
        """Create a Planner instance."""
        return Planner()

    @pytest.fixture
    def sample_findings(self) -> List[AnalysisResult]:
        """Create a diverse set of test findings."""
        return [
            # CRITICAL - always goes to LLM
            AnalysisResult(
                analyzer_name="security_analyzer",
                file_path=None,
                pattern_type="sql_injection",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.95,
                message="SQL injection vulnerability found",
                evidence={"line": 42},
                remediation=["Use parameterized queries"],
            ),
            # HIGH with high confidence - goes to LLM
            AnalysisResult(
                analyzer_name="complexity_analyzer",
                file_path=None,
                pattern_type="god_object",
                severity=Severity.HIGH,
                category=AnalysisCategory.MAINTAINABILITY,
                confidence=0.85,
                message="God object pattern detected",
                evidence={"methods": 15},
                remediation=["Extract responsibilities"],
            ),
            # HIGH with low confidence - does NOT go to LLM
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=None,
                pattern_type="generic_naming",
                severity=Severity.HIGH,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.60,
                message="Generic variable name",
                evidence={"name": "result"},
                remediation=["Rename to descriptive name"],
            ),
            # MEDIUM - does NOT go to LLM (by default)
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=None,
                pattern_type="generic_naming",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.75,
                message="Generic variable name",
                evidence={"name": "data"},
                remediation=["Rename to descriptive name"],
            ),
            # LOW - does NOT go to LLM
            AnalysisResult(
                analyzer_name="ai_slop_analyzer",
                file_path=None,
                pattern_type="whitespace",
                severity=Severity.LOW,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.50,
                message="Inconsistent whitespace",
                evidence={},
                remediation=["Run formatter"],
            ),
        ]

    @pytest.fixture
    def sample_patterns(self) -> List[CrossProjectPattern]:
        """Create sample cross-project patterns."""
        return [
            CrossProjectPattern(
                pattern_type="recurring_security_issue",
                severity=Severity.HIGH,
                category=AnalysisCategory.SECURITY,
                projects_count=3,
                projects=["project_a", "project_b", "project_c"],
                evidence={"type": "buffer_overflow"},
                message="Buffer overflow pattern found in 3 projects",
                projects_confidence=0.88,
            ),
            CrossProjectPattern(
                pattern_type="architectural_smell",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.MAINTAINABILITY,
                projects_count=2,
                projects=["project_x", "project_y"],
                evidence={"pattern": "circular_dependency"},
                message="Circular dependency pattern",
                projects_confidence=0.72,
            ),
        ]

    def test_triage_returns_triage_result(self, planner, sample_findings):
        """CONTRACT 1: triage() always returns a TriageResult."""
        result = planner.triage(sample_findings)

        assert isinstance(result, TriageResult), "triage() must return TriageResult"

    def test_triage_result_has_required_fields(self, planner, sample_findings):
        """CONTRACT 2: TriageResult has all required fields."""
        result = planner.triage(sample_findings)

        assert hasattr(result, "all_findings"), "Missing all_findings"
        assert hasattr(result, "llm_worthy_findings"), "Missing llm_worthy_findings"
        assert hasattr(result, "routing"), "Missing routing"
        assert hasattr(result, "token_estimate"), "Missing token_estimate"

    def test_triage_result_field_types(self, planner, sample_findings):
        """CONTRACT 3: TriageResult fields have correct types."""
        result = planner.triage(sample_findings)

        assert isinstance(result.all_findings, list), "all_findings must be list"
        assert isinstance(result.llm_worthy_findings, list), "llm_worthy_findings must be list"
        assert isinstance(result.routing, dict), "routing must be dict"
        assert isinstance(result.token_estimate, int), "token_estimate must be int"

    def test_all_findings_preserved(self, planner, sample_findings):
        """CONTRACT 4: All input findings are preserved in all_findings."""
        result = planner.triage(sample_findings)

        assert len(result.all_findings) == len(sample_findings), \
            "all_findings count must match input findings"
        assert result.all_findings == sample_findings, \
            "all_findings must be identical to input"

    def test_llm_worthy_is_subset(self, planner, sample_findings):
        """CONTRACT 5: llm_worthy_findings must be a subset of all_findings."""
        result = planner.triage(sample_findings)

        for finding in result.llm_worthy_findings:
            assert finding in result.all_findings, \
                "All llm_worthy_findings must be in all_findings"

    def test_triage_rule_critical_always_included(self, planner):
        """CONTRACT 6: CRITICAL findings ALWAYS go to LLM."""
        critical_finding = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="critical_issue",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.SECURITY,
            confidence=0.5,  # Even low confidence
            message="Critical finding",
            evidence={},
            remediation=[],
        )

        result = planner.triage([critical_finding])

        assert len(result.llm_worthy_findings) == 1, \
            "CRITICAL finding must be included regardless of confidence"
        assert critical_finding in result.llm_worthy_findings

    def test_triage_rule_high_confidence_included(self, planner):
        """CONTRACT 7: HIGH + confidence >= 0.8 goes to LLM."""
        high_confident = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="high_confident",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.80,
            message="High confidence finding",
            evidence={},
            remediation=[],
        )

        result = planner.triage([high_confident])

        assert len(result.llm_worthy_findings) == 1
        assert high_confident in result.llm_worthy_findings

    def test_triage_rule_high_low_confidence_excluded(self, planner):
        """CONTRACT 8: HIGH + confidence < 0.8 does NOT go to LLM."""
        high_low_conf = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="high_low_conf",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.75,  # Below 0.8
            message="High but low confidence",
            evidence={},
            remediation=[],
        )

        result = planner.triage([high_low_conf])

        assert len(result.llm_worthy_findings) == 0, \
            "HIGH with confidence < 0.8 should not be included"

    def test_triage_rule_patterns_always_included(self, planner, sample_patterns):
        """CONTRACT 9: ALL cross-project patterns always go to LLM."""
        result = planner.triage([], patterns=sample_patterns)

        # Patterns are converted to findings
        assert len(result.llm_worthy_findings) == len(sample_patterns), \
            "All patterns must be included as findings"

    def test_triage_rule_maximum_10_findings(self, planner):
        """CONTRACT 10: Maximum 10 findings selected (token budget)."""
        # Create 20 CRITICAL findings (all should qualify, but capped at 10)
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=None,
                pattern_type=f"critical_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.90,
                message=f"Critical {i}",
                evidence={},
                remediation=[],
            )
            for i in range(20)
        ]

        result = planner.triage(findings)

        assert len(result.llm_worthy_findings) <= 10, \
            "llm_worthy_findings must not exceed 10"

    def test_routing_security_to_security_analyst(self, planner):
        """CONTRACT 11: SECURITY findings route to security_analyst."""
        security_finding = AnalysisResult(
            analyzer_name="security_analyzer",
            file_path=None,
            pattern_type="sql_injection",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.SECURITY,
            confidence=0.95,
            message="SQL injection",
            evidence={},
            remediation=[],
        )

        result = planner.triage([security_finding])
        persona = result.routing.get("sql_injection")

        assert persona == "security_analyst", \
            "SECURITY findings must route to security_analyst"

    def test_routing_code_structure_to_refactor_gpt(self, planner):
        """CONTRACT 12: CODE_STRUCTURE findings route to refactor_gpt."""
        code_finding = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="god_object",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.90,
            message="God object",
            evidence={},
            remediation=[],
        )

        result = planner.triage([code_finding])
        persona = result.routing.get("god_object")

        assert persona == "refactor_gpt", \
            "CODE_STRUCTURE findings must route to refactor_gpt"

    def test_routing_maintainability_to_refactor_gpt(self, planner):
        """CONTRACT 13: MAINTAINABILITY findings route to refactor_gpt."""
        maint_finding = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="duplicated_code",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.MAINTAINABILITY,
            confidence=0.90,
            message="Duplicated code",
            evidence={},
            remediation=[],
        )

        result = planner.triage([maint_finding])
        persona = result.routing.get("duplicated_code")

        assert persona == "refactor_gpt", \
            "MAINTAINABILITY findings must route to refactor_gpt"

    def test_routing_performance_to_performance_analyst(self, planner):
        """CONTRACT 14: PERFORMANCE findings route to performance_analyst."""
        perf_finding = AnalysisResult(
            analyzer_name="test",
            file_path=None,
            pattern_type="n_plus_one_query",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.PERFORMANCE,
            confidence=0.90,
            message="N+1 query",
            evidence={},
            remediation=[],
        )

        result = planner.triage([perf_finding])
        persona = result.routing.get("n_plus_one_query")

        assert persona == "performance_analyst", \
            "PERFORMANCE findings must route to performance_analyst"

    def test_token_estimate_positive(self, planner, sample_findings):
        """CONTRACT 15: Token estimate must be positive."""
        result = planner.triage(sample_findings)

        assert result.token_estimate > 0, "token_estimate must be positive"

    def test_token_estimate_includes_base_tokens(self, planner):
        """CONTRACT 16: Token estimate includes base + per-finding."""
        # Create 5 findings that will be selected
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=None,
                pattern_type=f"critical_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.90,
                message=f"Critical {i}",
                evidence={},
                remediation=[],
            )
            for i in range(5)
        ]

        result = planner.triage(findings)

        # Expected: 100 (base) + 5 * 150 (per-finding) = 850
        expected = 100 + (5 * 150)
        assert result.token_estimate == expected, \
            f"Token estimate should be {expected}, got {result.token_estimate}"

    def test_empty_findings_triage(self, planner):
        """CONTRACT 17: Empty findings list is handled gracefully."""
        result = planner.triage([])

        assert isinstance(result, TriageResult)
        assert len(result.all_findings) == 0
        assert len(result.llm_worthy_findings) == 0
        assert isinstance(result.routing, dict)
        assert result.token_estimate > 0  # Still has base tokens

    def test_severity_ordering(self, planner):
        """CONTRACT 18: Findings are sorted by severity (CRITICAL > HIGH > MEDIUM)."""
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=None,
                pattern_type="medium",
                severity=Severity.MEDIUM,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.90,
                message="Medium",
                evidence={},
                remediation=[],
            ),
            AnalysisResult(
                analyzer_name="test",
                file_path=None,
                pattern_type="critical",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.90,
                message="Critical",
                evidence={},
                remediation=[],
            ),
            AnalysisResult(
                analyzer_name="test",
                file_path=None,
                pattern_type="high",
                severity=Severity.HIGH,
                category=AnalysisCategory.CODE_STRUCTURE,
                confidence=0.90,
                message="High",
                evidence={},
                remediation=[],
            ),
        ]

        result = planner.triage(findings)

        # MEDIUM doesn't qualify for LLM, so only CRITICAL and HIGH
        # Should be sorted: CRITICAL, HIGH
        assert len(result.llm_worthy_findings) == 2
        assert result.llm_worthy_findings[0].severity == Severity.CRITICAL
        assert result.llm_worthy_findings[1].severity == Severity.HIGH

    def test_deterministic_routing(self, planner, sample_findings):
        """CONTRACT 19: Same input produces same output (deterministic)."""
        result1 = planner.triage(sample_findings)
        result2 = planner.triage(sample_findings)

        assert len(result1.llm_worthy_findings) == len(result2.llm_worthy_findings)
        assert result1.token_estimate == result2.token_estimate
        assert result1.routing == result2.routing


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
