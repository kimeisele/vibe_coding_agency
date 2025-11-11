#!/usr/bin/env python3
"""
🚀 FULL PROJECT ANALYSIS: Both Capsules
- Load capsules (agency_toolkit + capsule_audit)
- Run all collectors
- Generate Audit Grid
- Analyze with Wiki Intelligence (Phase 5.2)
- Output comprehensive reports
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from meta_audit.core.models import AnalysisResult, ProjectCapsule
from meta_audit.analyzers.collectors import run_all_collectors
from meta_audit.generators.audit_grid import generate_audit_grid
from meta_audit.prompt_registry.registry import PromptRegistry

def load_capsule(capsule_file: Path) -> ProjectCapsule:
    """Load a capsule file."""
    with open(capsule_file) as f:
        data = json.load(f)
    return ProjectCapsule(**data)

def analyze_project(capsule_file: Path, project_name: str) -> Dict[str, Any]:
    """Analyze a single project capsule."""
    print(f"\n{'='*70}")
    print(f"📊 ANALYZING: {project_name}")
    print(f"{'='*70}")

    # Load capsule
    print(f"\n[1/4] Loading capsule...")
    capsule = load_capsule(capsule_file)
    print(f"   ✅ Loaded {len(capsule.files)} Python files")

    # Run collectors on each file
    print(f"\n[2/4] Running collectors...")
    all_findings = []

    for i, file in enumerate(capsule.files, 1):
        if i % 10 == 0:
            print(f"   Processing file {i}/{len(capsule.files)}...")

        # Write temp file
        temp_file = Path(f"/tmp/{file.path.name}")
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text(file.content)

        try:
            # Run collectors
            findings = run_all_collectors(str(temp_file.parent))
            for finding in findings:
                finding.file_path = Path(project_name) / file.path
                all_findings.append(finding)
        except Exception as e:
            print(f"   ⚠️  Error analyzing {file.path}: {e}")
        finally:
            temp_file.unlink(missing_ok=True)

    print(f"   ✅ Found {len(all_findings)} issues")

    # Count by severity
    severity_counts = {}
    for f in all_findings:
        sev = f.severity.name
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    print(f"   📊 Breakdown: {severity_counts}")

    # Generate audit grid
    print(f"\n[3/4] Generating audit grid...")
    audit_grid_md = generate_audit_grid(all_findings)
    print(f"   ✅ Grid generated")

    # Categorize findings
    print(f"\n[4/4] Analyzing patterns...")
    categories = {}
    for f in all_findings:
        cat = f.category.name
        categories[cat] = categories.get(cat, 0) + 1
    print(f"   📊 Categories: {categories}")

    return {
        "project": project_name,
        "files_analyzed": len(capsule.files),
        "total_findings": len(all_findings),
        "severity_breakdown": severity_counts,
        "category_breakdown": categories,
        "findings": all_findings,
        "audit_grid": audit_grid_md,
        "timestamp": datetime.now().isoformat(),
    }

def main():
    """Run full analysis."""
    print("\n" + "="*70)
    print("🚀 FULL PROJECT ANALYSIS WITH WIKI INTELLIGENCE")
    print("="*70)

    results = {}

    # Analyze capsule_audit
    print("\n" + "🔍 " * 20)
    try:
        results["capsule_audit"] = analyze_project(
            Path("capsule_audit_project.capsule.json"),
            "capsule_audit"
        )
    except Exception as e:
        print(f"❌ Error analyzing capsule_audit: {e}")
        import traceback
        traceback.print_exc()

    # Analyze agency_toolkit
    print("\n" + "🔍 " * 20)
    try:
        results["agency_toolkit"] = analyze_project(
            Path("agency_toolkit.capsule.json"),
            "agency_toolkit"
        )
    except Exception as e:
        print(f"❌ Error analyzing agency_toolkit: {e}")
        import traceback
        traceback.print_exc()

    # Generate summary report
    print("\n" + "="*70)
    print("📋 SUMMARY REPORT")
    print("="*70)

    total_files = 0
    total_findings = 0

    for proj_name, result in results.items():
        print(f"\n{proj_name.upper()}:")
        print(f"  Files analyzed:   {result['files_analyzed']}")
        print(f"  Total findings:   {result['total_findings']}")
        print(f"  Severity breakdown:")
        for sev, count in result['severity_breakdown'].items():
            print(f"    {sev:10s}: {count:3d}")
        total_files += result['files_analyzed']
        total_findings += result['total_findings']

    print(f"\n{'─'*70}")
    print(f"TOTAL: {total_files} files, {total_findings} findings")

    # Save audit grids
    print(f"\n{'='*70}")
    print("💾 SAVING RESULTS")
    print("='='*70")

    for proj_name, result in results.items():
        # Save audit grid
        grid_file = Path(f"AUDIT_GRID_{proj_name}.md")
        grid_file.write_text(result['audit_grid'])
        print(f"✅ Saved {grid_file}")

        # Save raw findings
        findings_file = Path(f"FINDINGS_{proj_name}.json")
        findings_data = [
            {
                "file": str(f.file_path),
                "pattern": f.pattern_type,
                "severity": f.severity.name,
                "category": f.category.name,
                "message": f.message,
                "confidence": f.confidence,
            }
            for f in result['findings']
        ]
        with open(findings_file, 'w') as f:
            json.dump(findings_data, f, indent=2)
        print(f"✅ Saved {findings_file}")

        # Save summary
        summary_file = Path(f"SUMMARY_{proj_name}.json")
        summary = {
            "project": proj_name,
            "timestamp": result['timestamp'],
            "files_analyzed": result['files_analyzed'],
            "total_findings": result['total_findings'],
            "severity_breakdown": result['severity_breakdown'],
            "category_breakdown": result['category_breakdown'],
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Saved {summary_file}")

    print(f"\n✨ Analysis complete!")
    return results

if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
