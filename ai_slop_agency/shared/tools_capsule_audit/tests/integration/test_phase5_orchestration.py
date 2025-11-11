"""Integration tests for Phase 5 LLM orchestration (Planner + AuditAgent)."""

import pytest

pytestmark = [pytest.mark.phase5, pytest.mark.integration]
from pathlib import Path
from unittest.mock import MagicMock, patch

from meta_audit.core.models import (
    AnalysisResult,
    CrossProjectPattern,
    Severity,
    AnalysisCategory,
    EnrichedReport,
    ExpertRecommendation,
)
from meta_audit.agents.audit_agent import AuditAgent
from meta_audit.agents.planning import Planner
from meta_audit.providers.base import TextProvider
from meta_audit.prompt_registry.registry import PromptRegistry


@pytest.fixture
def sample_findings():
    """Create a mix of findings for testing triage."""
    return [
        # CRITICAL (should be selected)
        AnalysisResult(
            analyzer_name="bandit",
            file_path=Path("src/auth.py"),
            pattern_type="hardcoded_password",
            severity=Severity.CRITICAL,
            category=AnalysisCategory.SECURITY,
            confidence=0.95,
            message="Use of hardcoded password",
            evidence={"test_id": "B105"},
        ),
        # HIGH + high confidence (should be selected)
        AnalysisResult(
            analyzer_name="bandit",
            file_path=Path("src/db/queries.py"),
            pattern_type="sql_injection",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            confidence=0.85,
            message="Potential SQL injection vulnerability",
            evidence={"test_id": "B608"},
        ),
        # HIGH + low confidence (should NOT be selected)
        AnalysisResult(
            analyzer_name="radon",
            file_path=Path("src/models.py"),
            pattern_type="high_complexity",
            severity=Severity.HIGH,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.7,
            message="High cyclomatic complexity",
            evidence={"complexity": 15},
        ),
        # MEDIUM (should NOT be selected)
        AnalysisResult(
            analyzer_name="radon",
            file_path=Path("src/utils.py"),
            pattern_type="moderate_complexity",
            severity=Severity.MEDIUM,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.8,
            message="Moderate cyclomatic complexity",
            evidence={"complexity": 8},
        ),
        # LOW (should NOT be selected)
        AnalysisResult(
            analyzer_name="ai_slop",
            file_path=Path("src/helpers.py"),
            pattern_type="generic_naming",
            severity=Severity.LOW,
            category=AnalysisCategory.CODE_STRUCTURE,
            confidence=0.75,
            message="Generic variable name",
            evidence={"indicators": ["temp"]},
        ),
    ]


@pytest.fixture
def sample_patterns():
    """Create cross-project patterns for testing."""
    return [
        CrossProjectPattern(
            pattern_type="sql_injection_systemic",
            severity=Severity.HIGH,
            category=AnalysisCategory.SECURITY,
            projects_count=3,
            projects=["auth_service", "api_gateway", "data_loader"],
            message="SQL injection found in 3 projects",
            projects_confidence=0.85,
            evidence={"affected_projects": 3},
        ),
    ]


@pytest.fixture
def mock_llm_provider():
    """Create a mock TextProvider for testing."""
    provider = MagicMock(spec=TextProvider)
    provider.generate.return_value = {
        "response": "This is a sample LLM analysis with recommendations.",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timestamp": "2025-11-10T12:00:00",
        "provider": "openai",
    }
    return provider


@pytest.fixture
def mock_prompt_registry():
    """Create a real PromptRegistry loaded with wiki-based prompts."""
    from pathlib import Path
    prompts_dir = Path(__file__).parent.parent.parent / "meta_audit" / "prompts"

    # If prompts directory exists, use real registry; otherwise mock
    if prompts_dir.exists():
        registry = PromptRegistry(prompts_dir=prompts_dir)
    else:
        # Fallback to mock for environments where prompts dir doesn't exist
        registry = MagicMock(spec=PromptRegistry)
        registry.render.side_effect = ValueError("Prompt not found")

    return registry


@pytest.fixture
def audit_agent(mock_llm_provider, mock_prompt_registry):
    """Create an AuditAgent with mocked dependencies."""
    return AuditAgent(
        llm_provider=mock_llm_provider,
        prompt_registry=mock_prompt_registry,
    )


class TestPhase5Orchestration:
    """Integration tests for Phase 5 full pipeline."""

    def test_audit_agent_initialization(self, mock_llm_provider, mock_prompt_registry):
        """Test AuditAgent initialization."""
        agent = AuditAgent(
            llm_provider=mock_llm_provider,
            prompt_registry=mock_prompt_registry,
        )
        assert agent is not None
        assert agent._llm_provider == mock_llm_provider
        assert agent._prompt_registry == mock_prompt_registry

    def test_audit_agent_run_returns_enriched_report(
        self, audit_agent, sample_findings, sample_patterns
    ):
        """Test that run() returns EnrichedReport."""
        result = audit_agent.run(sample_findings, sample_patterns)
        assert isinstance(result, EnrichedReport)

    def test_enriched_report_contains_all_findings(
        self, audit_agent, sample_findings, sample_patterns
    ):
        """Test that EnrichedReport.findings contains ALL original findings (no filtering)."""
        result = audit_agent.run(sample_findings, sample_patterns)

        assert result.findings == sample_findings
        assert len(result.findings) == 5  # All original findings preserved

    def test_enriched_report_contains_patterns(
        self, audit_agent, sample_findings, sample_patterns
    ):
        """Test that EnrichedReport.patterns contains input patterns."""
        result = audit_agent.run(sample_findings, sample_patterns)

        assert result.patterns == sample_patterns
        assert len(result.patterns) == 1

    def test_enriched_report_contains_triage_result(
        self, audit_agent, sample_findings
    ):
        """Test that EnrichedReport.triage contains TriageResult."""
        result = audit_agent.run(sample_findings)

        assert result.triage is not None
        # Triage should have selected 1 CRITICAL + 1 HIGH confident = 2
        assert len(result.triage.llm_worthy_findings) == 2
        assert len(result.triage.routing) == 2

    def test_triage_selects_correct_findings(self, audit_agent, sample_findings):
        """Test that triage selects exactly the right findings."""
        result = audit_agent.run(sample_findings)

        triage = result.triage
        worthy_patterns = {f.pattern_type for f in triage.llm_worthy_findings}

        # Should include CRITICAL and HIGH+confident
        assert "hardcoded_password" in worthy_patterns  # CRITICAL
        assert "sql_injection" in worthy_patterns  # HIGH + 0.85 confidence

        # Should NOT include others
        assert "high_complexity" not in worthy_patterns  # HIGH + 0.7 confidence
        assert "moderate_complexity" not in worthy_patterns  # MEDIUM
        assert "generic_naming" not in worthy_patterns  # LOW

    def test_triage_includes_patterns_as_findings(
        self, audit_agent, sample_findings, sample_patterns
    ):
        """Test that patterns are included in triage.llm_worthy_findings."""
        result = audit_agent.run(sample_findings, sample_patterns)

        triage = result.triage
        worthy_patterns = {f.pattern_type for f in triage.llm_worthy_findings}

        # Pattern should be converted and included
        assert "sql_injection_systemic" in worthy_patterns

    def test_expert_recommendations_only_for_worthy_findings(
        self, audit_agent, sample_findings
    ):
        """Test that expert recommendations only exist for triaged findings."""
        result = audit_agent.run(sample_findings)

        # Should have 2 recommendations (1 CRITICAL + 1 HIGH confident)
        assert len(result.expert_recommendations) == 2

        # All recommendations should be for worthy findings
        recommendation_ids = {r.finding_id for r in result.expert_recommendations}

        # Check that both worthy findings are represented
        assert any("hardcoded_password" in rid for rid in recommendation_ids)
        assert any("sql_injection" in rid for rid in recommendation_ids)

    def test_expert_recommendations_have_correct_structure(
        self, audit_agent, sample_findings
    ):
        """Test that ExpertRecommendation objects have all required fields."""
        result = audit_agent.run(sample_findings)

        for rec in result.expert_recommendations:
            assert isinstance(rec, ExpertRecommendation)
            assert rec.finding_id is not None
            assert rec.persona is not None
            assert rec.analysis is not None
            # artifacts is now ExtractedArtifacts (structured), not dict
            assert hasattr(rec.artifacts, 'patches')
            assert hasattr(rec.artifacts, 'tests')
            assert isinstance(rec.artifacts.patches, list)
            assert isinstance(rec.artifacts.tests, list)
            assert 0.0 <= rec.confidence <= 1.0

    def test_routing_maps_findings_to_personas(self, audit_agent, sample_findings):
        """Test that routing dict correctly maps findings to personas."""
        result = audit_agent.run(sample_findings)

        routing = result.triage.routing

        # SECURITY findings should route to security_analyst
        assert routing["hardcoded_password"] == "security_analyst"
        assert routing["sql_injection"] == "security_analyst"

    def test_llm_provider_called_for_worthy_findings(
        self, mock_llm_provider, mock_prompt_registry, sample_findings
    ):
        """Test that LLM provider is called for each worthy finding."""
        agent = AuditAgent(mock_llm_provider, mock_prompt_registry)
        agent.run(sample_findings)

        # Should be called twice (1 CRITICAL + 1 HIGH confident)
        assert mock_llm_provider.generate.call_count == 2

    def test_execution_time_is_tracked(self, audit_agent, sample_findings):
        """Test that execution time is recorded."""
        result = audit_agent.run(sample_findings)

        assert result.execution_time >= 0.0
        assert isinstance(result.execution_time, float)

    def test_timestamp_is_set(self, audit_agent, sample_findings):
        """Test that timestamp is set on result."""
        result = audit_agent.run(sample_findings)

        assert result.timestamp is not None
        assert isinstance(result.timestamp, str)

    def test_empty_findings_list(self, audit_agent):
        """Test that empty findings list is handled gracefully."""
        result = audit_agent.run([])

        assert result.findings == []
        assert result.triage.llm_worthy_findings == []
        assert result.expert_recommendations == []

    def test_findings_with_no_patterns(self, audit_agent, sample_findings):
        """Test that patterns can be None."""
        result = audit_agent.run(sample_findings, patterns=None)

        assert result.patterns == []
        assert result.triage is not None

    def test_recommendations_include_analysis_text(
        self, audit_agent, sample_findings
    ):
        """Test that expert recommendations include LLM analysis text."""
        result = audit_agent.run(sample_findings)

        for rec in result.expert_recommendations:
            assert len(rec.analysis) > 0
            assert "sample" in rec.analysis.lower()  # Contains mock response

    def test_artifact_extraction_status(self, audit_agent, sample_findings):
        """Test that artifacts contain patches and tests lists."""
        result = audit_agent.run(sample_findings)

        for rec in result.expert_recommendations:
            # artifacts is now ExtractedArtifacts with patches and tests
            assert hasattr(rec.artifacts, 'patches')
            assert hasattr(rec.artifacts, 'tests')
            assert isinstance(rec.artifacts.patches, list)
            assert isinstance(rec.artifacts.tests, list)


class TestTokenEstimation:
    """Tests for token estimation accuracy."""

    def test_token_estimate_in_triage_result(self, audit_agent, sample_findings):
        """Test that token estimate is calculated in triage result."""
        result = audit_agent.run(sample_findings)

        token_estimate = result.triage.token_estimate
        # 2 findings: 100 + (2 * 150) = 400
        assert token_estimate == 400

    def test_token_estimate_with_patterns(self, audit_agent, sample_findings, sample_patterns):
        """Test token estimate includes pattern findings."""
        result = audit_agent.run(sample_findings, sample_patterns)

        token_estimate = result.triage.token_estimate
        # 3 findings (1 CRITICAL + 1 HIGH + 1 pattern): 100 + (3 * 150) = 550
        assert token_estimate == 550


class TestErrorHandling:
    """Tests for error handling in Phase 5."""

    def test_llm_provider_failure_handled_gracefully(
        self, mock_llm_provider, mock_prompt_registry, sample_findings
    ):
        """Test that LLM provider failure doesn't crash orchestration."""
        mock_llm_provider.generate.side_effect = Exception("API Error")

        agent = AuditAgent(mock_llm_provider, mock_prompt_registry)
        result = agent.run(sample_findings)

        # Should still return valid report even if LLM fails
        assert isinstance(result, EnrichedReport)
        # But should have fewer recommendations
        assert len(result.expert_recommendations) < len(result.triage.llm_worthy_findings)

    def test_missing_prompt_uses_fallback(
        self, mock_llm_provider, mock_prompt_registry, sample_findings
    ):
        """Test that missing specialist prompts use fallback."""
        # Registry.render will raise exception
        agent = AuditAgent(mock_llm_provider, mock_prompt_registry)
        result = agent.run(sample_findings)

        # Should still generate recommendations using fallback prompts
        assert len(result.expert_recommendations) == 2


class TestCrossProjectPatternHandling:
    """Tests for cross-project pattern handling in Phase 5."""

    def test_pattern_converted_to_finding(self, audit_agent, sample_patterns):
        """Test that patterns are converted to AnalysisResult."""
        result = audit_agent.run([], sample_patterns)

        # Pattern should be in llm_worthy_findings
        assert len(result.triage.llm_worthy_findings) == 1

        converted = result.triage.llm_worthy_findings[0]
        pattern = sample_patterns[0]

        assert converted.pattern_type == pattern.pattern_type
        assert converted.severity == pattern.severity
        assert converted.category == pattern.category
        assert converted.file_path is None  # Corpus-level

    def test_pattern_marked_with_pattern_prefix(
        self, audit_agent, sample_patterns
    ):
        """Test that converted patterns have [PATTERN] prefix in message."""
        result = audit_agent.run([], sample_patterns)

        converted = result.triage.llm_worthy_findings[0]
        assert "[PATTERN]" in converted.message
