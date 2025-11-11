# Sprint 2: Structured Reporting (Säule B)

**Duration:** 1-2 weeks

**Goal:** Implement structured reporting with Pydantic AnalysisResult models (Option A) and JSON/Terminal output formats

**Current State:** Collectors return dicts; no report generation; no structured output

**Desired State:** Collectors return AnalysisResult objects; reports in JSON + Terminal formats; CLI with `--format` and `--output-file` flags

---

## Strategic Decision: Option A ("Data Model First")

**Why we're doing this:**
- Pydantic `AnalysisResult` is our strict data contract between layers
- Dict converters would undermine our guardrails
- 1-2 extra days now saves weeks of debugging later
- Prevents "Wildwuchs" through strict typing

**Report Format Priority:**
1. **JSON** - Structured, machine-readable, source of truth
2. **Terminal/Rich Table** - User-friendly CLI output
3. **YAML** - (Sprint 3)
4. **CSV** - (Sprint 3)

---

## Task 2.1: Review & Understand AnalysisResult Model

**File:** `src/meta_audit/core/models.py`

**What:** Read and understand the existing Pydantic models

**Action:**
```bash
# Read the models file
cat src/meta_audit/core/models.py
```

**Expected Output:** Understand structure of:
- `AnalysisResult` - Single finding from a collector
- `Report` - Aggregated findings
- `Severity` enum - LOW, MEDIUM, HIGH, CRITICAL
- `Category` enum - CODE_STRUCTURE, SECURITY, etc.

**Success:** You understand the fields and constraints of `AnalysisResult`

---

## Task 2.2: Refactor Complexity Analyzer to Return AnalysisResult

**File:** `src/meta_audit/analyzers/collectors/complexity.py`

**Current Code:** Returns `dict` with complexity metrics

**What:** Refactor to return `List[AnalysisResult]` instead of dicts

**Action:**

Replace the function to generate AnalysisResult objects:

```python
from src/meta_audit/core/models import AnalysisResult, Severity

def get_complexity_metrics(path: str, threshold_cc: int = 10) -> List[AnalysisResult]:
    """
    Analyze complexity and return AnalysisResult objects.

    Returns:
        List[AnalysisResult] with one result per high-complexity function
    """
    results = []

    # ... existing collection logic ...

    # For each high-CC function, create an AnalysisResult:
    for func_info in high_cc_functions:
        result = AnalysisResult(
            analyzer_name="complexity_analyzer",
            file_path=func_info["file"],
            line_start=func_info["line"],  # NEW: track line numbers
            line_end=None,  # Will be filled later if needed
            pattern_type="high_cyclomatic_complexity",
            severity=Severity.HIGH if func_info["cc"] >= 15 else Severity.MEDIUM,
            category=Category.CODE_STRUCTURE,
            confidence=0.95,
            message=f"Function '{func_info['name']}' has CC={func_info['cc']} (threshold: {threshold_cc})",
            evidence={
                "cc": func_info["cc"],
                "loc": func_info["loc"],
                "function_name": func_info["name"]
            },
            remediation=[
                "Break function into smaller, single-purpose functions",
                "Extract complex logic into helper functions",
                "Simplify conditional logic"
            ],
            project_name=None  # Will be set by caller if needed
        )
        results.append(result)

    return results
```

**Tests:**
- [ ] Function returns `List[AnalysisResult]`
- [ ] Each result has all required fields
- [ ] Severity is correctly set (HIGH >= 15, MEDIUM >= 10)
- [ ] Remediation list is not empty

---

## Task 2.3: Refactor Security Analyzer to Return AnalysisResult

**File:** `src/meta_audit/analyzers/collectors/security.py`

**Similar to 2.2** but for security findings:

```python
def get_security_vulnerabilities(path: str, ...) -> List[AnalysisResult]:
    results = []

    # ... existing bandit execution ...

    for issue in vulnerabilities:
        result = AnalysisResult(
            analyzer_name="security_analyzer",
            file_path=issue["file"],
            line_start=issue["line"],
            line_end=None,
            pattern_type=issue["issue_type"],  # e.g., "hardcoded_password"
            severity=Severity(issue["severity"]),  # HIGH, MEDIUM, LOW
            category=Category.SECURITY,
            confidence=0.95,
            message=issue["message"],
            evidence={
                "test_id": issue["test_id"],
                "confidence": issue["confidence"]
            },
            remediation=[
                "See OWASP guidelines for this vulnerability type",
                "Use proper secret management (env vars, vaults)"
            ],
            project_name=None
        )
        results.append(result)

    return results
```

**Tests:**
- [ ] Returns `List[AnalysisResult]`
- [ ] Severity mapping works (HIGH, MEDIUM, LOW)
- [ ] File and line numbers captured

---

## Task 2.4: Refactor AI-Slop Analyzer to Return AnalysisResult

**File:** `src/meta_audit/analyzers/collectors/ai_slop.py`

**Similar pattern** for AI-Slop findings:

```python
def get_ai_slop_findings(path: str) -> List[AnalysisResult]:
    results = []

    # ... existing pattern detection ...

    for finding in slop_findings:
        result = AnalysisResult(
            analyzer_name="ai_slop_analyzer",
            file_path=finding["file"],
            line_start=finding["line"],
            pattern_type=finding["pattern"],  # verbose_docstring, placeholder_comment
            severity=Severity.LOW,  # AI-Slop is generally LOW priority
            category=Category.CODE_STRUCTURE,
            confidence=0.85,
            message=finding["message"],
            evidence={"pattern": finding["pattern"]},
            remediation=["Review and improve code quality"],
            project_name=None
        )
        results.append(result)

    return results
```

**Tests:**
- [ ] Returns `List[AnalysisResult]`
- [ ] Pattern_type correctly set
- [ ] Severity consistently LOW

---

## Task 2.5: Update Collector Registry to Handle AnalysisResult

**File:** `src/meta_audit/analyzers/collectors/__init__.py`

**What:** Update `run_all_collectors()` to handle List[AnalysisResult]

**Current Output:**
```python
{
    "collectors_data": {
        "complexity": {...dict...},
        "security": {...dict...},
        "ai_slop": {...dict...}
    }
}
```

**New Output:**
```python
{
    "collectors_data": {
        "complexity": [AnalysisResult, AnalysisResult, ...],  # List!
        "security": [AnalysisResult, AnalysisResult, ...],
        "ai_slop": [AnalysisResult, AnalysisResult, ...]
    },
    "all_findings": [AnalysisResult, AnalysisResult, ...],  # Flattened list
    "status": "success"
}
```

**Action:**
```python
def run_all_collectors(path: str, timeout: int = 120) -> Dict[str, Any]:
    # ... existing code ...

    # Flatten all findings
    all_findings = []
    for collector_name, results in results.items():
        if isinstance(results, list):
            all_findings.extend(results)

    return {
        "collectors_data": results,
        "all_findings": all_findings,
        "errors": errors,
        "status": "success" if not errors else "partial_success"
    }
```

**Tests:**
- [ ] `all_findings` is a flat list of AnalysisResult
- [ ] Total count = sum of all collector results
- [ ] Each result is instance of AnalysisResult

---

## Task 2.6: Create Report Model & Generator

**File:** `src/meta_audit/generators/report.py` (NEW)

**What:** Create Report class and methods to generate JSON/Terminal output

**Implementation:**

```python
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
import json
from meta_audit.core.models import AnalysisResult

@dataclass
class Report:
    """Aggregated analysis report"""
    summary: Dict[str, int]  # {HIGH: 3, MEDIUM: 8, LOW: 5}
    findings: List[AnalysisResult]
    execution_time: float
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        """Export report as JSON string"""
        data = {
            "summary": self.summary,
            "findings": [
                {
                    "analyzer": f.analyzer_name,
                    "file": str(f.file_path),
                    "line": f.line_start,
                    "severity": f.severity,
                    "category": f.category,
                    "message": f.message,
                    "evidence": f.evidence,
                    "remediation": f.remediation
                }
                for f in self.findings
            ],
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }
        return json.dumps(data, indent=2)

    def to_terminal(self) -> str:
        """Export report as Rich-formatted table"""
        from rich.console import Console
        from rich.table import Table

        # Create table
        table = Table(title="Meta-Audit Report")
        table.add_column("Severity", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("File", style="green")
        table.add_column("Message", style="white")

        # Add rows
        for finding in self.findings:
            # Color-code severity
            severity_style = {
                "CRITICAL": "bold red",
                "HIGH": "red",
                "MEDIUM": "yellow",
                "LOW": "blue"
            }.get(finding.severity, "white")

            table.add_row(
                f"[{severity_style}]{finding.severity}[/{severity_style}]",
                str(finding.category),
                str(finding.file_path),
                finding.message[:60] + "..." if len(finding.message) > 60 else finding.message
            )

        # Render
        console = Console()
        with console.capture() as capture:
            console.print(table)

        # Add summary at top
        summary_lines = [
            "Meta-Audit Report",
            "=" * 50,
            f"Critical: {self.summary.get('CRITICAL', 0)} | "
            f"High: {self.summary.get('HIGH', 0)} | "
            f"Medium: {self.summary.get('MEDIUM', 0)} | "
            f"Low: {self.summary.get('LOW', 0)}",
            "",
        ]

        return "\n".join(summary_lines) + capture.getvalue()


def generate_report(findings: List[AnalysisResult], execution_time: float = 0.0) -> Report:
    """Generate report from findings list"""

    # Calculate summary
    summary = {
        "CRITICAL": sum(1 for f in findings if f.severity == "CRITICAL"),
        "HIGH": sum(1 for f in findings if f.severity == "HIGH"),
        "MEDIUM": sum(1 for f in findings if f.severity == "MEDIUM"),
        "LOW": sum(1 for f in findings if f.severity == "LOW"),
        "TOTAL": len(findings)
    }

    # Create report
    report = Report(
        summary=summary,
        findings=findings,
        execution_time=execution_time
    )

    return report
```

**Tests:**
- [ ] `to_json()` returns valid JSON
- [ ] `to_terminal()` returns formatted string
- [ ] Summary counts are correct
- [ ] All findings are included

---

## Task 2.7: Update CLI to Use Reports

**File:** `src/meta_audit/cli/commands/analyze.py`

**What:** Integrate new Report class and format options

**Action:**

```python
from meta_audit.generators.report import generate_report
import time

@click.command()
@click.option("--path", default=".", help="Project path")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
@click.option("--output-file", default=None, help="Save report to file")
def analyze(path: str, format: str, output_file: Optional[str]):
    """Analyze project and output structured report"""

    start_time = time.time()

    # Phase 1: Collect
    collection_result = run_all_collectors(path)
    all_findings = collection_result["all_findings"]

    # Phase 2: Generate Report
    execution_time = time.time() - start_time
    report = generate_report(all_findings, execution_time)

    # Phase 3: Output
    if format == "json":
        output = report.to_json()
    else:  # table
        output = report.to_terminal()

    # Write or print
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        click.echo(f"✓ Report saved to {output_file}")
    else:
        click.echo(output)
```

**Tests:**
- [ ] `--format json` outputs valid JSON
- [ ] `--format table` outputs formatted table
- [ ] `--output-file` creates file correctly

---

## Task 2.8: Update Unit Tests for AnalysisResult

**File:** `tests/unit/test_collectors.py`

**What:** Update existing tests to work with AnalysisResult objects

**Changes:**
- Collectors now return `List[AnalysisResult]`
- Tests should verify AnalysisResult fields
- Check Pydantic validation

```python
def test_complexity_returns_analysis_results():
    result = get_complexity_metrics(sample_project)

    assert isinstance(result, list)
    for finding in result:
        assert isinstance(finding, AnalysisResult)
        assert finding.analyzer_name == "complexity_analyzer"
        assert finding.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert finding.category == Category.CODE_STRUCTURE
```

**Tests:**
- [ ] All 19 unit tests updated and passing

---

## Task 2.9: Integration Tests for Reports

**File:** `tests/integration/test_phase1_reports.py` (NEW)

**What:** Test full workflow: Collectors → AnalysisResult → Report

```python
def test_end_to_end_report_generation(realistic_project):
    """Test full Phase 1 + Report generation"""

    # Phase 1
    collection_result = run_all_collectors(realistic_project)
    findings = collection_result["all_findings"]

    # Generate report
    report = generate_report(findings)

    # Verify
    assert len(report.findings) > 0
    assert report.summary["TOTAL"] == len(findings)

    # Test JSON export
    json_output = report.to_json()
    json.loads(json_output)  # Should parse

    # Test Terminal export
    terminal_output = report.to_terminal()
    assert "Meta-Audit Report" in terminal_output
```

**Tests:**
- [ ] 10+ integration tests for reports
- [ ] JSON export validation
- [ ] Terminal formatting validation

---

## Task 2.10: Commit & Document

**What:** Commit all changes with clear message

**Action:**
```bash
git add src/meta_audit/analyzers/collectors/
git add src/meta_audit/generators/
git add src/meta_audit/cli/commands/analyze.py
git add tests/

git commit -m "refactor: Implement Option A - AnalysisResult models throughout

Collectors Refactor:
- complexity.py returns List[AnalysisResult]
- security.py returns List[AnalysisResult]
- ai_slop.py returns List[AnalysisResult]
- All findings now have strict type validation via Pydantic

Report Generation:
- New Report class with summary aggregation
- to_json() method for structured output
- to_terminal() method with Rich formatting
- CLI flags: --format json|table, --output-file

Testing:
- Updated 19 unit tests for AnalysisResult
- Added 10+ integration tests for reports
- All 45+ tests passing

Guarantees:
- Strict data contracts (no converters)
- Type safety via Pydantic
- Prevents 'Wildwuchs' through validation
- Ready for Phase 4 (Token Tracking) and Phase 5 (Multi-Agent)

Sprint 2 complete."
```

---

## Acceptance Criteria

- [ ] All 3 collectors return `List[AnalysisResult]`
- [ ] AnalysisResult objects pass Pydantic validation
- [ ] Report class generates JSON correctly
- [ ] Report class generates Terminal output (Rich)
- [ ] CLI flags `--format` and `--output-file` work
- [ ] Unit tests: 19/19 PASS
- [ ] Integration tests: 10+/10+ PASS
- [ ] No "dict converters" or workarounds

---

## Success Output (Example)

When you run `meta-audit analyze --path /project --format json --output-file report.json`:

```json
{
  "summary": {
    "CRITICAL": 0,
    "HIGH": 3,
    "MEDIUM": 8,
    "LOW": 12,
    "TOTAL": 23
  },
  "findings": [
    {
      "analyzer": "complexity_analyzer",
      "file": "main.py",
      "line": 42,
      "severity": "HIGH",
      "category": "CODE_STRUCTURE",
      "message": "Function 'process_data' has CC=15 (threshold: 10)",
      "remediation": ["Break function into smaller functions", ...]
    },
    ...
  ],
  "execution_time": 0.82,
  "timestamp": "2025-11-10T14:23:45.123456"
}
```

---

## Next: Sprint 3

Once Sprint 2 is complete:
- Sprint 3 = Säule C (Capsule System + Config)
- Extend Report with YAML + CSV formats
- Full integration tests for all 3 Säulen
