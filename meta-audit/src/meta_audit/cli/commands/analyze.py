"""
CLI command to run a meta-audit analysis.

Supports both single-project analysis and multi-project corpus analysis.
"""

import os
import time
import click
import logging
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from meta_audit.agents.audit_agent import AuditAgent
from meta_audit.providers.google_provider import GoogleProvider
from meta_audit.analyzers.collectors import (
    run_all_collectors,
    list_collectors,
)
from meta_audit.analyzers.batch_processor import BatchProcessor
from meta_audit.core.models import ProjectCapsule, AnalysisResult
from meta_audit.generators import generate_report

logger = logging.getLogger(__name__)


def _analyze_single_project(project_path: str) -> tuple[List[AnalysisResult], Dict[str, Any], float]:
    """
    Analyze a single project directory.

    Args:
        project_path: Path to project

    Returns:
        Tuple of (all_findings, collectors_data, execution_time)
    """
    click.echo("\nPhase 1: Collecting data from static analyzers...")
    click.echo(f"  Collectors: {', '.join(list_collectors())}")
    click.echo("  Running in parallel...")

    start_time = time.time()
    collection_result = run_all_collectors(str(project_path))
    execution_time = time.time() - start_time

    if collection_result["status"] == "partial_success":
        click.echo(
            click.style(f"⚠️  Warning: Some collectors failed", fg="yellow")
        )
        for error in collection_result["errors"]:
            click.echo(f"    - {error['collector']}: {error['error']}")

    elif collection_result["status"] == "success":
        click.echo(click.style("✓ All collectors completed successfully", fg="green"))

    # Extract all findings
    all_findings = collection_result["all_findings"]
    collectors_data = collection_result["collectors_data"]

    # Summary of Phase 1 results
    click.echo(f"\nPhase 1 Results:")
    click.echo(f"  • Total findings: {len(all_findings)}")
    click.echo(f"    - Complexity: {len(collectors_data.get('complexity', []))} issues")
    click.echo(f"    - Security: {len(collectors_data.get('security', []))} issues")
    click.echo(f"    - AI-Slop: {len(collectors_data.get('ai_slop', []))} issues")
    click.echo(f"  • Execution time: {execution_time:.2f}s")

    return all_findings, collectors_data, execution_time


def _analyze_corpus(capsule_paths: Optional[List[str]], directory_path: Optional[str]) -> tuple[List[AnalysisResult], Dict[str, Any], float]:
    """
    Analyze a corpus of ProjectCapsules.

    Args:
        capsule_paths: Explicit list of capsule files, or None
        directory_path: Directory containing capsules, or None

    Returns:
        Tuple of (all_findings, analysis_results_by_project, total_execution_time)
    """
    click.echo("\nPhase 1 (Corpus): Discovering and analyzing ProjectCapsules...")

    start_time = time.time()

    # Discover capsules
    if capsule_paths:
        capsules_to_load = list(capsule_paths)
        click.echo(f"  Loading {len(capsules_to_load)} specified capsule(s)")
    elif directory_path:
        discovered = BatchProcessor.discover_capsules(directory_path)
        capsules_to_load = [str(p) for p in discovered]
        click.echo(f"  Discovered {len(capsules_to_load)} capsule(s)")
    else:
        click.echo(click.style("ERROR: No capsules specified", fg="red"))
        raise click.Abort()

    if not capsules_to_load:
        click.echo(click.style("ERROR: No capsules found", fg="red"))
        raise click.Abort()

    # Load capsules
    click.echo("\n  Loading ProjectCapsules...")
    capsules: List[ProjectCapsule] = []
    for i, capsule_path in enumerate(capsules_to_load, 1):
        capsule = BatchProcessor.load_capsule(capsule_path)
        if capsule:
            capsules.append(capsule)
            click.echo(f"    ✓ {i}. {capsule.project_name} ({len(capsule.files)} files)")
        else:
            click.echo(f"    ✗ {i}. Failed to load {capsule_path}")

    if not capsules:
        click.echo(click.style("ERROR: No capsules loaded successfully", fg="red"))
        raise click.Abort()

    # Analyze capsules in parallel
    click.echo(f"\n  Analyzing {len(capsules)} capsule(s) in parallel...")
    analysis_results = BatchProcessor.analyze_capsules_parallel(capsules, max_workers=3)

    # Flatten findings
    all_findings_dicts = BatchProcessor.flatten_all_findings(analysis_results)

    # Convert dict findings back to AnalysisResult for consistency
    all_findings: List[AnalysisResult] = []
    for finding_dict in all_findings_dicts:
        project = finding_dict.pop("project", None)
        try:
            result = AnalysisResult(**finding_dict)
            all_findings.append(result)
        except Exception as e:
            logger.warning(f"Failed to parse finding from {project}: {e}")

    execution_time = time.time() - start_time

    # Summary by project
    click.echo(f"\nCorpus Analysis Results:")
    total_findings = 0
    for project_name, result in analysis_results.items():
        if "error" in result:
            click.echo(f"  ✗ {project_name}: FAILED ({result['error']})")
        else:
            findings_count = len(result.get("all_findings", []))
            total_findings += findings_count
            click.echo(f"  ✓ {project_name}: {findings_count} findings")

    click.echo(f"  • Total findings across corpus: {total_findings}")
    click.echo(f"  • Execution time: {execution_time:.2f}s")

    return all_findings, analysis_results, execution_time


@click.command()
@click.option(
    "--path",
    default=".",
    help="Project path (single-project mode) or capsule directory (corpus mode with --corpus)",
)
@click.option(
    "--capsule",
    multiple=True,
    type=click.Path(exists=True),
    help="Specific ProjectCapsule file(s) to analyze (can be used multiple times)",
)
@click.option(
    "--corpus",
    is_flag=True,
    help="Treat --path as a directory containing *.capsule.json files",
)
@click.option(
    "--format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format for the report",
)
@click.option(
    "--output-file",
    type=click.Path(),
    default=None,
    help="Save report to file instead of printing to stdout",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
def analyze(
    path: str,
    capsule: tuple,
    corpus: bool,
    format: str,
    output_file: Optional[str],
    verbose: bool,
):
    """
    Run meta-audit analysis on a project or corpus.

    Single-project mode (default):
        meta-audit analyze --path /my/project

    Corpus mode (multiple projects):
        meta-audit analyze --path ./capsules --corpus
        meta-audit analyze --capsule proj1.json --capsule proj2.json
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Mode detection and validation
    if capsule:
        # Explicit capsule mode
        click.echo("Mode: Analyzing specified ProjectCapsule(s)")
        try:
            all_findings, analysis_results, execution_time = _analyze_corpus(
                capsule_paths=capsule, directory_path=None
            )
        except Exception as e:
            click.echo(click.style(f"ERROR during corpus analysis: {e}", fg="red"))
            logger.exception("Corpus analysis failed")
            raise click.Abort()

    elif corpus:
        # Corpus directory mode
        click.echo(f"Mode: Analyzing capsule directory: {path}")
        corpus_path = Path(path).resolve()
        if not corpus_path.exists():
            click.echo(
                click.style(f"ERROR: Corpus directory does not exist: {path}", fg="red")
            )
            raise click.Abort()

        try:
            all_findings, analysis_results, execution_time = _analyze_corpus(
                capsule_paths=None, directory_path=str(corpus_path)
            )
        except Exception as e:
            click.echo(click.style(f"ERROR during corpus analysis: {e}", fg="red"))
            logger.exception("Corpus analysis failed")
            raise click.Abort()

    else:
        # Single-project mode (default)
        click.echo(f"Mode: Analyzing single project: {path}")
        project_path = Path(path).resolve()
        if not project_path.exists():
            click.echo(
                click.style(f"ERROR: Path does not exist: {path}", fg="red")
            )
            raise click.Abort()

        try:
            all_findings, collectors_data, execution_time = _analyze_single_project(
                str(project_path)
            )
        except Exception as e:
            click.echo(click.style(f"ERROR during data collection: {e}", fg="red"))
            logger.exception("Data collection failed")
            raise click.Abort()

        # For single-project mode, we'll use None as analysis_results
        analysis_results = None

    # --- Generate Report from Phase 1 Findings ---
    click.echo("\nPhase 2: Generating structured report...")

    try:
        # Generate report from all findings
        report = generate_report(all_findings, execution_time=execution_time)

        # Prepare output
        if format == "json":
            output = report.to_json()
        else:  # table
            output = report.to_terminal()

        # Output or save
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(output)
            click.echo(
                click.style(f"✓ Report saved to {output_path.absolute()}", fg="green")
            )
            click.echo(f"  Format: {format.upper()}")
        else:
            click.echo("\n" + output)

    except Exception as e:
        click.echo(click.style(f"ERROR during report generation: {e}", fg="red"))
        logger.exception("Report generation failed")
        raise click.Abort()

    # --- Phase 3: Optional LLM-Powered Analysis ---
    click.echo("\nPhase 3: Synthesizing analysis with LLM-powered agent...")

    if not os.environ.get("GOOGLE_API_KEY"):
        click.echo(
            click.style(
                "⚠️  Skipping Phase 3: GOOGLE_API_KEY not set",
                fg="yellow",
            )
        )
        click.echo("To enable LLM analysis, set: export GOOGLE_API_KEY=<your-key>")
        click.echo("\n✓ Analysis complete! (Phase 1 + Report generated)")
        return

    # LLM analysis only for single-project mode (corpus is too large)
    if corpus or capsule:
        click.echo(
            click.style(
                "⏭️  Skipping Phase 3: LLM analysis not available for corpus mode",
                fg="yellow",
            )
        )
        click.echo("Corpus analysis focuses on Phase 1 and 2 (collection & reporting)")
        return

    try:
        # Single-project LLM analysis
        serialized_collectors_data = {}
        for collector_name, findings in collectors_data.items():
            if isinstance(findings, list):
                serialized_collectors_data[collector_name] = json.loads(
                    json.dumps(
                        [finding.model_dump(mode="json") for finding in findings],
                        default=str,
                    )
                )
            else:
                serialized_collectors_data[collector_name] = findings

        collected_data = {
            "success": True,
            "detail": "Static analysis data collected successfully.",
            "data": serialized_collectors_data,
        }

        provider = GoogleProvider()
        agent = AuditAgent(llm_provider=provider)
        llm_report = agent.run(collected_data)

        click.echo("\n" + "=" * 70)
        click.echo("LLM-POWERED SYNTHESIS")
        click.echo("=" * 70)
        click.echo(llm_report)
        click.echo("=" * 70)

    except Exception as e:
        click.echo(click.style(f"ERROR during analysis phase: {e}", fg="red"))
        logger.exception("Analysis phase failed")
        raise click.Abort()


if __name__ == "__main__":
    analyze()
