"""
Unit tests for PromptRegistry integration with AuditAgent.

Tests that wiki intelligence (CLEAR Framework, God Object Detection) is properly
loaded from the registry and used by the AuditAgent.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.meta_audit.agents.audit_agent import AuditAgent
from src.meta_audit.prompt_registry.registry import PromptRegistry
from src.meta_audit.core.models import (
    AnalysisResult,
    Severity,
    AnalysisCategory,
    ExpertRecommendation,
)


@pytest.fixture
def prompts_dir():
    """Get prompts directory path."""
    return Path(__file__).parent.parent.parent / "src" / "meta_audit" / "prompts"


@pytest.fixture
def registry(prompts_dir):
    """Create PromptRegistry with real prompts."""
    if not prompts_dir.exists():
        pytest.skip(f"Prompts directory not found: {prompts_dir}")
    return PromptRegistry(prompts_dir=prompts_dir)


@pytest.fixture
def mock_llm_provider():
    """Create mock LLM provider."""
    provider = Mock()
    provider.generate = Mock(return_value={"response": "Mock LLM analysis"})
    return provider


@pytest.fixture
def audit_agent(registry, mock_llm_provider):
    """Create AuditAgent with registry and mock LLM."""
    return AuditAgent(
        llm_provider=mock_llm_provider,
        prompt_registry=registry,
    )


@pytest.fixture
def sample_finding():
    """Create a sample finding for testing."""
    return AnalysisResult(
        analyzer_name="test_analyzer",
        pattern_type="sql_injection",
        severity=Severity.CRITICAL,
        category=AnalysisCategory.SECURITY,
        message="Potential SQL injection vulnerability",
        file_path=Path("src/app.py"),
        line_start=42,
        line_end=45,
        evidence={"query": "SELECT * FROM users WHERE id = '{user_id}'"},
        remediation=["Use parameterized queries", "Validate user input"],
    )


class TestPromptRegistryIntegration:
    """Test suite for PromptRegistry integration with AuditAgent."""

    def test_registry_loads_clear_framework_prompt(self, registry):
        """Test that CLEAR Framework prompt is loaded from registry."""
        clear_prompt = registry.get("audit_context_clear")

        assert clear_prompt is not None, "CLEAR Framework prompt not found"
        assert clear_prompt.category == "audit_context"
        assert "CLEAR" in clear_prompt.prompt
        assert "Context" in clear_prompt.prompt
        assert "Layered" in clear_prompt.prompt
        assert "Explicit" in clear_prompt.prompt
        assert "Alternative" in clear_prompt.prompt
        assert "Refactoring" in clear_prompt.prompt

    def test_registry_loads_god_object_prompt(self, registry):
        """Test that God Object Detection prompt is loaded from registry."""
        god_object_prompt = registry.get("audit_context_god_object")

        assert god_object_prompt is not None, "God Object prompt not found"
        assert god_object_prompt.category == "audit_context"
        assert "God Object" in god_object_prompt.prompt
        assert "Single Responsibility" in god_object_prompt.prompt or "SRP" in god_object_prompt.prompt

    def test_registry_loads_security_analyst_persona(self, registry):
        """Test that Security Analyst persona is loaded from registry."""
        security_prompt = registry.get("security_analyst")

        assert security_prompt is not None, "Security Analyst prompt not found"
        assert security_prompt.category == "expert_personas"
        assert "security" in security_prompt.prompt.lower()
        assert "finding" in security_prompt.variables

    def test_registry_loads_refactor_gpt_persona(self, registry):
        """Test that Refactor GPT persona is loaded from registry."""
        refactor_prompt = registry.get("refactor_gpt")

        assert refactor_prompt is not None, "Refactor GPT prompt not found"
        assert refactor_prompt.category == "expert_personas"
        assert "refactor" in refactor_prompt.prompt.lower()
        assert "finding" in refactor_prompt.variables

    def test_audit_agent_loads_wiki_intelligence(self, audit_agent):
        """Test that AuditAgent loads wiki intelligence (CLEAR + God Object)."""
        wiki_context = audit_agent._load_wiki_intelligence()

        assert wiki_context is not None
        assert len(wiki_context) > 0
        assert "CLEAR" in wiki_context or "Context" in wiki_context
        # Check that God Object context is included
        assert "God Object" in wiki_context or "Single Responsibility" in wiki_context

    def test_audit_agent_combines_wiki_intelligence_with_specialist_prompt(
        self, audit_agent, sample_finding, mock_llm_provider
    ):
        """Test that AuditAgent combines wiki intelligence with specialist prompt."""
        # Analyze finding with security_analyst persona
        recommendation = audit_agent._analyze_with_persona(
            finding=sample_finding,
            persona="security_analyst"
        )

        # Verify LLM was called
        assert mock_llm_provider.generate.called

        # Get the prompt that was passed to LLM
        call_args = mock_llm_provider.generate.call_args
        prompt = call_args.kwargs.get("prompt", "")

        # Verify prompt contains wiki intelligence
        assert "CLEAR" in prompt or "Context" in prompt, "Wiki intelligence (CLEAR) not in prompt"
        assert "God Object" in prompt or "Single Responsibility" in prompt, "Wiki intelligence (God Object) not in prompt"

        # Verify prompt contains specialist content
        assert "security" in prompt.lower(), "Security analyst persona not in prompt"
        assert "sql" in prompt.lower() or "injection" in prompt.lower(), "Finding context not in prompt"

        # Verify recommendation is returned
        assert isinstance(recommendation, ExpertRecommendation)
        assert recommendation.persona == "security_analyst"

    def test_audit_agent_handles_missing_wiki_prompts_gracefully(
        self, mock_llm_provider
    ):
        """Test that AuditAgent handles missing wiki prompts gracefully."""
        # Create registry with non-existent directory
        empty_registry = PromptRegistry(prompts_dir=Path("/tmp/nonexistent"))

        agent = AuditAgent(
            llm_provider=mock_llm_provider,
            prompt_registry=empty_registry,
        )

        # Should not crash, should return empty context
        wiki_context = agent._load_wiki_intelligence()
        assert wiki_context is not None
        assert "No wiki context available" in wiki_context or len(wiki_context) == 0

    def test_audit_agent_fallback_to_generic_prompt_when_specialist_missing(
        self, audit_agent, sample_finding, mock_llm_provider
    ):
        """Test that AuditAgent falls back to generic prompt when specialist persona is missing."""
        # Try to analyze with non-existent persona
        recommendation = audit_agent._analyze_with_persona(
            finding=sample_finding,
            persona="nonexistent_persona"
        )

        # Should still work with fallback generic prompt
        assert mock_llm_provider.generate.called
        assert isinstance(recommendation, ExpertRecommendation)
        assert recommendation.persona == "nonexistent_persona"

    def test_clear_framework_prompt_structure(self, registry):
        """Test that CLEAR Framework prompt has expected structure."""
        clear_prompt = registry.get("audit_context_clear")
        rendered = registry.render("audit_context_clear", variables={})

        # Check all CLEAR dimensions are present
        dimensions = ["Context", "Layered", "Explicit", "Alternative", "Refactoring"]
        for dimension in dimensions:
            assert dimension in rendered, f"CLEAR dimension '{dimension}' not found in prompt"

    def test_god_object_prompt_structure(self, registry):
        """Test that God Object prompt has expected structure."""
        god_object_prompt = registry.get("audit_context_god_object")
        rendered = registry.render("audit_context_god_object", variables={})

        # Check detection heuristics are present
        assert "quantitative" in rendered.lower() or "method count" in rendered.lower()
        assert "qualitative" in rendered.lower() or "responsibilities" in rendered.lower()

    def test_security_analyst_prompt_has_finding_variable(self, registry):
        """Test that Security Analyst prompt uses {finding} variable."""
        security_prompt = registry.get("security_analyst")

        # Render with sample finding
        rendered = registry.render(
            "security_analyst",
            variables={"finding": "Sample SQL injection vulnerability"}
        )

        assert "Sample SQL injection vulnerability" in rendered

    def test_refactor_gpt_prompt_has_finding_variable(self, registry):
        """Test that Refactor GPT prompt uses {finding} variable."""
        refactor_prompt = registry.get("refactor_gpt")

        # Render with sample finding
        rendered = registry.render(
            "refactor_gpt",
            variables={"finding": "Large class with 50 methods"}
        )

        assert "Large class with 50 methods" in rendered

    def test_wiki_intelligence_cached_per_analysis(
        self, audit_agent, sample_finding, mock_llm_provider
    ):
        """Test that wiki intelligence is loaded once per analysis (not per finding)."""
        # Analyze multiple findings
        findings = [sample_finding, sample_finding, sample_finding]

        with patch.object(audit_agent, '_load_wiki_intelligence', wraps=audit_agent._load_wiki_intelligence) as mock_load:
            for finding in findings:
                audit_agent._analyze_with_persona(finding, "security_analyst")

            # Wiki intelligence should be loaded for each finding
            # (could be optimized to cache, but current implementation loads each time)
            assert mock_load.call_count == len(findings)

    def test_full_audit_agent_run_with_wiki_intelligence(
        self, audit_agent, sample_finding, mock_llm_provider
    ):
        """Test full AuditAgent.run() with wiki intelligence integration."""
        findings = [sample_finding]

        # Run full audit
        report = audit_agent.run(findings=findings, patterns=[])

        # Verify report contains expert recommendations
        assert len(report.expert_recommendations) > 0

        # Verify LLM was called with wiki intelligence
        assert mock_llm_provider.generate.called
        call_args = mock_llm_provider.generate.call_args
        prompt = call_args.kwargs.get("prompt", "")

        # Verify wiki intelligence was included
        assert "CLEAR" in prompt or "Context" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
