import json
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from ..core.models import (
    AnalysisResult,
    CrossProjectPattern,
    EnrichedReport,
    ExpertRecommendation,
    TriageResult,
    ExtractedArtifacts,
)
from ..providers.base import TextProvider
from ..prompt_registry.registry import PromptRegistry
from .planning import Planner
from .artifact_parser import ArtifactParser

_logger = logging.getLogger(__name__)


class AuditAgent:
    """
    Phase 5 Orchestrator: Intelligently routes findings to specialist personas.

    Pipeline:
    1. Planner: Automatic triage (which findings are LLM-worthy)
    2. Routing: Route each finding to appropriate specialist (security_analyst, refactor_gpt, etc)
    3. LLM Analysis: Call specialist personas with context-aware prompts
    4. Artifact Extraction: Parse LLM responses into structured recommendations
    5. Report Generation: Combine findings, patterns, and expert recommendations
    """

    def __init__(
        self,
        llm_provider: TextProvider,
        prompt_registry: PromptRegistry,
        artifact_parser: Optional[ArtifactParser] = None,
    ):
        """
        Initialize AuditAgent with LLM provider, prompt registry, and artifact parser.

        Args:
            llm_provider: TextProvider instance for LLM calls
            prompt_registry: PromptRegistry for loading specialist prompts
            artifact_parser: Optional ArtifactParser for extracting structured artifacts
                           If None, creates default parser with LLM provider
        """
        if llm_provider is None:
            raise ValueError("LLM provider is required")
        if prompt_registry is None:
            raise ValueError("PromptRegistry is required")

        self._llm_provider = llm_provider
        self._prompt_registry = prompt_registry
        self._planner = Planner()

        # Create parser if not provided (uses heuristic parsing by default, not LLM)
        # Phase 5.3 will enable LLM-based structured extraction
        self._artifact_parser = artifact_parser or ArtifactParser(llm_provider=None)

    def run(
        self,
        findings: List[AnalysisResult],
        patterns: Optional[List[CrossProjectPattern]] = None,
    ) -> EnrichedReport:
        """
        Orchestrate Phase 5 analysis with automatic triage and LLM routing.

        Args:
            findings: All static analysis findings from Phase 1
            patterns: Cross-project patterns from Phase 4 (optional)

        Returns:
            EnrichedReport with findings, patterns, triage results, and expert recommendations
        """
        if patterns is None:
            patterns = []

        start_time = datetime.now()

        # Step 1: Automatic Triage
        _logger.info(f"Phase 5: Starting orchestration with {len(findings)} findings")
        triage_result = self._planner.triage(findings, patterns)
        _logger.info(
            f"Triage complete: {len(triage_result.llm_worthy_findings)} findings "
            f"selected for LLM (~{triage_result.token_estimate} tokens)"
        )

        # Step 2: Expert Analysis (call LLM for each worthy finding)
        expert_recommendations = []
        for finding in triage_result.llm_worthy_findings:
            try:
                persona = triage_result.routing.get(finding.pattern_type)
                if not persona:
                    _logger.warning(
                        f"No persona routing found for {finding.pattern_type}, skipping"
                    )
                    continue

                recommendation = self._analyze_with_persona(finding, persona)
                expert_recommendations.append(recommendation)
                _logger.debug(
                    f"Generated expert recommendation from {persona} for {finding.pattern_type}"
                )
            except Exception as e:
                _logger.error(
                    f"Failed to generate recommendation for {finding.pattern_type}: {e}"
                )
                continue

        # Step 3: Build Enriched Report
        execution_time = (datetime.now() - start_time).total_seconds()
        enriched_report = EnrichedReport(
            findings=findings,
            patterns=patterns,
            triage=triage_result,
            expert_recommendations=expert_recommendations,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
        )

        _logger.info(
            f"Phase 5 complete: Generated {len(expert_recommendations)} "
            f"expert recommendations in {execution_time:.2f}s"
        )

        return enriched_report

    def _analyze_with_persona(
        self, finding: AnalysisResult, persona: str
    ) -> ExpertRecommendation:
        """
        Analyze a finding using a specific specialist persona with wiki intelligence.

        Args:
            finding: The AnalysisResult to analyze
            persona: The specialist persona name (e.g., 'security_analyst')

        Returns:
            ExpertRecommendation with LLM-generated insights
        """
        # Step 1: Load wiki intelligence as system context
        system_context = self._load_wiki_intelligence()

        # Step 2: Render specialist prompt with finding context
        specialist_prompt = self._render_specialist_prompt(finding, persona)

        # Step 3: Combine system context + specialist prompt
        full_prompt = f"{system_context}\n\n---\n\n{specialist_prompt}"

        # Step 4: Call LLM with combined prompt (wiki intelligence + specialist)
        llm_response = self._llm_provider.generate(
            prompt=full_prompt,
            temperature=0.7,
            max_tokens=1000,
        )

        analysis_text = llm_response.get("response", "")

        # Step 5: Extract artifacts (structured data) from LLM response
        artifacts = self._extract_artifacts(analysis_text, persona)

        # Step 6: Create ExpertRecommendation object
        recommendation = ExpertRecommendation(
            finding_id=f"{finding.pattern_type}_{finding.file_path or 'corpus'}",
            persona=persona,
            analysis=analysis_text,
            artifacts=artifacts,
            confidence=0.8,  # Conservative default for LLM outputs
        )

        return recommendation

    def _render_specialist_prompt(self, finding: AnalysisResult, persona: str) -> str:
        """
        Render a specialist prompt with finding context.

        Args:
            finding: The finding to analyze
            persona: The specialist persona

        Returns:
            Rendered prompt text
        """
        # Format finding as context
        finding_context = {
            "pattern_type": finding.pattern_type,
            "severity": finding.severity.value,
            "category": finding.category.value,
            "message": finding.message,
            "file_path": str(finding.file_path) if finding.file_path else None,
            "line_start": finding.line_start,
            "line_end": finding.line_end,
            "evidence": finding.evidence,
            "remediation": finding.remediation,
        }

        # Try to render specialist prompt from registry
        try:
            rendered = self._prompt_registry.render(
                prompt_id=persona,
                variables={"finding": json.dumps(finding_context, indent=2)},
            )
            return rendered
        except Exception as e:
            # Fallback to generic prompt if specialist prompt not found
            _logger.warning(
                f"Could not render specialist prompt '{persona}': {e}, using fallback"
            )
            return self._generic_specialist_prompt(finding, persona)

    def _generic_specialist_prompt(
        self, finding: AnalysisResult, persona: str
    ) -> str:
        """
        Generate a generic specialist prompt when registry lookup fails.

        Args:
            finding: The finding to analyze
            persona: The specialist persona

        Returns:
            Generic specialist prompt
        """
        persona_roles = {
            "security_analyst": "security expert",
            "refactor_gpt": "code refactoring specialist",
            "performance_analyst": "performance optimization expert",
            "general_analyst": "code analyst",
        }

        role = persona_roles.get(persona, "code analyst")

        prompt = f"""You are a {role}. Analyze the following code finding and provide actionable recommendations.

Finding Type: {finding.pattern_type}
Severity: {finding.severity.value}
Category: {finding.category.value}
File: {finding.file_path or 'N/A (corpus-level pattern)'}
Message: {finding.message}

Evidence: {json.dumps(finding.evidence, indent=2)}

Please provide:
1. A concise explanation of the issue
2. Specific, actionable remediation steps
3. Code examples (if applicable)
4. Impact assessment

Format your response as a structured analysis."""

        return prompt

    def _load_wiki_intelligence(self) -> str:
        """
        Load wiki intelligence (CLEAR Framework + God Object Detection) as system context.

        Returns:
            Combined system context string with CLEAR and God Object prompts
        """
        try:
            # Load CLEAR Framework context
            clear_context = self._prompt_registry.render(
                prompt_id="audit_context_clear",
                variables={}
            )
        except Exception as e:
            _logger.warning(
                f"Failed to load CLEAR Framework context: {e}, using empty context"
            )
            clear_context = ""

        try:
            # Load God Object Detection context
            god_object_context = self._prompt_registry.render(
                prompt_id="audit_context_god_object",
                variables={}
            )
        except Exception as e:
            _logger.warning(
                f"Failed to load God Object Detection context: {e}, using empty context"
            )
            god_object_context = ""

        # Combine contexts
        if clear_context and god_object_context:
            system_context = f"# System Context: Wiki Intelligence\n\n{clear_context}\n\n---\n\n{god_object_context}"
        elif clear_context:
            system_context = f"# System Context: Wiki Intelligence\n\n{clear_context}"
        elif god_object_context:
            system_context = f"# System Context: Wiki Intelligence\n\n{god_object_context}"
        else:
            system_context = "# System Context: Wiki Intelligence\n\n(No wiki context available)"

        _logger.debug(
            f"Loaded wiki intelligence: {len(clear_context)} chars (CLEAR), "
            f"{len(god_object_context)} chars (God Object)"
        )

        return system_context

    def _extract_artifacts(self, analysis_text: str, persona: str) -> ExtractedArtifacts:
        """
        Extract structured artifacts from LLM analysis response using ArtifactParser.

        Args:
            analysis_text: The LLM response text
            persona: The specialist persona

        Returns:
            ExtractedArtifacts with patches and tests lists
        """
        try:
            # Use the artifact parser to extract structured data
            artifacts = self._artifact_parser.parse(analysis_text)
            _logger.debug(
                f"Extracted artifacts from {persona}: "
                f"{len(artifacts.patches)} patches, {len(artifacts.tests)} tests"
            )
            return artifacts
        except Exception as e:
            _logger.warning(
                f"Failed to extract artifacts from {persona} response: {e}, "
                f"returning empty artifacts"
            )
            return ExtractedArtifacts(patches=[], tests=[])


__all__ = ["AuditAgent"]
