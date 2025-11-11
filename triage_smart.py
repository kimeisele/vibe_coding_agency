#!/usr/bin/env python3
"""
Smart Triage - Filter false positives and categorize by actionability
"""

import json
import sys
from pathlib import Path


# Trusted CLI tools that are safe to call via subprocess
TRUSTED_TOOLS = ["radon", "pytest", "coverage", "bandit", "ruff", "mypy", "git", "python3"]


def is_test_file(file_path: str) -> bool:
    """Check if file is in a test directory."""
    return "/test" in file_path.lower()


def uses_trusted_tool(code_snippet: str) -> bool:
    """Check if subprocess call uses a trusted tool."""
    return any(tool in code_snippet for tool in TRUSTED_TOOLS)


def is_config_param(code_snippet: str) -> bool:
    """Check if 'shell=' is a config parameter, not subprocess.run(..., shell=True)."""
    # If snippet is "shell=shell," or similar, it's a config param
    # Real subprocess.run would have "shell=True" or "shell=False"
    return "shell=shell" in code_snippet or ("shell=" in code_snippet and "subprocess" not in code_snippet)


BANDIT_PATTERNS = {
    "security_b101": {
        "name": "assert_used",
        "description": "Use of assert (removed in optimized bytecode)",
        "false_positive_if": lambda i: is_test_file(i["file_path"]),
        "category": "FALSE_POSITIVE"
    },
    "security_b110": {
        "name": "try_except_pass",
        "description": "Try-except-pass detected",
        "category": "AUTO_SAFE"
    },
    "security_b404": {
        "name": "import_subprocess",
        "description": "Import subprocess module",
        "category": "INFO_ONLY"
    },
    "security_b108": {
        "name": "hardcoded_tmp_directory",
        "description": "Hardcoded /tmp directory",
        "false_positive_if": lambda i: is_test_file(i["file_path"]),
        "category": "MANUAL_REVIEW"
    },
    "security_b603": {
        "name": "subprocess_without_shell",
        "description": "subprocess.run() - check for untrusted input",
        "false_positive_if": lambda i: uses_trusted_tool(i["code_snippet"]) or is_test_file(i["file_path"]),
        "category": "MANUAL_REVIEW"
    },
    "security_b604": {
        "name": "shell_true",
        "description": "subprocess with shell=True",
        "false_positive_if": lambda i: is_config_param(i["code_snippet"]),
        "category": "CRITICAL"
    },
    "security_b607": {
        "name": "partial_executable_path",
        "description": "Starting process with partial path",
        "false_positive_if": lambda i: uses_trusted_tool(i["code_snippet"]) or is_test_file(i["file_path"]),
        "category": "MANUAL_REVIEW"
    },
    "security_b104": {
        "name": "hardcoded_bind_all",
        "description": "Hardcoded 0.0.0.0 bind",
        "false_positive_if": lambda i: is_test_file(i["file_path"]),
        "category": "MANUAL_REVIEW"
    },
}


def categorize_issue(issue):
    """Categorize issue with false positive detection"""
    pattern_id = issue["category"]
    pattern = BANDIT_PATTERNS.get(pattern_id)

    if not pattern:
        return "UNKNOWN"

    # Check for false positive
    if "false_positive_if" in pattern:
        if pattern["false_positive_if"](issue):
            return "FALSE_POSITIVE"

    return pattern["category"]


def smart_triage(json_path: str):
    """Perform smart triage with false positive filtering"""

    with open(json_path, 'r') as f:
        data = json.load(f)

    issues = data.get("issues", [])

    # Categorize all issues
    categorized = {
        "FALSE_POSITIVE": [],
        "AUTO_SAFE": [],
        "INFO_ONLY": [],
        "MANUAL_REVIEW": [],
        "CRITICAL": [],
        "UNKNOWN": []
    }

    for issue in issues:
        category = categorize_issue(issue)
        categorized[category].append(issue)

    # Print summary
    print("="*80)
    print("SMART TRIAGE ANALYSIS - SECURITY ISSUES")
    print("="*80)
    print()

    total = len(issues)
    false_pos = len(categorized["FALSE_POSITIVE"])
    actionable = total - false_pos

    print(f"Total issues from bandit: {total}")
    print(f"False positives (filtered): {false_pos}")
    print(f"REAL actionable issues: {actionable}")
    print()

    print("BREAKDOWN:")
    print("-"*80)
    for cat in ["CRITICAL", "MANUAL_REVIEW", "AUTO_SAFE", "INFO_ONLY", "UNKNOWN"]:
        count = len(categorized[cat])
        if count > 0:
            pct = (count / actionable * 100) if actionable else 0
            print(f"{cat:20s}: {count:4d} issues ({pct:5.1f}% of actionable)")
    print()

    # Details by pattern
    print("PATTERN DETAILS:")
    print("-"*80)

    # Group by pattern
    by_pattern = {}
    for cat in ["CRITICAL", "MANUAL_REVIEW", "AUTO_SAFE"]:
        for issue in categorized[cat]:
            pattern_id = issue["category"]
            if pattern_id not in by_pattern:
                by_pattern[pattern_id] = []
            by_pattern[pattern_id].append(issue)

    sorted_patterns = sorted(by_pattern.items(), key=lambda x: len(x[1]), reverse=True)
    for pattern_id, pattern_issues in sorted_patterns:
        pattern_info = BANDIT_PATTERNS.get(pattern_id, {})
        name = pattern_info.get("name", pattern_id)
        category = categorize_issue(pattern_issues[0])
        print(f"{len(pattern_issues):4d} - {name:30s} [{category}]")
    print()

    # Generate filtered JSONs
    output_dir = Path("examples/triage_output")
    output_dir.mkdir(exist_ok=True)

    # Save actionable issues only
    for cat in ["CRITICAL", "MANUAL_REVIEW", "AUTO_SAFE"]:
        if not categorized[cat]:
            continue

        output_file = output_dir / f"security_{cat.lower()}.json"
        output_data = {
            "analysis_type": "security",
            "triage_category": cat,
            "timestamp": data.get("timestamp"),
            "total_issues": len(categorized[cat]),
            "issues": categorized[cat]
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✓ Generated: {output_file}")

    print()
    print("="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print()

    critical = len(categorized["CRITICAL"])
    manual = len(categorized["MANUAL_REVIEW"])
    auto = len(categorized["AUTO_SAFE"])

    if critical > 0:
        print(f"🔥 PRIORITY 1: {critical} CRITICAL issues (shell=True)")
        print(f"   → Use kdaf-fix on: examples/triage_output/security_critical.json")
        print()

    if auto > 0:
        print(f"✅ PRIORITY 2: {auto} AUTO-SAFE issues (try-except-pass)")
        print(f"   → Already fixed in previous commit!")
        print()

    if manual > 0:
        print(f"⚠️  PRIORITY 3: {manual} MANUAL_REVIEW issues")
        print(f"   → Review with kdaf-fix: examples/triage_output/security_manual_review.json")
        print(f"   → These need case-by-case judgment")
        print()

    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: triage_smart.py <security.json>")
        sys.exit(1)

    smart_triage(sys.argv[1])
