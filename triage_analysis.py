#!/usr/bin/env python3
"""
Triage Analysis - Categorize security issues by fix-ability

Categories:
1. AUTO_SAFE: Simple, safe to auto-fix (e.g., try-except-pass)
2. MANUAL_REVIEW: Complex, requires human review (e.g., shell=True)
3. INFO_ONLY: Informational, may not need fix (e.g., import subprocess)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


# Define fix-ability categories
AUTO_SAFE_PATTERNS = {
    "security_b110",  # try-except-pass
}

MANUAL_REVIEW_PATTERNS = {
    "security_b604",  # shell=True
    "security_b105",  # hardcoded_password_string
    "security_b106",  # hardcoded_password_funcarg
    "security_b107",  # hardcoded_password_default
    "security_b108",  # hardcoded_tmp_directory
    "security_b601",  # paramiko_calls
    "security_b602",  # shell_injection
}

INFO_ONLY_PATTERNS = {
    "security_b404",  # import subprocess
    "security_b403",  # import pickle
    "security_b401",  # import telnetlib
}


def categorize_issue(issue):
    """Categorize issue by fix-ability"""
    pattern = issue["category"]

    if pattern in AUTO_SAFE_PATTERNS:
        return "AUTO_SAFE"
    elif pattern in MANUAL_REVIEW_PATTERNS:
        return "MANUAL_REVIEW"
    elif pattern in INFO_ONLY_PATTERNS:
        return "INFO_ONLY"
    else:
        # Default: assume complex until proven otherwise
        return "MANUAL_REVIEW"


def analyze_triage(json_path: str):
    """Perform triage analysis on security JSON"""

    with open(json_path, 'r') as f:
        data = json.load(f)

    issues = data.get("issues", [])

    # Categorize all issues
    by_triage = defaultdict(list)
    by_pattern = defaultdict(list)

    for issue in issues:
        category = categorize_issue(issue)
        pattern = issue["category"]

        by_triage[category].append(issue)
        by_pattern[pattern].append(issue)

    # Print triage summary
    print("="*80)
    print("TRIAGE ANALYSIS - SECURITY ISSUES")
    print("="*80)
    print()

    print("BY FIX-ABILITY:")
    print("-"*80)
    for category in ["AUTO_SAFE", "MANUAL_REVIEW", "INFO_ONLY"]:
        count = len(by_triage[category])
        pct = (count / len(issues) * 100) if issues else 0
        print(f"{category:20s}: {count:4d} issues ({pct:5.1f}%)")
    print()

    print("TOP PATTERNS:")
    print("-"*80)
    sorted_patterns = sorted(by_pattern.items(), key=lambda x: len(x[1]), reverse=True)
    for pattern, pattern_issues in sorted_patterns[:20]:
        category = categorize_issue(pattern_issues[0])
        print(f"{len(pattern_issues):4d} - {pattern:30s} [{category}]")
    print()

    print("RECOMMENDATIONS:")
    print("-"*80)

    auto_count = len(by_triage["AUTO_SAFE"])
    manual_count = len(by_triage["MANUAL_REVIEW"])
    info_count = len(by_triage["INFO_ONLY"])

    print(f"1. AUTO-FIX: {auto_count} issues are safe to auto-fix (try-except-pass)")
    print(f"2. MANUAL REVIEW: {manual_count} issues require human judgment")
    print(f"3. INFO ONLY: {info_count} issues are informational (may not need fix)")
    print()

    # Generate separate JSON files
    output_dir = Path("examples/triage_output")
    output_dir.mkdir(exist_ok=True)

    for category, category_issues in by_triage.items():
        if not category_issues:
            continue

        output_file = output_dir / f"security_{category.lower()}.json"
        output_data = {
            "analysis_type": "security",
            "triage_category": category,
            "timestamp": data.get("timestamp"),
            "total_issues": len(category_issues),
            "issues": category_issues
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✓ Generated: {output_file}")

    print()
    print("="*80)
    print("NEXT STEPS:")
    print("="*80)
    print()
    print(f"1. Review: examples/triage_output/security_auto_safe.json ({auto_count} issues)")
    print(f"2. Build auto-fix script for 'try-except-pass' pattern")
    print(f"3. Use kdaf-fix for manual review of {manual_count} complex issues")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: triage_analysis.py <security.json>")
        sys.exit(1)

    analyze_triage(sys.argv[1])
