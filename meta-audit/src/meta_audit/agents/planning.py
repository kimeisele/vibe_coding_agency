"""
Planner: Automatic Triage Logic for Phase 5 Orchestration

The Planner is the "brain" of Phase 5. It automatically decides:
1. Which findings are LLM-worthy (data-driven triage)
2. Which specialist persona should analyze each finding (routing)

This ensures token-efficiency: only critical, high-confidence, and
cross-project findings go to expensive LLM calls.
"""

import logging
from typing import List, Dict

from ..core.models import (
    AnalysisResult,
    CrossProjectPattern,
    TriageResult,
    Severity,
    AnalysisCategory,
)

logger = logging.getLogger(__name__)


class Planner:
    """
    Intelligent triage and routing for Phase 5 LLM orchestration.

    Responsibilities:
    1. Triage: Decide which findings warrant LLM analysis
    2. Routing: Decide which persona specializes in each finding
    3. Token budgeting: Estimate tokens needed for the batch

    Rules for LLM-worthiness:
    - ALL CRITICAL findings
    - HIGH findings with confidence >= 0.8
    - ALL CrossProjectPattern findings (systemic issues)
    - Maximum 10 findings per audit (token budget)
    """

    def __init__(self):
        """Initialize the Planner."""
        pass

    def triage(
        self,
        findings: List[AnalysisResult],
        patterns: List[CrossProjectPattern] = None,
    ) -> TriageResult:
        """
        Automatic triage: decide which findings need LLM analysis.

        Args:
            findings: All findings from Phase 1 static analysis
            patterns: Cross-project patterns from Phase 4 (optional)

        Returns:
            TriageResult with llm_worthy_findings and routing
        """
        if patterns is None:
            patterns = []

        llm_worthy = []
        routing = {}

        # Rule 1: All CRITICAL findings go to LLM
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        llm_worthy.extend(critical_findings)

        # Rule 2: HIGH findings with confidence >= 0.8 go to LLM
        high_confident = [
            f
            for f in findings
            if f.severity == Severity.HIGH and f.confidence >= 0.8
        ]
        llm_worthy.extend(high_confident)

        # Rule 3: Convert all patterns to findings (systemic issues are always worthy)
        pattern_findings = [self._pattern_to_finding(p) for p in patterns]
        llm_worthy.extend(pattern_findings)

        # Rule 4: Limit to top 10 (by severity rank)
        llm_worthy = self._sort_by_severity(llm_worthy)[:10]

        # Routing: decide which persona analyzes each
        for finding in llm_worthy:
            persona = self.route_to_persona(finding)
            # Use pattern_type as key (unique identifier)
            routing[finding.pattern_type] = persona

        # Token estimation
        token_estimate = self._estimate_tokens(llm_worthy)

        logger.info(
            f"Triage complete: {len(llm_worthy)} of {len(findings)} findings "
            f"are LLM-worthy (~{token_estimate} tokens)"
        )

        return TriageResult(
            all_findings=findings,
            llm_worthy_findings=llm_worthy,
            routing=routing,
            token_estimate=token_estimate,
        )

    def route_to_persona(self, finding: AnalysisResult) -> str:
        """
        Intelligent routing: which persona should analyze this finding?

        Routing rules:
        - SECURITY → security_analyst (vulnerability expert)
        - CODE_STRUCTURE → refactor_gpt (code improvement)
        - MAINTAINABILITY → refactor_gpt (code improvement)
        - PERFORMANCE → performance_analyst
        - Others → general_analyst (fallback)

        Args:
            finding: The AnalysisResult to route

        Returns:
            Name of the persona to handle this finding
        """
        category = finding.category

        if category == AnalysisCategory.SECURITY:
            return "security_analyst"
        elif category == AnalysisCategory.CODE_STRUCTURE:
            return "refactor_gpt"
        elif category == AnalysisCategory.MAINTAINABILITY:
            return "refactor_gpt"
        elif category == AnalysisCategory.PERFORMANCE:
            return "performance_analyst"
        else:
            return "general_analyst"

    # ==================
    # Private Helpers
    # ==================

    def _pattern_to_finding(
        self, pattern: CrossProjectPattern
    ) -> AnalysisResult:
        """
        Convert CrossProjectPattern to AnalysisResult for unified handling.

        This allows patterns to be treated as special "findings"
        for routing and token estimation.
        """
        return AnalysisResult(
            analyzer_name="cross_project_analyzer",
            file_path=None,  # Patterns are corpus-level, not file-specific
            pattern_type=pattern.pattern_type,
            severity=pattern.severity,
            category=pattern.category,
            confidence=pattern.projects_confidence,
            message=f"[PATTERN] {pattern.message}",
            evidence=pattern.evidence,
            remediation=[],
        )

    def _sort_by_severity(self, findings: List[AnalysisResult]) -> List[AnalysisResult]:
        """Sort findings by severity (CRITICAL > HIGH > MEDIUM > LOW)."""
        severity_rank = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
        }
        return sorted(
            findings, key=lambda f: severity_rank.get(f.severity, 0), reverse=True
        )

    def _estimate_tokens(self, findings: List[AnalysisResult]) -> int:
        """
        Estimate tokens needed for this batch of LLM calls.

        Heuristic: ~150 tokens per finding (average LLM analysis)
        """
        base_tokens = 100  # Prompt setup
        per_finding = 150  # Average analysis per finding
        return base_tokens + (len(findings) * per_finding)

