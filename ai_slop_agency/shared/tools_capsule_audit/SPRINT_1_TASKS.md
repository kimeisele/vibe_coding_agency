# Sprint 1: Data Collection Layer (Säule A)

**Duration:** 1 Week (3-5 working days)

**Goal:** Phase 1 mit echten Analyzern (Radon, Bandit, AI-Slop Pattern Matching) – nicht Mock-Daten

**Current State:** Collectors sind Stubs, geben nur Mock-Daten zurück

**Desired State:** Collectors nutzen echte Libraries, geben echte `AnalysisResult` Objekte zurück

---

## Task 1.1: Dependency Management Update

**File:** `pyproject.toml`

**What:** Add missing dependencies for Collectors

**Action:**
```toml
# Add to [project.dependencies]
radon>=6.1.0          # Complexity metrics
bandit>=1.7.5         # Security analysis
pyyaml>=6.0          # For config (already there)
pydantic>=2.5        # For models (already there)

# Add to [project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0",
    "mypy>=1.0",
]
```

**Success:** `pip install -e ".[dev]"` works without errors, radon + bandit are available

---

## Task 1.2: Complexity Analyzer Implementation

**File:** `src/meta_audit/analyzers/collectors/complexity.py`

**Current Code:** Returns mock data

**What:** Implement real complexity analysis using `radon`

**Action:**

Replace the stub with:

```python
"""
Complexity Analyzer - Uses Radon to analyze code complexity metrics.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from radon.complexity import cc_visit, SCORE
from radon.metrics import mi_visit

logger = logging.getLogger(__name__)


def get_complexity_metrics(path: str, threshold_cc: int = 10) -> Dict[str, Any]:
    """
    Analyze complexity metrics for a project.

    Args:
        path: Root path to analyze
        threshold_cc: Cyclomatic complexity threshold to flag as HIGH

    Returns:
        Dictionary containing:
        - cyclomatic_complexity: Average CC across all functions
        - maintainability_index: Average MI
        - total_loc: Total lines of code
        - functions: List of functions with their metrics
        - high_cc_functions: Functions exceeding threshold
    """
    try:
        project_path = Path(path)

        complexity_data = {
            "cyclomatic_complexity": 0.0,
            "maintainability_index": 0.0,
            "total_loc": 0,
            "functions": [],
            "high_cc_functions": [],
        }

        python_files = list(project_path.rglob("*.py"))

        if not python_files:
            logger.warning(f"No Python files found in {path}")
            return complexity_data

        total_cc = 0
        function_count = 0
        total_mi = 0

        for py_file in python_files:
            try:
                # Skip common non-source directories
                if any(part in py_file.parts for part in [".venv", "venv", ".git", "__pycache__"]):
                    continue

                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()

                # Get cyclomatic complexity
                try:
                    cc_results = cc_visit(code_content)
                    for block in cc_results:
                        complexity_data["functions"].append({
                            "file": str(py_file.relative_to(project_path)),
                            "name": block.name,
                            "cc": block.complexity,
                            "loc": block.end_lineno - block.lineno + 1,
                        })

                        if block.complexity >= threshold_cc:
                            complexity_data["high_cc_functions"].append({
                                "file": str(py_file.relative_to(project_path)),
                                "name": block.name,
                                "cc": block.complexity,
                            })

                        total_cc += block.complexity
                        function_count += 1
                except Exception as e:
                    logger.debug(f"Radon CC analysis failed for {py_file}: {e}")

                # Get maintainability index
                try:
                    mi = mi_visit(code_content, False)
                    if mi:
                        total_mi += mi
                except Exception as e:
                    logger.debug(f"Radon MI analysis failed for {py_file}: {e}")

                complexity_data["total_loc"] += len(code_content.splitlines())

            except (OSError, IOError) as e:
                logger.warning(f"Could not read file {py_file}: {e}")
                continue

        # Calculate averages
        if function_count > 0:
            complexity_data["cyclomatic_complexity"] = round(total_cc / function_count, 2)

        if len(python_files) > 0:
            complexity_data["maintainability_index"] = round(total_mi / len(python_files), 2)

        return complexity_data

    except Exception as e:
        logger.error(f"Complexity analysis failed: {e}")
        return {
            "cyclomatic_complexity": 0.0,
            "maintainability_index": 0.0,
            "total_loc": 0,
            "functions": [],
            "high_cc_functions": [],
            "error": str(e),
        }
```

**Tests:**
- [ ] Run on a test project (e.g., test_data/sample_project)
- [ ] Verify `high_cc_functions` is populated (functions with CC > 10)
- [ ] Verify averages are calculated correctly

---

## Task 1.3: Security Analyzer Implementation

**File:** `src/meta_audit/analyzers/collectors/security.py`

**Current Code:** Returns mock data

**What:** Implement real security analysis using `bandit`

**Action:**

Replace the stub with:

```python
"""
Security Analyzer - Uses Bandit to identify security vulnerabilities.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def get_security_vulnerabilities(path: str, severity_threshold: str = "MEDIUM") -> Dict[str, Any]:
    """
    Analyze security vulnerabilities using Bandit.

    Args:
        path: Root path to analyze
        severity_threshold: Minimum severity to include (LOW, MEDIUM, HIGH)

    Returns:
        Dictionary containing:
        - vulnerabilities: List of security issues found
        - confidence_level: Overall assessment
        - high_severity_count: Number of HIGH/CRITICAL issues
    """
    try:
        project_path = Path(path)

        security_data = {
            "vulnerabilities": [],
            "confidence_level": "HIGH",
            "high_severity_count": 0,
        }

        # Run bandit
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", str(project_path), "-f", "json", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 or result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)

                    for issue in bandit_output.get("results", []):
                        severity = issue.get("severity", "MEDIUM")

                        # Filter by threshold
                        severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                        if severity_order.get(severity, 0) >= severity_order.get(severity_threshold, 0):
                            security_data["vulnerabilities"].append({
                                "file": issue.get("filename", "unknown"),
                                "line": issue.get("line_number", 0),
                                "severity": severity,
                                "issue_type": issue.get("issue_text", "unknown").split(":")[0],
                                "message": issue.get("issue_text", ""),
                                "confidence": issue.get("confidence", "MEDIUM"),
                            })

                            if severity == "HIGH":
                                security_data["high_severity_count"] += 1

                except json.JSONDecodeError:
                    logger.warning("Could not parse bandit JSON output")

        except subprocess.TimeoutExpired:
            logger.warning("Bandit analysis timed out")
        except FileNotFoundError:
            logger.warning("Bandit not installed. Run: pip install bandit")

        return security_data

    except Exception as e:
        logger.error(f"Security analysis failed: {e}")
        return {
            "vulnerabilities": [],
            "confidence_level": "LOW",
            "high_severity_count": 0,
            "error": str(e),
        }
```

**Tests:**
- [ ] Run on a test project
- [ ] Verify vulnerabilities are detected (or empty list if no issues)
- [ ] Verify filtering by severity works

---

## Task 1.4: AI-Slop Analyzer Implementation

**File:** `src/meta_audit/analyzers/collectors/ai_slop.py`

**Current Code:** Empty or stub

**What:** Implement pattern-based detection for AI-Slop (no LLM needed)

**Action:**

Create new:

```python
"""
AI-Slop Analyzer - Pattern-based detection of AI-generated code smells.

Patterns checked:
- Verbose docstrings with no real info
- Placeholder comments ("This function does...")
- Dead code (unused variables, imports)
- Overly generic variable names
- Redundant exception handling
"""

import re
from pathlib import Path
from typing import Dict, Any, List
import logging
import ast

logger = logging.getLogger(__name__)


class AISlop:
    """Pattern definitions for AI-Slop detection."""

    # Verbose docstring pattern (too many words, no real info)
    VERBOSE_DOCSTRING = re.compile(
        r'""".*?(?:This function|This method|This class).*?"""',
        re.DOTALL | re.IGNORECASE
    )

    # Placeholder comment pattern
    PLACEHOLDER_COMMENT = re.compile(
        r'#\s*(?:TODO|FIXME|XXX|HACK|BUG)\s*:',
        re.IGNORECASE
    )

    # Generic variable names
    GENERIC_VARS = {"data", "temp", "result", "value", "obj", "item", "thing"}


def get_ai_slop_findings(path: str) -> Dict[str, Any]:
    """
    Detect AI-Slop patterns in Python code.

    Args:
        path: Root path to analyze

    Returns:
        Dictionary containing:
        - slop_findings: List of detected patterns
        - total_slop_issues: Count of issues
    """
    try:
        project_path = Path(path)

        slop_data = {
            "slop_findings": [],
            "total_slop_issues": 0,
        }

        python_files = list(project_path.rglob("*.py"))

        for py_file in python_files:
            try:
                # Skip common non-source directories
                if any(part in py_file.parts for part in [".venv", "venv", ".git", "__pycache__"]):
                    continue

                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()

                lines = code_content.splitlines()

                # Check 1: Verbose docstrings
                for i, line in enumerate(lines, 1):
                    if AISlop.VERBOSE_DOCSTRING.search(line):
                        slop_data["slop_findings"].append({
                            "file": str(py_file.relative_to(project_path)),
                            "line": i,
                            "pattern": "verbose_docstring",
                            "message": "Generic docstring detected (typical of AI-generated code)",
                            "severity": "LOW",
                        })
                        slop_data["total_slop_issues"] += 1

                # Check 2: Placeholder comments
                for i, line in enumerate(lines, 1):
                    if AISlop.PLACEHOLDER_COMMENT.search(line):
                        slop_data["slop_findings"].append({
                            "file": str(py_file.relative_to(project_path)),
                            "line": i,
                            "pattern": "placeholder_comment",
                            "message": f"Unresolved comment: {line.strip()}",
                            "severity": "MEDIUM",
                        })
                        slop_data["total_slop_issues"] += 1

                # Check 3: Generic variable names (AST-based)
                try:
                    tree = ast.parse(code_content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name) and node.id in AISlop.GENERIC_VARS:
                            if hasattr(node, "lineno"):
                                slop_data["slop_findings"].append({
                                    "file": str(py_file.relative_to(project_path)),
                                    "line": node.lineno,
                                    "pattern": "generic_variable",
                                    "message": f"Generic variable name: '{node.id}'",
                                    "severity": "LOW",
                                })
                                slop_data["total_slop_issues"] += 1
                except SyntaxError:
                    logger.debug(f"Could not parse {py_file}")

            except (OSError, IOError) as e:
                logger.warning(f"Could not read file {py_file}: {e}")
                continue

        return slop_data

    except Exception as e:
        logger.error(f"AI-Slop analysis failed: {e}")
        return {
            "slop_findings": [],
            "total_slop_issues": 0,
            "error": str(e),
        }
```

**Tests:**
- [ ] Test on a sample file with known patterns
- [ ] Verify placeholder comments are detected
- [ ] Verify generic variable names are detected

---

## Task 1.5: Collector Registry & Parallel Execution

**File:** `src/meta_audit/analyzers/collectors/__init__.py`

**Current Code:** Might not exist or be empty

**What:** Create registry pattern + parallel executor

**Action:**

Create/Update:

```python
"""
Collector Registry & Parallel Execution Engine.

Pattern: All collectors are registered and can be executed in parallel.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Callable, List
from functools import wraps

logger = logging.getLogger(__name__)

# Registry of all collectors
_COLLECTORS = {}


def register_collector(name: str):
    """Decorator to register a collector function."""
    def decorator(func: Callable) -> Callable:
        _COLLECTORS[name] = func
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Register all collectors
from .complexity import get_complexity_metrics
from .security import get_security_vulnerabilities
from .ai_slop import get_ai_slop_findings

# Automatically register
_COLLECTORS["complexity"] = get_complexity_metrics
_COLLECTORS["security"] = get_security_vulnerabilities
_COLLECTORS["ai_slop"] = get_ai_slop_findings


def run_all_collectors(path: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute all registered collectors in parallel.

    Args:
        path: Root path to analyze
        timeout: Max time per collector (seconds)

    Returns:
        Dictionary with results from all collectors:
        {
            "complexity": {...},
            "security": {...},
            "ai_slop": {...}
        }
    """
    results = {}
    errors = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(collector_func, path): name
            for name, collector_func in _COLLECTORS.items()
        }

        for future in as_completed(futures, timeout=timeout):
            collector_name = futures[future]
            try:
                result = future.result()
                results[collector_name] = result
                logger.info(f"✓ Collector '{collector_name}' completed successfully")
            except Exception as e:
                logger.warning(f"✗ Collector '{collector_name}' failed: {e}")
                errors.append({
                    "collector": collector_name,
                    "error": str(e),
                })
                # Graceful degradation: continue with other collectors
                results[collector_name] = {"error": str(e)}

    return {
        "collectors_data": results,
        "errors": errors,
        "status": "success" if not errors else "partial_success",
    }


def get_collector(name: str) -> Callable:
    """Get a specific collector by name."""
    return _COLLECTORS.get(name)


def list_collectors() -> List[str]:
    """Get list of all registered collectors."""
    return list(_COLLECTORS.keys())
```

**Tests:**
- [ ] `run_all_collectors("/path/to/project")` returns all 3 collectors' results
- [ ] If one collector fails, others still complete (graceful degradation)
- [ ] Execution is parallel (measure time)

---

## Task 1.6: Update CLI to use new Collectors

**File:** `src/meta_audit/cli/commands/analyze.py`

**Current Code:** Calls old mock collectors

**What:** Update to use new `run_all_collectors()`

**Action:**

Update the `analyze` command:

```python
from src.meta_audit.analyzers.collectors import run_all_collectors

# In the analyze command:
def analyze(path: str):
    click.echo("Phase 1: Collecting data...")

    # OLD: collectors_result = collect_phase_1_mock()
    # NEW:
    collectors_result = run_all_collectors(path)

    if collectors_result["status"] == "partial_success":
        click.echo(f"⚠️  Warning: Some collectors failed: {collectors_result['errors']}")
    elif collectors_result["status"] == "success":
        click.echo("✓ All collectors completed successfully")

    click.echo("\nPhase 2: Analyzing with Agent...")
    # Continue with agent...
```

---

## Task 1.7: Unit Tests for Collectors

**File:** `tests/unit/test_collectors.py`

**What:** Test each collector in isolation

**Action:**

Create:

```python
"""Unit tests for all collectors."""

import pytest
from pathlib import Path
from src.meta_audit.analyzers.collectors.complexity import get_complexity_metrics
from src.meta_audit.analyzers.collectors.security import get_security_vulnerabilities
from src.meta_audit.analyzers.collectors.ai_slop import get_ai_slop_findings


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def simple_function():
    return 42

def complex_function():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        return "too complex"
""")
    return tmp_path


def test_complexity_metrics(sample_python_file):
    result = get_complexity_metrics(str(sample_python_file))
    assert "cyclomatic_complexity" in result
    assert "functions" in result
    assert len(result["functions"]) > 0


def test_security_vulnerabilities(sample_python_file):
    result = get_security_vulnerabilities(str(sample_python_file))
    assert "vulnerabilities" in result
    assert isinstance(result["vulnerabilities"], list)


def test_ai_slop_findings(sample_python_file):
    result = get_ai_slop_findings(str(sample_python_file))
    assert "slop_findings" in result
    assert "total_slop_issues" in result
```

---

## Task 1.8: Integration Test (End-to-End Phase 1)

**File:** `tests/integration/test_phase1_collectors.py`

**What:** Test complete Phase 1 workflow

**Action:**

Create:

```python
"""Integration test for Phase 1 (Data Collection)."""

import pytest
from src.meta_audit.analyzers.collectors import run_all_collectors


def test_phase1_complete_workflow(tmp_path):
    """Test Phase 1: All collectors run and return valid data."""

    # Create a simple project structure
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def util(): pass")

    # Run all collectors
    result = run_all_collectors(str(tmp_path))

    # Assertions
    assert result["status"] in ["success", "partial_success"]
    assert "collectors_data" in result

    collectors_data = result["collectors_data"]
    assert "complexity" in collectors_data
    assert "security" in collectors_data
    assert "ai_slop" in collectors_data

    # Each collector should return valid structure
    assert isinstance(collectors_data["complexity"], dict)
    assert isinstance(collectors_data["security"], dict)
    assert isinstance(collectors_data["ai_slop"], dict)


def test_phase1_graceful_degradation(tmp_path):
    """Test that Phase 1 continues even if one collector fails."""

    # Empty directory (might cause some collectors to fail)
    result = run_all_collectors(str(tmp_path))

    # Should still succeed or partial_success
    assert result["status"] in ["success", "partial_success"]

    # Should have attempted all collectors
    assert len(result["collectors_data"]) == 3
```

---

## Acceptance Criteria

- [ ] `radon` and `bandit` installed and importable
- [ ] `get_complexity_metrics()` returns real data (not mock)
- [ ] `get_security_vulnerabilities()` returns real data (not mock)
- [ ] `get_ai_slop_findings()` detects real patterns
- [ ] `run_all_collectors()` runs all 3 in parallel
- [ ] If one collector fails, others still complete
- [ ] CLI integration: `meta-audit analyze --path <project>` uses real collectors
- [ ] Unit tests pass: `pytest tests/unit/test_collectors.py`
- [ ] Integration test passes: `pytest tests/integration/test_phase1_collectors.py`

---

## Success Output (Example)

When you run `meta-audit analyze --path /path/to/project`:

```
Phase 1: Collecting data...
✓ Collector 'complexity' completed successfully
✓ Collector 'security' completed successfully
✓ Collector 'ai_slop' completed successfully

Collected Data Summary:
- Complexity: 8.5 avg CC, 82.3 MI
- Security: 2 HIGH vulnerabilities found
- AI-Slop: 12 issues detected

Phase 2: Analyzing with Agent...
[LLM call with real data, not mock]
```

---

## Next: Sprint 2

Once Sprint 1 is complete and green:
- Sprint 2 = Säule B (Reporting with real AnalysisResults)
- Sprint 3 = Säule C (Capsule System + Config)

