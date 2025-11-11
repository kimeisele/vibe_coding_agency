"""
Enhanced Report Generator - Prioritizes LLM semantic analysis over static tool results.

This is the "PRO SYSTEM" that replaces generic linter noise with actual intelligence.

Report Structure:
1. 🧠 SEMANTIC AUDIT (LLM-POWERED INTELLIGENCE) - THE REAL VALUE
   - Expert Recommendations from Specialist Personas
   - God Object Detection Results
   - CLEAR Framework Analysis
   - Security Analyst Deep Dive
   - Refactor GPT Recommendations

2. 🧹 STATIC ANALYSIS (TOOL VALIDATION APPENDIX)
   - Bandit Results
   - Complexity Metrics
   - Traditional Linter Findings
"""

import json
import logging
from datetime import datetime
from typing import List, Optional

from meta_audit.core.models import EnrichedReport, AnalysisResult, ExpertRecommendation

logger = logging.getLogger(__name__)


class EnrichedReportGenerator:
    """
    Generate reports that prioritize semantic intelligence over tool noise.

    Philosophy:
    - LLM analysis finds REAL problems (logic flaws, architecture issues)
    - Static tools find surface-level problems (style, basic security)
    - We show LLM results FIRST because that's what matters
    """

    def __init__(self, enriched_report: EnrichedReport):
        """
        Initialize with an EnrichedReport from AuditAgent.

        Args:
            enriched_report: EnrichedReport containing findings, patterns,
                           triage results, and expert recommendations
        """
        self.report = enriched_report

    def to_markdown(self) -> str:
        """
        Generate markdown report with semantic analysis first.

        Returns:
            Formatted markdown string
        """
        sections = []

        # Header
        sections.append(self._generate_header())

        # PART 1: 🧠 SEMANTIC AUDIT (THE REAL VALUE)
        sections.append(self._generate_semantic_section())

        # PART 2: 🧹 STATIC ANALYSIS (APPENDIX)
        sections.append(self._generate_static_section())

        # Footer
        sections.append(self._generate_footer())

        return "\n\n".join(sections)

    def to_terminal(self) -> str:
        """
        Generate terminal-friendly output with colors.

        Returns:
            Terminal-formatted string
        """
        # For now, return markdown (can be enhanced with Rich later)
        return self.to_markdown()

    def to_json(self) -> str:
        """
        Export complete report as JSON.

        Returns:
            JSON string
        """
        data = {
            "summary": {
                "total_findings": len(self.report.findings),
                "llm_analyzed": len(self.report.expert_recommendations),
                "patterns_detected": len(self.report.patterns),
                "execution_time": self.report.execution_time,
            },
            "semantic_audit": [
                {
                    "finding_id": rec.finding_id,
                    "persona": rec.persona,
                    "analysis": rec.analysis,
                    "confidence": rec.confidence,
                    "artifacts": rec.artifacts.model_dump(mode="json") if rec.artifacts else {},
                }
                for rec in self.report.expert_recommendations
            ],
            "static_findings": [
                finding.model_dump(mode="json") for finding in self.report.findings
            ],
            "patterns": [
                pattern.model_dump(mode="json") for pattern in self.report.patterns
            ],
            "timestamp": self.report.timestamp,
        }
        return json.dumps(data, indent=2)

    def _generate_header(self) -> str:
        """Generate report header with summary."""
        lines = [
            "# 📊 Meta-Audit Enhanced Report",
            "",
            f"**Generated:** {self.report.timestamp}",
            f"**Execution Time:** {self.report.execution_time:.2f}s",
            "",
            "## Executive Summary",
            "",
            f"- **Total Findings:** {len(self.report.findings)}",
            f"- **LLM-Analyzed Findings:** {len(self.report.expert_recommendations)}",
            f"- **Cross-Project Patterns:** {len(self.report.patterns)}",
            f"- **Triaged for Intelligence:** {len(self.report.triage.llm_worthy_findings)} findings",
            "",
            "---",
        ]
        return "\n".join(lines)

    def _generate_semantic_section(self) -> str:
        """
        Generate the semantic audit section - THE REAL VALUE.

        This is what humans care about:
        - Architecture problems
        - Logic flaws
        - Security vulnerabilities with exploitation scenarios
        - Refactoring strategies
        """
        lines = [
            "# 🧠 PART 1: SEMANTIC AUDIT (LLM-POWERED INTELLIGENCE)",
            "",
            "> **This is the real value.** LLM analysis finds logic flaws, architecture issues,",
            "> and edge cases that static tools miss. Read this first.",
            "",
        ]

        if not self.report.expert_recommendations:
            lines.extend([
                "**No expert recommendations generated.**",
                "",
                "*Either no findings were deemed worthy of LLM analysis,*",
                "*or the AuditAgent was not run on this report.*",
            ])
            return "\n".join(lines)

        # Group recommendations by persona
        by_persona = {}
        for rec in self.report.expert_recommendations:
            persona = rec.persona
            if persona not in by_persona:
                by_persona[persona] = []
            by_persona[persona].append(rec)

        # Generate sections for each persona
        persona_order = ["security_analyst", "refactor_gpt", "performance_analyst", "general_analyst"]

        for persona in persona_order:
            if persona not in by_persona:
                continue

            recommendations = by_persona[persona]
            lines.append(self._generate_persona_section(persona, recommendations))
            lines.append("")

        # Add any other personas not in the predefined order
        for persona, recommendations in by_persona.items():
            if persona not in persona_order:
                lines.append(self._generate_persona_section(persona, recommendations))
                lines.append("")

        return "\n".join(lines)

    def _generate_persona_section(self, persona: str, recommendations: List[ExpertRecommendation]) -> str:
        """Generate section for a specific specialist persona."""
        persona_titles = {
            "security_analyst": "## 🔒 Security Analyst: Deep Vulnerability Analysis",
            "refactor_gpt": "## ♻️ Refactor GPT: Code Quality & Architecture",
            "performance_analyst": "## ⚡ Performance Analyst: Optimization Opportunities",
            "general_analyst": "## 🔍 General Analyst: Code Review",
        }

        title = persona_titles.get(persona, f"## 📋 {persona.replace('_', ' ').title()}")

        lines = [
            title,
            "",
            f"**{len(recommendations)} findings analyzed by {persona.replace('_', ' ').title()}**",
            "",
        ]

        for i, rec in enumerate(recommendations, 1):
            lines.extend([
                f"### Finding {i}: `{rec.finding_id}`",
                "",
                f"**Confidence:** {rec.confidence:.0%}",
                "",
                "#### Analysis",
                "",
                rec.analysis,
                "",
            ])

            # Show artifacts if available
            if rec.artifacts:
                if rec.artifacts.patches:
                    lines.extend([
                        "#### 🔧 Suggested Patches",
                        "",
                    ])
                    for j, patch in enumerate(rec.artifacts.patches, 1):
                        lines.extend([
                            f"**Patch {j}:**",
                            "```python",
                            patch,
                            "```",
                            "",
                        ])

                if rec.artifacts.tests:
                    lines.extend([
                        "#### 🧪 Suggested Tests",
                        "",
                    ])
                    for j, test in enumerate(rec.artifacts.tests, 1):
                        lines.extend([
                            f"**Test {j}:**",
                            "```python",
                            test,
                            "```",
                            "",
                        ])

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_static_section(self) -> str:
        """
        Generate the static analysis section - TOOL VALIDATION APPENDIX.

        This is the "noob report" - useful for compliance, but not the main value.
        """
        lines = [
            "# 🧹 PART 2: STATIC ANALYSIS (TOOL VALIDATION APPENDIX)",
            "",
            "> **This is the appendix.** Static tools find surface-level issues:",
            "> style violations, obvious security patterns, basic complexity metrics.",
            "> Useful for compliance, but the semantic audit above is the real value.",
            "",
        ]

        if not self.report.findings:
            lines.extend([
                "**No static findings detected.**",
                "",
                "All static analysis tools passed cleanly. ✅",
            ])
            return "\n".join(lines)

        # Group findings by analyzer
        by_analyzer = {}
        for finding in self.report.findings:
            analyzer = finding.analyzer_name
            if analyzer not in by_analyzer:
                by_analyzer[analyzer] = []
            by_analyzer[analyzer].append(finding)

        # Summary table
        lines.extend([
            "## Summary by Analyzer",
            "",
            "| Analyzer | Findings | Critical | High | Medium | Low |",
            "|----------|----------|----------|------|--------|-----|",
        ])

        for analyzer, findings in sorted(by_analyzer.items()):
            counts = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
            }
            for f in findings:
                severity = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
                if severity in counts:
                    counts[severity] += 1

            lines.append(
                f"| {analyzer} | {len(findings)} | {counts['CRITICAL']} | "
                f"{counts['HIGH']} | {counts['MEDIUM']} | {counts['LOW']} |"
            )

        lines.extend(["", ""])

        # Detailed findings by analyzer
        lines.append("## Detailed Findings")
        lines.append("")

        for analyzer, findings in sorted(by_analyzer.items()):
            lines.extend([
                f"### {analyzer}",
                "",
                f"**{len(findings)} findings**",
                "",
            ])

            # Show only top 10 findings per analyzer to avoid noise
            for finding in findings[:10]:
                severity = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)
                lines.extend([
                    f"- **[{severity}]** `{finding.file_path}:{finding.line_start}` - {finding.message}",
                ])

            if len(findings) > 10:
                lines.append(f"- *(... and {len(findings) - 10} more findings)*")

            lines.append("")

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        """Generate report footer."""
        lines = [
            "---",
            "",
            "## 📖 How to Use This Report",
            "",
            "1. **Read Part 1 (Semantic Audit) first** - This is where the real problems are",
            "2. **Prioritize expert recommendations** - These are LLM-validated issues",
            "3. **Use Part 2 (Static Analysis) for compliance** - Fix these if required by policy",
            "4. **Focus on CRITICAL and HIGH severity** - Everything else is nice-to-have",
            "",
            "**Philosophy:** AI-powered semantic analysis > Static tool noise",
            "",
            f"*Report generated by Meta-Audit Enhanced Report Generator v1.0*",
            f"*Timestamp: {self.report.timestamp}*",
        ]
        return "\n".join(lines)


def generate_enriched_report(enriched_report: EnrichedReport) -> EnrichedReportGenerator:
    """
    Generate an enhanced report from an EnrichedReport.

    Args:
        enriched_report: EnrichedReport from AuditAgent

    Returns:
        EnrichedReportGenerator instance with export methods
    """
    return EnrichedReportGenerator(enriched_report)


__all__ = ["EnrichedReportGenerator", "generate_enriched_report"]
