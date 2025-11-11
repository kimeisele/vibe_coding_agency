#!/usr/bin/env python3
"""
Run Real Audit - 10-Minute Bridge to System 1

This script:
1. Imports real analysis tools from meta-audit
2. Scans agency-toolkit directory
3. Generates REAL JSON files for kdaf-fix

This is the "Motor of System 1" without the full orchestrator.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add meta-audit to path
sys.path.insert(0, str(Path(__file__).parent / "meta-audit" / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from meta_audit.analyzers.collectors import run_all_collectors
    from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory
except ImportError as e:
    logger.error(f"Failed to import meta_audit: {e}")
    logger.error("Make sure meta-audit is in the correct location")
    sys.exit(1)


def read_code_snippet(file_path: Path, line_number: int, context_lines: int = 0) -> str:
    """
    Read the code snippet at the given line.

    Args:
        file_path: Path to file
        line_number: Line number (1-indexed)
        context_lines: Number of lines before/after to include

    Returns:
        Code snippet as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines):
            return "# Code snippet unavailable (line out of range)"

        # Extract line (convert to 0-indexed)
        target_line = lines[line_number - 1].rstrip()

        if context_lines > 0:
            start = max(0, line_number - 1 - context_lines)
            end = min(len(lines), line_number + context_lines)
            snippet = "".join(lines[start:end]).rstrip()
            return snippet
        else:
            return target_line

    except Exception as e:
        logger.warning(f"Could not read {file_path}:{line_number}: {e}")
        return f"# Code snippet unavailable: {e}"


def generate_fix_suggestion(finding: AnalysisResult, code_snippet: str) -> str:
    """
    Generate a suggested fix based on the pattern type.

    This is a SIMPLE rule-based generator. For complex fixes, manual editing needed.
    """
    pattern = finding.pattern_type.lower()

    # Security patterns with simple fixes
    if "hardcoded_password" in pattern or "hardcoded_bind_all" in pattern:
        return f"# TODO: Move to environment variable\n# Use: os.getenv('SECRET_NAME')"

    if "shell" in pattern and "subprocess" in code_snippet.lower():
        return code_snippet.replace("shell=True", "shell=False")

    if "assert" in pattern:
        return code_snippet.replace("assert", "if not ... raise ValueError(")

    # Default: Return a placeholder
    return f"# MANUAL FIX REQUIRED\n# See remediation suggestions:\n# " + "\n# ".join(finding.remediation[:2])


def convert_to_kdaf_issue(finding: AnalysisResult, project_root: Path, issue_id: int) -> Dict[str, Any]:
    """
    Convert AnalysisResult to kdaf-fix JSON format.
    """
    # Make file path relative to project root
    try:
        if finding.file_path:
            relative_path = Path(finding.file_path)
            # Make it relative to vibe_coding_agency root
            file_path_str = f"agency-toolkit/{relative_path}"
        else:
            file_path_str = "unknown"
    except Exception:
        file_path_str = str(finding.file_path) if finding.file_path else "unknown"

    # Read code snippet
    full_path = project_root / finding.file_path if finding.file_path else None
    line_number = finding.line_start or 1

    if full_path and full_path.exists():
        code_snippet = read_code_snippet(full_path, line_number)
        suggested_fix = generate_fix_suggestion(finding, code_snippet)
    else:
        code_snippet = "# Code unavailable"
        suggested_fix = "# Fix unavailable"

    # Map severity
    severity_map = {
        Severity.CRITICAL: "critical",
        Severity.HIGH: "high",
        Severity.MEDIUM: "medium",
        Severity.LOW: "low"
    }

    return {
        "id": f"{finding.category.value.upper()}-{issue_id:03d}",
        "severity": severity_map.get(finding.severity, "medium"),
        "category": finding.pattern_type,
        "description": finding.message,
        "file_path": file_path_str,
        "line_number": line_number,
        "code_snippet": code_snippet,
        "suggested_fix": suggested_fix,
        "rationale": " | ".join(finding.remediation[:2]) if finding.remediation else "See security best practices",
        "references": []
    }


def main():
    logger.info("="*80)
    logger.info("RUN REAL AUDIT - 10-Minute Bridge")
    logger.info("="*80)

    # Target: agency-toolkit
    project_root = Path("agency-toolkit")

    if not project_root.exists():
        logger.error(f"Project not found: {project_root}")
        sys.exit(1)

    logger.info(f"\n📁 Target: {project_root.absolute()}")

    # Step 1: Run all collectors
    logger.info("\n🔍 Step 1: Running meta-audit collectors...")
    logger.info("  - security (bandit)")
    logger.info("  - complexity (radon)")
    logger.info("  - ai_slop (pattern matching)")
    logger.info("  - god_object (class analysis)")

    result = run_all_collectors(str(project_root.absolute()))

    all_findings: List[AnalysisResult] = result.get("all_findings", [])
    errors = result.get("errors", [])

    if errors:
        logger.warning(f"⚠️  {len(errors)} collector(s) failed:")
        for err in errors:
            logger.warning(f"  - {err['collector']}: {err['error']}")

    logger.info(f"\n✓ Collectors complete: {len(all_findings)} total findings")

    # Step 2: Group by category
    logger.info("\n📊 Step 2: Grouping findings by category...")

    by_category = {}
    for finding in all_findings:
        category = finding.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(finding)

    for category, findings in by_category.items():
        logger.info(f"  - {category}: {len(findings)} issues")

    # Step 3: Generate kdaf-fix JSON files
    logger.info("\n💾 Step 3: Generating kdaf-fix JSON files...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("examples/real_audit_output")
    output_dir.mkdir(exist_ok=True, parents=True)

    for category, findings in by_category.items():
        if not findings:
            continue

        # Convert to kdaf-fix format
        issues = []
        for idx, finding in enumerate(findings, 1):
            issue = convert_to_kdaf_issue(finding, project_root, idx)
            issues.append(issue)

        # Create JSON
        output_data = {
            "analysis_type": category,
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(issues),
            "issues": issues
        }

        # Write to file
        output_file = output_dir / f"{category}_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"  ✓ {output_file}")

    # Step 4: Summary
    logger.info("\n" + "="*80)
    logger.info("✅ REAL AUDIT COMPLETE")
    logger.info("="*80)
    logger.info(f"\nGenerated {len(by_category)} JSON files in: {output_dir}")
    logger.info("\n📋 Next steps:")
    logger.info("  1. Review the JSON files (some fixes may need manual editing)")
    logger.info("  2. Run: ./tools/kdaf-fix examples/real_audit_output/security_*.json")
    logger.info("  3. Apply fixes interactively (y/n/q)")
    logger.info("\n🎯 This is KDAF in action: Real analysis → Real fixes")


if __name__ == "__main__":
    main()
