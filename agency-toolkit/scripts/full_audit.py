#!/usr/bin/env python3
"""
Comprehensive code quality audit based on AI Code Quality standards.
Scans for: god functions, magic numbers, duplication, missing error handling.
"""

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Issue:
    file: str
    line: int
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str


class CodeAuditor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: list[Issue] = []
        self.current_function = None
        self.string_literals: dict[str, list[int]] = defaultdict(list)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_function = self.current_function
        self.current_function = node.name

        # Check for god functions (>50 lines)
        func_length = node.end_lineno - node.lineno
        if func_length > 50:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="HIGH",
                    category="god_function",
                    description=f"Function '{node.name}' is {func_length} lines (>50 threshold)",
                )
            )

        # Check for too many parameters
        if len(node.args.args) > 5:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="MEDIUM",
                    category="too_many_params",
                    description=f"Function '{node.name}' has {len(node.args.args)} parameters (>5)",
                )
            )

        # Check for unclear names
        if node.name in ["tmp", "temp", "data", "x", "y", "z", "foo", "bar", "test"]:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="LOW",
                    category="unclear_name",
                    description=f"Unclear function name: '{node.name}'",
                )
            )

        self.generic_visit(node)
        self.current_function = old_function

    def visit_Num(self, node: ast.Num):
        # Magic numbers (except common ones: 0, 1, -1, 2, 10, 100)
        if isinstance(node.n, (int, float)) and node.n not in [0, 1, -1, 2, 10, 100]:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="MEDIUM",
                    category="magic_number",
                    description=f"Magic number: {node.n}",
                )
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        # Handle Python 3.8+ constants
        if isinstance(node.value, (int, float)) and node.value not in [
            0,
            1,
            -1,
            2,
            10,
            100,
        ]:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="MEDIUM",
                    category="magic_number",
                    description=f"Magic number: {node.value}",
                )
            )

        # Track string literals for duplication
        if isinstance(node.value, str) and len(node.value) > 10:
            self.string_literals[node.value].append(node.lineno)

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        # Check for unclear variable names
        if node.id in [
            "tmp",
            "temp",
            "data",
            "x",
            "y",
            "z",
            "foo",
            "bar",
            "test",
            "val",
        ]:
            self.issues.append(
                Issue(
                    file=self.filepath,
                    line=node.lineno,
                    severity="LOW",
                    category="unclear_name",
                    description=f"Unclear variable name: '{node.id}'",
                )
            )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        # Check for bare except
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append(
                    Issue(
                        file=self.filepath,
                        line=handler.lineno,
                        severity="HIGH",
                        category="bare_except",
                        description="Bare except clause - catches all exceptions",
                    )
                )
        self.generic_visit(node)

    def check_duplicates(self):
        # Check for duplicate string literals
        for literal, lines in self.string_literals.items():
            if len(lines) > 2:
                self.issues.append(
                    Issue(
                        file=self.filepath,
                        line=lines[0],
                        severity="MEDIUM",
                        category="duplication",
                        description=f"String '{literal[:50]}...' repeated {len(lines)} times at lines: {lines}",
                    )
                )


def scan_file(filepath: Path) -> list[Issue]:
    """Scan a single Python file for issues."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        auditor = CodeAuditor(str(filepath))
        auditor.visit(tree)
        auditor.check_duplicates()

        # Check for missing error handling (no try/except in file)
        has_try = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        if not has_try and filepath.stat().st_size > 500:  # Only for non-trivial files
            auditor.issues.append(
                Issue(
                    file=str(filepath),
                    line=1,
                    severity="MEDIUM",
                    category="missing_error_handling",
                    description="No error handling (try/except) found in file",
                )
            )

        return auditor.issues
    except SyntaxError as e:
        return [
            Issue(
                file=str(filepath),
                line=e.lineno or 0,
                severity="CRITICAL",
                category="syntax_error",
                description=f"Syntax error: {e.msg}",
            )
        ]
    except Exception as e:
        return [
            Issue(
                file=str(filepath),
                line=0,
                severity="CRITICAL",
                category="parse_error",
                description=f"Failed to parse: {e}",
            )
        ]


def scan_directory(directory: Path) -> dict[str, list[Issue]]:
    """Scan all Python files in directory."""
    all_issues = {}

    for pyfile in directory.rglob("*.py"):
        # Skip test files and venv
        if any(
            skip in str(pyfile)
            for skip in [
                ".venv",
                "venv",
                "__pycache__",
                ".pytest_cache",
                "test_",
                "tests/",
            ]
        ):
            continue

        issues = scan_file(pyfile)
        if issues:
            all_issues[str(pyfile)] = issues

    return all_issues


def print_report(all_issues: dict[str, list[Issue]]):
    """Print formatted audit report."""
    severity_counts = defaultdict(int)
    category_counts = defaultdict(int)

    print("=" * 80)
    print("CODE QUALITY AUDIT REPORT")
    print("=" * 80)
    print()

    for filepath, issues in sorted(all_issues.items()):
        if not issues:
            continue

        print(f"\n📄 {filepath}")
        print("-" * 80)

        for issue in sorted(issues, key=lambda x: (x.line, x.severity)):
            severity_counts[issue.severity] += 1
            category_counts[issue.category] += 1

            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "⚪"}.get(
                issue.severity, "❓"
            )

            print(
                f"  {emoji} Line {issue.line:4d} | {issue.severity:8s} | {issue.category:20s} | {issue.description}"
            )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_issues = sum(severity_counts.values())
    print(f"\nTotal Issues: {total_issues}")

    print("\nBy Severity:")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = severity_counts[severity]
        if count > 0:
            print(f"  {severity:10s}: {count:4d}")

    print("\nBy Category:")
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {category:30s}: {count:4d}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if category_counts["god_function"] > 0:
        print(
            "\n🔧 GOD FUNCTIONS: Refactor functions >50 lines into smaller, single-purpose functions"
        )

    if category_counts["magic_number"] > 0:
        print(
            "\n🔧 MAGIC NUMBERS: Replace with named constants (e.g., MAX_RETRIES = 3)"
        )

    if category_counts["duplication"] > 0:
        print("\n🔧 DUPLICATION: Extract repeated strings to constants or config")

    if category_counts["missing_error_handling"] > 0:
        print(
            "\n🔧 ERROR HANDLING: Add try/except blocks for file I/O, network calls, API calls"
        )

    if category_counts["bare_except"] > 0:
        print("\n🔧 BARE EXCEPT: Replace 'except:' with specific exception types")

    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path("agency_toolkit")

    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    all_issues = scan_directory(target)
    print_report(all_issues)

    # Exit code based on severity
    has_critical = any(
        any(issue.severity == "CRITICAL" for issue in issues)
        for issues in all_issues.values()
    )
    sys.exit(1 if has_critical else 0)
