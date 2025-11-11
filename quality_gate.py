#!/usr/bin/env python3
"""
Quality Gate - Comprehensive Quality Metrics and Enforcement

This script implements the Measurement Layer (Option C) for the Vibe Coding Agency monorepo.
It collects objective quality metrics using industry-standard tools and enforces quality gates.

Tools used:
- radon: Cyclomatic complexity and maintainability index
- bandit: Security vulnerability scanning
- pylint: Code quality and style checking
- pytest: Test coverage and pass rate

Usage:
    python quality_gate.py [component_path]
    python quality_gate.py --all  # Run on all components
    python quality_gate.py --ci   # CI mode (strict enforcement)

Exit codes:
    0 - All quality gates passed
    1 - Quality gates failed
    2 - Error during execution
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import tomli


@dataclass
class QualityMetrics:
    """Container for all quality metrics."""
    component: str
    complexity_score: float = 0.0
    complexity_grade: str = "F"
    maintainability_index: float = 0.0
    security_issues: Dict[str, int] = field(default_factory=dict)
    lint_score: float = 0.0
    lint_issues: Dict[str, int] = field(default_factory=dict)
    coverage: float = 0.0
    test_pass_rate: float = 0.0
    total_score: float = 0.0
    passed: bool = False
    errors: List[str] = field(default_factory=list)


class QualityGate:
    """Main quality gate implementation."""

    def __init__(self, standards_file: Path = None, ci_mode: bool = False):
        """Initialize quality gate.
        
        Args:
            standards_file: Path to quality_standards.toml
            ci_mode: If True, enforce strict CI/CD rules
        """
        self.ci_mode = ci_mode
        self.standards_file = standards_file or Path(__file__).parent / "quality_standards.toml"
        self.standards = self._load_standards()
        self.thresholds = self.standards.get("thresholds", {})
        
    def _load_standards(self) -> Dict[str, Any]:
        """Load quality standards from TOML file."""
        try:
            with open(self.standards_file, "rb") as f:
                return tomli.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: {self.standards_file} not found, using defaults")
            return self._get_default_standards()
        except Exception as e:
            print(f"⚠️  Error loading standards: {e}, using defaults")
            return self._get_default_standards()
    
    def _get_default_standards(self) -> Dict[str, Any]:
        """Get default quality standards."""
        return {
            "thresholds": {
                "minimum_quality_score": 80,
                "minimum_coverage": 75.0,
                "minimum_pass_rate": 100.0,
                "max_function_complexity": 10,
                "max_module_complexity": 50,
                "average_complexity_threshold": 5.0,
                "max_high_severity_issues": 0,
                "max_medium_severity_issues": 5,
                "minimum_maintainability_index": 65.0,
                "min_rating": 7.0,
            }
        }

    def run_radon_complexity(self, path: Path) -> Dict[str, Any]:
        """Run radon complexity analysis.
        
        Returns:
            Dict with complexity metrics
        """
        print(f"  📊 Running complexity analysis (radon)...")
        
        result = {
            "average_complexity": 0.0,
            "grade": "F",
            "violations": 0,
            "raw_output": ""
        }
        
        try:
            # Run radon cc (cyclomatic complexity)
            cmd = ["radon", "cc", str(path), "-s", "-a", "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if proc.returncode == 0 and proc.stdout:
                try:
                    data = json.loads(proc.stdout)
                    total_complexity = 0
                    total_functions = 0
                    violations = 0
                    
                    for file_path, items in data.items():
                        for item in items:
                            complexity = item.get("complexity", 0)
                            total_complexity += complexity
                            total_functions += 1
                            
                            # Check threshold
                            if complexity > self.thresholds.get("max_function_complexity", 10):
                                violations += 1
                    
                    if total_functions > 0:
                        result["average_complexity"] = total_complexity / total_functions
                    result["violations"] = violations
                    result["raw_output"] = proc.stdout
                    
                    # Assign grade based on average
                    avg = result["average_complexity"]
                    if avg <= 5:
                        result["grade"] = "A"
                    elif avg <= 10:
                        result["grade"] = "B"
                    elif avg <= 20:
                        result["grade"] = "C"
                    elif avg <= 30:
                        result["grade"] = "D"
                    else:
                        result["grade"] = "F"
                        
                except json.JSONDecodeError:
                    pass
            
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Radon timeout")
        except FileNotFoundError:
            print(f"    ⚠️  Radon not installed (pip install radon)")
        except Exception as e:
            print(f"    ⚠️  Radon error: {e}")
        
        return result

    def run_radon_maintainability(self, path: Path) -> float:
        """Run radon maintainability index analysis.
        
        Returns:
            Average maintainability index (0-100, higher is better)
        """
        print(f"  📊 Running maintainability analysis (radon)...")
        
        try:
            cmd = ["radon", "mi", str(path), "-s", "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if proc.returncode == 0 and proc.stdout:
                try:
                    data = json.loads(proc.stdout)
                    scores = []
                    
                    for file_path, metrics in data.items():
                        if isinstance(metrics, dict) and "mi" in metrics:
                            scores.append(metrics["mi"])
                    
                    if scores:
                        return sum(scores) / len(scores)
                        
                except json.JSONDecodeError:
                    pass
                    
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Maintainability check timeout")
        except FileNotFoundError:
            print(f"    ⚠️  Radon not installed")
        except Exception as e:
            print(f"    ⚠️  Maintainability error: {e}")
        
        return 0.0

    def run_bandit_security(self, path: Path) -> Dict[str, int]:
        """Run bandit security analysis.
        
        Returns:
            Dict with counts by severity: {CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0}
        """
        print(f"  🔒 Running security analysis (bandit)...")
        
        issues = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        try:
            cmd = ["bandit", "-r", str(path), "-f", "json", "--quiet"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Bandit returns 1 if issues found, 0 if no issues
            if proc.stdout:
                try:
                    data = json.loads(proc.stdout)
                    results = data.get("results", [])
                    
                    for issue in results:
                        severity = issue.get("issue_severity", "LOW").upper()
                        if severity in issues:
                            issues[severity] += 1
                            
                except json.JSONDecodeError:
                    pass
                    
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Bandit timeout")
        except FileNotFoundError:
            print(f"    ⚠️  Bandit not installed (pip install bandit)")
        except Exception as e:
            print(f"    ⚠️  Bandit error: {e}")
        
        return issues

    def run_pylint(self, path: Path) -> Dict[str, Any]:
        """Run pylint code quality analysis.
        
        Returns:
            Dict with score and issue counts
        """
        print(f"  ✨ Running code quality analysis (pylint)...")
        
        result = {
            "score": 0.0,
            "issues": {"critical": 0, "error": 0, "warning": 0, "info": 0},
            "raw_output": ""
        }
        
        try:
            # Find Python files
            python_files = list(Path(path).rglob("*.py"))
            if not python_files:
                return result
                
            # Run pylint with JSON output
            cmd = [
                "pylint",
                str(path),
                "--output-format=json",
                "--max-line-length=120",
                "--disable=C0111,R0903",  # Skip some checks
            ]
            
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if proc.stdout:
                try:
                    data = json.loads(proc.stdout)
                    
                    for issue in data:
                        msg_type = issue.get("type", "").lower()
                        if "error" in msg_type or msg_type == "fatal":
                            result["issues"]["error"] += 1
                        elif "warning" in msg_type:
                            result["issues"]["warning"] += 1
                        elif msg_type == "convention" or msg_type == "refactor":
                            result["issues"]["info"] += 1
                            
                except json.JSONDecodeError:
                    # Try to extract score from stderr
                    if proc.stderr:
                        import re
                        match = re.search(r"rated at ([\d.]+)/10", proc.stderr)
                        if match:
                            result["score"] = float(match.group(1))
                
                result["raw_output"] = proc.stdout or proc.stderr
                    
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Pylint timeout")
        except FileNotFoundError:
            print(f"    ⚠️  Pylint not installed (pip install pylint)")
        except Exception as e:
            print(f"    ⚠️  Pylint error: {e}")
        
        return result

    def run_pytest_coverage(self, path: Path) -> Dict[str, float]:
        """Run pytest with coverage.
        
        Returns:
            Dict with coverage and pass_rate
        """
        print(f"  🧪 Running tests with coverage...")
        
        result = {"coverage": 0.0, "pass_rate": 0.0}
        
        # Check if tests directory exists
        component_root = path if path.is_dir() else path.parent
        tests_dir = component_root / "tests"
        
        if not tests_dir.exists():
            print(f"    ⚠️  No tests directory found at {tests_dir}")
            return result
        
        try:
            # Determine package name from path
            pkg_name = path.name if path.is_dir() else path.parent.name
            
            # Run pytest with coverage
            cmd = [
                "python", "-m", "pytest",
                str(tests_dir),
                f"--cov={pkg_name}",
                "--cov-report=json",
                "--cov-report=term-missing",
                "-v",
                "--tb=short"
            ]
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(component_root)
            )
            
            # Parse coverage from JSON
            cov_file = component_root / "coverage.json"
            if cov_file.exists():
                try:
                    with open(cov_file) as f:
                        cov_data = json.load(f)
                        result["coverage"] = cov_data.get("totals", {}).get("percent_covered", 0.0)
                except:
                    pass
            
            # Parse test results from output
            if proc.stdout:
                import re
                # Look for patterns like "120 passed in 2.34s"
                match = re.search(r"(\d+) passed", proc.stdout)
                if match:
                    passed = int(match.group(1))
                    failed_match = re.search(r"(\d+) failed", proc.stdout)
                    failed = int(failed_match.group(1)) if failed_match else 0
                    total = passed + failed
                    result["pass_rate"] = (passed / total * 100) if total > 0 else 100.0
                else:
                    result["pass_rate"] = 100.0 if proc.returncode == 0 else 0.0
                    
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Pytest timeout")
        except FileNotFoundError:
            print(f"    ⚠️  Pytest not installed")
        except Exception as e:
            print(f"    ⚠️  Pytest error: {e}")
        
        return result

    def calculate_total_score(self, metrics: QualityMetrics) -> float:
        """Calculate total quality score (0-100).
        
        Breakdown:
        - Complexity: 20 points
        - Security: 20 points
        - Code Quality: 20 points
        - Coverage: 20 points
        - Test Pass Rate: 20 points
        """
        score = 0.0
        
        # Complexity score (20 points max)
        if metrics.complexity_grade == "A":
            score += 20
        elif metrics.complexity_grade == "B":
            score += 16
        elif metrics.complexity_grade == "C":
            score += 12
        elif metrics.complexity_grade == "D":
            score += 8
        else:
            score += 4
        
        # Security score (20 points max)
        security_deductions = (
            metrics.security_issues.get("CRITICAL", 0) * 10 +
            metrics.security_issues.get("HIGH", 0) * 5 +
            metrics.security_issues.get("MEDIUM", 0) * 2 +
            metrics.security_issues.get("LOW", 0) * 0.5
        )
        score += max(0, 20 - security_deductions)
        
        # Code quality score (20 points max)
        # Based on lint score (0-10) mapped to 0-20
        score += min(20, metrics.lint_score * 2)
        
        # Coverage score (20 points max)
        score += min(20, metrics.coverage * 0.2)
        
        # Test pass rate (20 points max)
        score += min(20, metrics.test_pass_rate * 0.2)
        
        return round(score, 1)

    def check_quality_gates(self, metrics: QualityMetrics) -> bool:
        """Check if metrics pass all quality gates.
        
        Returns:
            True if all gates passed, False otherwise
        """
        passed = True
        failures = []
        
        # Check complexity
        if metrics.complexity_score > self.thresholds.get("average_complexity_threshold", 5.0):
            failures.append(
                f"Average complexity {metrics.complexity_score:.1f} exceeds threshold "
                f"{self.thresholds['average_complexity_threshold']}"
            )
            passed = False
        
        # Check security
        if metrics.security_issues.get("CRITICAL", 0) > self.thresholds.get("max_high_severity_issues", 0):
            failures.append(
                f"Critical security issues: {metrics.security_issues['CRITICAL']}"
            )
            passed = False
        
        if metrics.security_issues.get("HIGH", 0) > self.thresholds.get("max_high_severity_issues", 0):
            failures.append(
                f"High severity security issues: {metrics.security_issues['HIGH']}"
            )
            if self.ci_mode:
                passed = False
        
        # Check coverage
        min_coverage = self.thresholds.get("minimum_coverage", 75.0)
        if metrics.coverage < min_coverage:
            failures.append(
                f"Coverage {metrics.coverage:.1f}% below threshold {min_coverage}%"
            )
            passed = False
        
        # Check test pass rate
        if metrics.test_pass_rate < self.thresholds.get("minimum_pass_rate", 100.0):
            failures.append(
                f"Test pass rate {metrics.test_pass_rate:.1f}% below 100%"
            )
            passed = False
        
        # Check total score
        min_score = self.thresholds.get("minimum_quality_score", 80)
        if metrics.total_score < min_score:
            failures.append(
                f"Total quality score {metrics.total_score:.1f} below threshold {min_score}"
            )
            passed = False
        
        metrics.errors = failures
        return passed

    def analyze_component(self, component_path: Path) -> QualityMetrics:
        """Run complete quality analysis on a component.
        
        Args:
            component_path: Path to component directory
            
        Returns:
            QualityMetrics with all measurements
        """
        print(f"\n{'='*80}")
        print(f"Analyzing: {component_path.name}")
        print(f"{'='*80}\n")
        
        metrics = QualityMetrics(component=component_path.name)
        
        # Run all analyses
        complexity_result = self.run_radon_complexity(component_path)
        metrics.complexity_score = complexity_result["average_complexity"]
        metrics.complexity_grade = complexity_result["grade"]
        
        metrics.maintainability_index = self.run_radon_maintainability(component_path)
        metrics.security_issues = self.run_bandit_security(component_path)
        
        lint_result = self.run_pylint(component_path)
        metrics.lint_score = lint_result["score"]
        metrics.lint_issues = lint_result["issues"]
        
        test_result = self.run_pytest_coverage(component_path)
        metrics.coverage = test_result["coverage"]
        metrics.test_pass_rate = test_result["pass_rate"]
        
        # Calculate total score
        metrics.total_score = self.calculate_total_score(metrics)
        
        # Check quality gates
        metrics.passed = self.check_quality_gates(metrics)
        
        return metrics

    def print_report(self, metrics: QualityMetrics):
        """Print formatted quality report."""
        print(f"\n{'='*80}")
        print(f"Quality Report: {metrics.component}")
        print(f"{'='*80}\n")
        
        status = "✅ PASSED" if metrics.passed else "❌ FAILED"
        print(f"Status: {status}")
        print(f"Total Score: {metrics.total_score}/100\n")
        
        print("Metrics:")
        print(f"  Complexity:       Grade {metrics.complexity_grade} (avg {metrics.complexity_score:.1f})")
        print(f"  Maintainability:  {metrics.maintainability_index:.1f}/100")
        print(f"  Security Issues:  CRIT:{metrics.security_issues.get('CRITICAL', 0)} "
              f"HIGH:{metrics.security_issues.get('HIGH', 0)} "
              f"MED:{metrics.security_issues.get('MEDIUM', 0)} "
              f"LOW:{metrics.security_issues.get('LOW', 0)}")
        print(f"  Lint Score:       {metrics.lint_score:.1f}/10")
        print(f"  Coverage:         {metrics.coverage:.1f}%")
        print(f"  Test Pass Rate:   {metrics.test_pass_rate:.1f}%")
        
        if metrics.errors:
            print(f"\n⚠️  Quality Gate Failures:")
            for error in metrics.errors:
                print(f"  - {error}")
        
        print(f"\n{'='*80}\n")

    def save_report(self, metrics: QualityMetrics, output_dir: Path):
        """Save quality report to JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"quality_report_{metrics.component}.json"
        
        report_data = {
            "component": metrics.component,
            "total_score": metrics.total_score,
            "passed": metrics.passed,
            "metrics": {
                "complexity_score": metrics.complexity_score,
                "complexity_grade": metrics.complexity_grade,
                "maintainability_index": metrics.maintainability_index,
                "security_issues": metrics.security_issues,
                "lint_score": metrics.lint_score,
                "lint_issues": metrics.lint_issues,
                "coverage": metrics.coverage,
                "test_pass_rate": metrics.test_pass_rate,
            },
            "errors": metrics.errors,
            "thresholds": self.thresholds,
        }
        
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Report saved to {report_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Quality Gate - Comprehensive quality metrics and enforcement"
    )
    parser.add_argument(
        "component",
        nargs="?",
        help="Path to component to analyze (default: agency-toolkit)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all components"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode (strict enforcement)"
    )
    parser.add_argument(
        "--output",
        default="quality_reports",
        help="Output directory for reports"
    )
    
    args = parser.parse_args()
    
    # Initialize quality gate
    gate = QualityGate(ci_mode=args.ci)
    
    # Determine components to analyze
    if args.all:
        # Analyze all main components
        repo_root = Path(__file__).parent
        components = [
            repo_root / "agency-toolkit",
            repo_root / "meta-audit",
            repo_root / "explore_agent",
        ]
    elif args.component:
        components = [Path(args.component)]
    else:
        # Default to agency-toolkit
        components = [Path(__file__).parent / "agency-toolkit"]
    
    # Analyze each component
    all_metrics = []
    overall_passed = True
    
    for component in components:
        if not component.exists():
            print(f"⚠️  Component not found: {component}")
            continue
        
        metrics = gate.analyze_component(component)
        gate.print_report(metrics)
        gate.save_report(metrics, Path(args.output))
        
        all_metrics.append(metrics)
        if not metrics.passed:
            overall_passed = False
    
    # Print summary
    if len(all_metrics) > 1:
        print(f"\n{'='*80}")
        print("Overall Summary")
        print(f"{'='*80}\n")
        
        for metrics in all_metrics:
            status = "✅" if metrics.passed else "❌"
            print(f"{status} {metrics.component:20s} - Score: {metrics.total_score}/100")
        
        print(f"\n{'='*80}\n")
    
    # Exit with appropriate code
    if overall_passed:
        print("✅ All quality gates passed!")
        return 0
    else:
        print("❌ Some quality gates failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
