"""Unit tests for Planner (Phase 5 automatic triage and routing)."""

import pytest

pytestmark = [pytest.mark.phase5, pytest.mark.unit]
from pathlib import Path
from meta_audit.agents.planning import Planner
from meta_audit.core.models import (
    AnalysisResult,
    CrossProjectPattern,
    Severity,
    AnalysisCategory,
    TriageResult,
)


@pytest.fixture
def planner():
    """Create a Planner instance for testing."""
    return Planner()


@pytest.fixture
def critical_finding():
    """Create a CRITICAL severity finding."""
    return AnalysisResult(
        analyzer_name="bandit",
        file_path=Path("src/auth.py"),
        pattern_type="hardcoded_password",
        severity=Severity.CRITICAL,
        category=AnalysisCategory.SECURITY,
        confidence=0.95,
        message="Use of hardcoded password",
        evidence={"test_id": "B105"},
        remediation=["Use environment variables or secrets manager"],
    )


@pytest.fixture
def high_confident_finding():
    """Create a HIGH severity finding with confidence >= 0.8."""
    return AnalysisResult(
        analyzer_name="bandit",
        file_path=Path("src/db/queries.py"),
        pattern_type="sql_injection",
        severity=Severity.HIGH,
        category=AnalysisCategory.SECURITY,
        confidence=0.85,
        message="Potential SQL injection vulnerability",
        evidence={"test_id": "B608"},
        remediation=["Use parameterized queries"],
    )


@pytest.fixture
def high_low_confidence_finding():
    """Create a HIGH severity finding with confidence < 0.8 (should NOT be triaged)."""
    return AnalysisResult(
        analyzer_name="radon",
        file_path=Path("src/models.py"),
        pattern_type="high_complexity",
        severity=Severity.HIGH,
        category=AnalysisCategory.CODE_STRUCTURE,
        confidence=0.7,
        message="High cyclomatic complexity",
        evidence={"complexity": 15},
        remediation=["Refactor into smaller functions"],
    )


@pytest.fixture
def medium_finding():
    """Create a MEDIUM severity finding (should NOT be triaged unless pattern)."""
    return AnalysisResult(
        analyzer_name="radon",
        file_path=Path("src/utils.py"),
        pattern_type="moderate_complexity",
        severity=Severity.MEDIUM,
        category=AnalysisCategory.CODE_STRUCTURE,
        confidence=0.8,
        message="Moderate cyclomatic complexity",
        evidence={"complexity": 8},
        remediation=["Consider refactoring"],
    )


@pytest.fixture
def low_finding():
    """Create a LOW severity finding (should NOT be triaged)."""
    return AnalysisResult(
        analyzer_name="ai_slop",
        file_path=Path("src/helpers.py"),
        pattern_type="generic_naming",
        severity=Severity.LOW,
        category=AnalysisCategory.CODE_STRUCTURE,
        confidence=0.75,
        message="Generic variable name 'temp'",
        evidence={"indicators": ["generic_name"]},
        remediation=["Use more descriptive names"],
    )


@pytest.fixture
def cross_project_pattern():
    """Create a cross-project pattern (should always be triaged)."""
    return CrossProjectPattern(
        pattern_type="sql_injection_systemic",
        severity=Severity.HIGH,
        category=AnalysisCategory.SECURITY,
        projects_count=3,
        projects=["auth_service", "api_gateway", "data_loader"],
        message="SQL injection vulnerability found in 3 projects",
        projects_confidence=0.82,
        evidence={"affected_projects": 3},
    )


class TestPlannerTriageLogic:
    """Tests for Planner.triage() - automatic finding selection."""

    def test_triage_returns_triage_result(self, planner, critical_finding):
        """Test that triage() returns a TriageResult object."""
        result = planner.triage([critical_finding])
        assert isinstance(result, TriageResult)

    def test_triage_includes_all_findings(self, planner, critical_finding, medium_finding):
        """Test that triage result includes all input findings (no filtering of all_findings)."""
        findings = [critical_finding, medium_finding]
        result = planner.triage(findings)
        assert result.all_findings == findings
        assert len(result.all_findings) == 2

    def test_rule1_all_critical_selected(self, planner, critical_finding, medium_finding):
        """Rule 1: ALL CRITICAL findings go to LLM."""
        findings = [critical_finding, medium_finding]
        result = planner.triage(findings)

        assert critical_finding in result.llm_worthy_findings
        assert medium_finding not in result.llm_worthy_findings

    def test_rule2_high_confident_selected(
        self, planner, high_confident_finding, high_low_confidence_finding
    ):
        """Rule 2: HIGH findings with confidence >= 0.8 are selected."""
        findings = [high_confident_finding, high_low_confidence_finding]
        result = planner.triage(findings)

        assert high_confident_finding in result.llm_worthy_findings
        assert high_low_confidence_finding not in result.llm_worthy_findings

    def test_rule2_high_exactly_0_8_confidence(self, planner):
        """Rule 2: HIGH with exactly 0.8 confidence should be selected."""
        finding = AnalysisResult(
            analyzer_name="test",
            file_path=Path("test.py"),
            pattern_type="test_pattern",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            confidence=0.8,
            message="Test finding",
        )
        result = planner.triage([finding])
        assert finding in result.llm_worthy_findings

    def test_rule2_high_just_below_threshold(self, planner):
        """Rule 2: HIGH with 0.79 confidence should NOT be selected."""
        finding = AnalysisResult(
            analyzer_name="test",
            file_path=Path("test.py"),
            pattern_type="test_pattern",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            confidence=0.79,
            message="Test finding",
        )
        result = planner.triage([finding])
        assert finding not in result.llm_worthy_findings

    def test_rule3_patterns_always_selected(
        self, planner, medium_finding, cross_project_pattern
    ):
        """Rule 3: ALL CrossProjectPattern findings are converted and selected."""
        # Medium finding on its own would NOT be selected
        result = planner.triage([medium_finding], patterns=[cross_project_pattern])

        # Pattern should create an AnalysisResult that gets selected
        assert len(result.llm_worthy_findings) == 1
        assert result.llm_worthy_findings[0].pattern_type == "sql_injection_systemic"

    def test_rule3_pattern_converted_to_finding(self, planner, cross_project_pattern):
        """Rule 3: Patterns are converted to AnalysisResult for unified handling."""
        result = planner.triage([], patterns=[cross_project_pattern])

        assert len(result.llm_worthy_findings) == 1
        converted = result.llm_worthy_findings[0]

        assert converted.pattern_type == cross_project_pattern.pattern_type
        assert converted.severity == cross_project_pattern.severity
        assert converted.category == cross_project_pattern.category
        assert converted.confidence == cross_project_pattern.projects_confidence
        assert "[PATTERN]" in converted.message
        assert converted.file_path is None  # Patterns are corpus-level

    def test_rule4_limit_to_10_findings(self, planner):
        """Rule 4: Maximum 10 findings per audit (token budget)."""
        # Create 15 CRITICAL findings
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"file{i}.py"),
                pattern_type=f"pattern_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.9,
                message=f"Finding {i}",
            )
            for i in range(15)
        ]

        result = planner.triage(findings)
        assert len(result.llm_worthy_findings) == 10

    def test_rule4_respects_original_list(self, planner):
        """Rule 4: all_findings should still contain all 15 items."""
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"file{i}.py"),
                pattern_type=f"pattern_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.9,
                message=f"Finding {i}",
            )
            for i in range(15)
        ]

        result = planner.triage(findings)
        assert len(result.all_findings) == 15
        assert len(result.llm_worthy_findings) == 10

    def test_empty_findings_list(self, planner):
        """Test triage with empty findings list."""
        result = planner.triage([])
        assert result.llm_worthy_findings == []
        assert result.routing == {}

    def test_empty_patterns_list(self, planner, critical_finding):
        """Test that patterns=None is handled gracefully."""
        result = planner.triage([critical_finding], patterns=None)
        assert critical_finding in result.llm_worthy_findings


class TestPlannerRouting:
    """Tests for Planner.route_to_persona() - specialist assignment."""

    def test_security_routes_to_security_analyst(self, planner):
        """SECURITY category → security_analyst persona."""
        finding = AnalysisResult(
            analyzer_name="bandit",
            file_path=Path("src/auth.py"),
            pattern_type="sql_injection",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.SECURITY,
            confidence=0.95,
            message="Test",
        )
        persona = planner.route_to_persona(finding)
        assert persona == "security_analyst"

    def test_code_structure_routes_to_refactor_gpt(self, planner):
        """CODE_STRUCTURE category → refactor_gpt persona."""
        finding = AnalysisResult(
            analyzer_name="radon",
            file_path=Path("src/models.py"),
            pattern_type="high_complexity",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.8,
            message="Test",
        )
        persona = planner.route_to_persona(finding)
        assert persona == "refactor_gpt"

    def test_maintainability_routes_to_refactor_gpt(self, planner):
        """MAINTAINABILITY category → refactor_gpt persona."""
        finding = AnalysisResult(
            analyzer_name="radon",
            file_path=Path("src/models.py"),
            pattern_type="low_maintainability",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.MAINTAINABILITY,
            confidence=0.8,
            message="Test",
        )
        persona = planner.route_to_persona(finding)
        assert persona == "refactor_gpt"

    def test_performance_routes_to_performance_analyst(self, planner):
        """PERFORMANCE category → performance_analyst persona."""
        finding = AnalysisResult(
            analyzer_name="test",
            file_path=Path("src/slow.py"),
            pattern_type="inefficient_loop",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.PERFORMANCE,
            confidence=0.8,
            message="Test",
        )
        persona = planner.route_to_persona(finding)
        assert persona == "performance_analyst"

    def test_routing_added_to_result(self, planner, critical_finding, high_confident_finding):
        """Test that routing dict is populated in TriageResult."""
        findings = [critical_finding, high_confident_finding]
        result = planner.triage(findings)

        # Should have 2 entries in routing
        assert len(result.routing) == 2
        assert "hardcoded_password" in result.routing
        assert "sql_injection" in result.routing
        assert result.routing["hardcoded_password"] == "security_analyst"
        assert result.routing["sql_injection"] == "security_analyst"

    def test_routing_key_is_pattern_type(self, planner, critical_finding):
        """Test that routing dict uses pattern_type as key."""
        result = planner.triage([critical_finding])

        # Key should be pattern_type, not file_path or something else
        assert critical_finding.pattern_type in result.routing


class TestPlannerSeveritySorting:
    """Tests for _sort_by_severity() - critical findings prioritized in top-10 limit."""

    def test_severity_priority_critical_over_high(self, planner):
        """CRITICAL findings take priority over HIGH when limit is reached."""
        # Create 5 HIGH + 10 MEDIUM to trigger the 10-limit
        high_findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"high_{i}.py"),
                pattern_type=f"high_{i}",
                severity=Severity.HIGH,
                category=AnalysisCategory.SECURITY,
                confidence=0.85,
                message=f"High {i}",
            )
            for i in range(5)
        ]

        critical_findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"critical_{i}.py"),
                pattern_type=f"critical_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.9,
                message=f"Critical {i}",
            )
            for i in range(6)
        ]

        all_findings = high_findings + critical_findings
        result = planner.triage(all_findings)

        # All 6 CRITICAL should be included, no HIGH
        assert len(result.llm_worthy_findings) == 10
        critical_count = sum(
            1 for f in result.llm_worthy_findings if f.severity == Severity.CRITICAL
        )
        assert critical_count == 6


class TestPlannerTokenEstimation:
    """Tests for _estimate_tokens() - token budget calculation."""

    def test_token_estimate_base_plus_findings(self, planner, critical_finding):
        """Token estimate = base (100) + findings * 150."""
        result = planner.triage([critical_finding])

        # 1 finding: 100 + (1 * 150) = 250
        assert result.token_estimate == 250

    def test_token_estimate_multiple_findings(self, planner):
        """Test token estimation with multiple findings."""
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"file_{i}.py"),
                pattern_type=f"pattern_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.9,
                message=f"Finding {i}",
            )
            for i in range(5)
        ]

        result = planner.triage(findings)

        # 5 findings: 100 + (5 * 150) = 850
        assert result.token_estimate == 850

    def test_token_estimate_empty_findings(self, planner):
        """Token estimate for 0 findings = 100 base."""
        result = planner.triage([])
        assert result.token_estimate == 100

    def test_token_estimate_capped_at_10_findings(self, planner):
        """Token estimate should be for top 10 findings, not all."""
        findings = [
            AnalysisResult(
                analyzer_name="test",
                file_path=Path(f"file_{i}.py"),
                pattern_type=f"pattern_{i}",
                severity=Severity.CRITICAL,
                category=AnalysisCategory.SECURITY,
                confidence=0.9,
                message=f"Finding {i}",
            )
            for i in range(15)
        ]

        result = planner.triage(findings)

        # Should estimate for 10, not 15: 100 + (10 * 150) = 1600
        assert result.token_estimate == 1600
        assert len(result.llm_worthy_findings) == 10


class TestPlannerIntegration:
    """Integration tests combining multiple rules."""

    def test_mixed_severities_complex_scenario(
        self,
        planner,
        critical_finding,
        high_confident_finding,
        high_low_confidence_finding,
        medium_finding,
        low_finding,
        cross_project_pattern,
    ):
        """Test with mixed severities and patterns."""
        findings = [
            critical_finding,
            high_confident_finding,
            high_low_confidence_finding,
            medium_finding,
            low_finding,
        ]

        result = planner.triage(findings, patterns=[cross_project_pattern])

        # Should select:
        # - critical_finding (CRITICAL)
        # - high_confident_finding (HIGH + 0.85 conf)
        # - pattern (converted to HIGH finding)
        assert len(result.llm_worthy_findings) == 3
        assert critical_finding in result.llm_worthy_findings
        assert high_confident_finding in result.llm_worthy_findings
        assert high_low_confidence_finding not in result.llm_worthy_findings
        assert medium_finding not in result.llm_worthy_findings
        assert low_finding not in result.llm_worthy_findings

    def test_routing_includes_all_worthy_findings(
        self, planner, critical_finding, high_confident_finding
    ):
        """Test that routing dict has entry for every worthy finding."""
        findings = [critical_finding, high_confident_finding]
        result = planner.triage(findings)

        # Should have entries for both
        assert len(result.routing) == len(result.llm_worthy_findings)
        for finding in result.llm_worthy_findings:
            assert finding.pattern_type in result.routing

    def test_multiple_patterns_combined_with_findings(self, planner, critical_finding):
        """Test with multiple patterns and findings combined."""
        pattern1 = CrossProjectPattern(
            pattern_type="pattern1",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            projects_count=2,
            projects=["proj1", "proj2"],
            message="Pattern 1",
            projects_confidence=0.85,
        )

        pattern2 = CrossProjectPattern(
            pattern_type="pattern2",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            projects_count=3,
            projects=["proj1", "proj2", "proj3"],
            message="Pattern 2",
            projects_confidence=0.8,
        )

        result = planner.triage([critical_finding], patterns=[pattern1, pattern2])

        # Should have: 1 CRITICAL + 2 patterns = 3 worthy
        assert len(result.llm_worthy_findings) == 3

        # All should have routing entries
        assert len(result.routing) == 3
