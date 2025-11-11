#!/usr/bin/env python3
"""
Demo: Semantic Audit System (Pro Mode)

This demonstrates the "RICHTIG" way to audit code:
1. Run static analysis (basic validation)
2. Use AuditAgent with LLM to find REAL problems (logic, architecture)
3. Generate Enhanced Report with semantic analysis FIRST

This is the hybrid system that combines tool stability with LLM intelligence.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

from meta_audit.analyzers.batch_processor import BatchProcessor
from meta_audit.analyzers.collectors import run_all_collectors
from meta_audit.generators.enriched_report import generate_enriched_report

# Optional imports (LLM features)
try:
    from meta_audit.agents.audit_agent import AuditAgent
    from meta_audit.prompt_registry.registry import PromptRegistry
    from meta_audit.providers.ollama_provider import OllamaProvider
    LLM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LLM features not available: {e}")
    AuditAgent = None
    PromptRegistry = None
    OllamaProvider = None
    LLM_AVAILABLE = False


def demo_semantic_audit_on_capsule(capsule_path: str, output_path: str):
    """
    Demonstrate semantic audit on a ProjectCapsule.

    Args:
        capsule_path: Path to .capsule.json file
        output_path: Path to save enhanced report
    """
    logger.info("=" * 80)
    logger.info("SEMANTIC AUDIT DEMO - PRO MODE")
    logger.info("=" * 80)

    # Step 1: Load capsule
    logger.info(f"\n📦 Step 1: Loading capsule from {capsule_path}")
    capsule = BatchProcessor.load_capsule(capsule_path)
    if not capsule:
        logger.error("Failed to load capsule")
        return

    logger.info(f"✓ Loaded: {capsule.project_name} ({capsule.files_count} files)")

    # Step 2: Run static analysis (the "noob report" tools)
    logger.info("\n🧹 Step 2: Running static analysis (bandit, complexity, etc.)")
    analysis_result = BatchProcessor.analyze_capsule(capsule)

    if analysis_result.get("status") == "failed":
        logger.error(f"Static analysis failed: {analysis_result.get('error')}")
        return

    findings = analysis_result.get("all_findings", [])
    logger.info(f"✓ Static analysis complete: {len(findings)} findings")

    # Step 3: Initialize LLM provider and prompt registry
    logger.info("\n🧠 Step 3: Initializing LLM provider and prompt registry")

    llm_provider = None
    prompt_registry = None

    if LLM_AVAILABLE:
        try:
            # Use Ollama with a local model (or configure your preferred provider)
            llm_provider = OllamaProvider(
                model="qwen2.5-coder:7b",  # Or any model you have
                base_url="http://localhost:11434"
            )
            logger.info("✓ LLM provider initialized (Ollama)")

            # Load prompt registry
            prompts_dir = Path(__file__).parent / "src" / "meta_audit" / "prompts"
            prompt_registry = PromptRegistry(prompts_dir)
            logger.info(f"✓ Prompt registry loaded from {prompts_dir}")
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            logger.info("Skipping LLM analysis (no provider available)")
            llm_provider = None
    else:
        logger.warning("LLM features not available (missing dependencies)")
        logger.info("Install with: pip install -e .[ollama]")

    # Step 4: Run AuditAgent (the "Pro System")
    if llm_provider and LLM_AVAILABLE:
        logger.info("\n🎯 Step 4: Running AuditAgent (semantic analysis)")
        logger.info("This is where the REAL intelligence happens...")

        audit_agent = AuditAgent(
            llm_provider=llm_provider,
            prompt_registry=prompt_registry
        )

        # Convert dict findings to AnalysisResult if needed
        from meta_audit.core.models import AnalysisResult
        analysis_results = []
        for f in findings:
            if isinstance(f, dict):
                analysis_results.append(AnalysisResult(**f))
            else:
                analysis_results.append(f)

        enriched_report = audit_agent.run(
            findings=analysis_results,
            patterns=[]  # Could include cross-project patterns here
        )

        logger.info(f"✓ AuditAgent complete:")
        logger.info(f"  - {len(enriched_report.triage.llm_worthy_findings)} findings triaged for LLM")
        logger.info(f"  - {len(enriched_report.expert_recommendations)} expert recommendations generated")
    else:
        # Fallback: Create empty enriched report
        logger.info("\n⚠️  Step 4: Skipping AuditAgent (no LLM provider)")
        from meta_audit.core.models import EnrichedReport, TriageResult
        from meta_audit.core.models import AnalysisResult

        analysis_results = []
        for f in findings:
            if isinstance(f, dict):
                analysis_results.append(AnalysisResult(**f))
            else:
                analysis_results.append(f)

        enriched_report = EnrichedReport(
            findings=analysis_results,
            patterns=[],
            triage=TriageResult(
                all_findings=analysis_results,
                llm_worthy_findings=[],
                routing={},
                token_estimate=0
            ),
            expert_recommendations=[],
            execution_time=0.0,
            timestamp=""
        )

    # Step 5: Generate Enhanced Report
    logger.info("\n📊 Step 5: Generating Enhanced Report")
    report_generator = generate_enriched_report(enriched_report)

    # Export as Markdown
    markdown_output = report_generator.to_markdown()
    Path(output_path).write_text(markdown_output)
    logger.info(f"✓ Enhanced report saved to: {output_path}")

    # Also export as JSON
    json_output_path = output_path.replace(".md", ".json")
    json_output = report_generator.to_json()
    Path(json_output_path).write_text(json_output)
    logger.info(f"✓ JSON report saved to: {json_output_path}")

    logger.info("\n" + "=" * 80)
    logger.info("✅ SEMANTIC AUDIT COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\nRead the report at: {output_path}")
    logger.info("\nNOTE: The Enhanced Report shows:")
    logger.info("  🧠 PART 1: Semantic Audit (LLM Intelligence) - THE REAL VALUE")
    logger.info("  🧹 PART 2: Static Analysis (Tool Validation) - APPENDIX")


def demo_semantic_audit_on_directory(project_dir: str, output_path: str):
    """
    Demonstrate semantic audit on a local directory.

    Args:
        project_dir: Path to project directory
        output_path: Path to save enhanced report
    """
    logger.info("=" * 80)
    logger.info("SEMANTIC AUDIT DEMO - DIRECTORY MODE")
    logger.info("=" * 80)

    # Step 1: Run static analysis on directory
    logger.info(f"\n🧹 Step 1: Running static analysis on {project_dir}")
    result = run_all_collectors(project_dir)

    findings = result.get("all_findings", [])
    logger.info(f"✓ Static analysis complete: {len(findings)} findings")

    # Step 2: Initialize LLM and prompt registry
    logger.info("\n🧠 Step 2: Initializing LLM provider and prompt registry")

    llm_provider = None
    prompt_registry = None

    if LLM_AVAILABLE:
        try:
            llm_provider = OllamaProvider(
                model="qwen2.5-coder:7b",
                base_url="http://localhost:11434"
            )
            logger.info("✓ LLM provider initialized (Ollama)")

            prompts_dir = Path(__file__).parent / "src" / "meta_audit" / "prompts"
            prompt_registry = PromptRegistry(prompts_dir)
            logger.info(f"✓ Prompt registry loaded")
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            llm_provider = None
    else:
        logger.warning("LLM features not available (missing dependencies)")
        logger.info("Install with: pip install -e .[ollama]")

    # Step 3: Run AuditAgent
    if llm_provider and LLM_AVAILABLE:
        logger.info("\n🎯 Step 3: Running AuditAgent (semantic analysis)")

        audit_agent = AuditAgent(
            llm_provider=llm_provider,
            prompt_registry=prompt_registry
        )

        from meta_audit.core.models import AnalysisResult
        analysis_results = []
        for f in findings:
            if isinstance(f, dict):
                analysis_results.append(AnalysisResult(**f))
            else:
                analysis_results.append(f)

        enriched_report = audit_agent.run(
            findings=analysis_results,
            patterns=[]
        )

        logger.info(f"✓ AuditAgent complete:")
        logger.info(f"  - {len(enriched_report.expert_recommendations)} expert recommendations")
    else:
        logger.info("\n⚠️  Step 3: Skipping AuditAgent (no LLM provider)")
        from meta_audit.core.models import EnrichedReport, TriageResult, AnalysisResult

        analysis_results = []
        for f in findings:
            if isinstance(f, dict):
                analysis_results.append(AnalysisResult(**f))
            else:
                analysis_results.append(f)

        enriched_report = EnrichedReport(
            findings=analysis_results,
            patterns=[],
            triage=TriageResult(
                all_findings=analysis_results,
                llm_worthy_findings=[],
                routing={},
                token_estimate=0
            ),
            expert_recommendations=[],
            execution_time=0.0,
            timestamp=""
        )

    # Step 4: Generate Enhanced Report
    logger.info("\n📊 Step 4: Generating Enhanced Report")
    report_generator = generate_enriched_report(enriched_report)

    markdown_output = report_generator.to_markdown()
    Path(output_path).write_text(markdown_output)
    logger.info(f"✓ Enhanced report saved to: {output_path}")

    json_output_path = output_path.replace(".md", ".json")
    json_output = report_generator.to_json()
    Path(json_output_path).write_text(json_output)
    logger.info(f"✓ JSON report saved to: {json_output_path}")

    logger.info("\n" + "=" * 80)
    logger.info("✅ SEMANTIC AUDIT COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Demo: Semantic Audit System (Pro Mode)"
    )
    parser.add_argument(
        "--capsule",
        help="Path to .capsule.json file to analyze"
    )
    parser.add_argument(
        "--directory",
        help="Path to project directory to analyze"
    )
    parser.add_argument(
        "--output",
        default="semantic_audit_report.md",
        help="Output path for enhanced report (default: semantic_audit_report.md)"
    )

    args = parser.parse_args()

    if args.capsule:
        demo_semantic_audit_on_capsule(args.capsule, args.output)
    elif args.directory:
        demo_semantic_audit_on_directory(args.directory, args.output)
    else:
        # Default: Analyze the capsule_audit project itself
        logger.info("No input specified, analyzing capsule_audit project...")
        project_dir = str(Path(__file__).parent / "src" / "meta_audit")
        demo_semantic_audit_on_directory(project_dir, args.output)
