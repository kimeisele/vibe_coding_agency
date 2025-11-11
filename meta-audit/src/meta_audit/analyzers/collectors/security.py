"""
Security Analyzer - Uses Bandit to identify security vulnerabilities.

Detects:
- Hardcoded passwords/credentials
- SQL injection risks
- Command injection risks
- Insecure random/hash usage
- etc.

Returns List[AnalysisResult] with strict Pydantic validation.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from meta_audit.core.models import AnalysisResult, Severity, AnalysisCategory

logger = logging.getLogger(__name__)


def get_security_vulnerabilities(
    path: str, severity_threshold: str = "MEDIUM"
) -> List[AnalysisResult]:
    """
    Analyze security vulnerabilities using Bandit.

    Returns AnalysisResult objects for each vulnerability found.

    Args:
        path: Root path to analyze
        severity_threshold: Minimum severity to include (LOW, MEDIUM, HIGH)

    Returns:
        List[AnalysisResult] - Each result represents a security finding.
    """
    results: List[AnalysisResult] = []

    try:
        project_path = Path(path)

        # Run bandit
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", str(project_path), "-f", "json", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Log stderr if bandit had issues
            if result.stderr:
                logger.debug(f"Bandit stderr: {result.stderr}")

            # Bandit returns 0 if no issues found, 1 if issues found, >1 if error
            # We should process output if returncode is 0 or 1 and stdout exists
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)

                    severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                    threshold_level = severity_order.get(severity_threshold, 0)

                    for issue in bandit_output.get("results", []):
                        severity_str = issue.get("severity", "MEDIUM")

                        # Filter by threshold
                        if severity_order.get(severity_str, 0) >= threshold_level:
                            # Map string severity to Severity enum
                            severity = Severity(severity_str)

                            # Get file path and make it relative if possible
                            filename = issue.get("filename", "unknown")
                            try:
                                file_path = Path(filename).relative_to(project_path)
                            except (ValueError, TypeError):
                                file_path = Path(filename)

                            # Extract issue type from message
                            issue_text = issue.get("issue_text", "")
                            issue_type = issue_text.split(":")[0].strip()

                            # Create AnalysisResult with strict validation
                            analysis_result = AnalysisResult(
                                analyzer_name="security_analyzer",
                                file_path=file_path,
                                line_start=issue.get("line_number"),
                                line_end=None,
                                pattern_type=f"security_{issue.get('test_id', 'unknown').lower()}",
                                severity=severity,
                                category=AnalysisCategory.SECURITY,
                                confidence=0.95,
                                message=issue_text,
                                evidence={
                                    "test_id": issue.get("test_id", "unknown"),
                                    "test_name": issue.get("test_name", "unknown"),
                                    "confidence": issue.get("confidence", "MEDIUM"),
                                },
                                remediation=[
                                    "See OWASP Top 10 for guidance on this vulnerability type",
                                    "Use secure alternatives (e.g., use environment variables for secrets)",
                                    "Run a security code review with team",
                                    "Consider using static security scanning in CI/CD",
                                ],
                                project_name=None,
                            )
                            results.append(analysis_result)

                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse bandit JSON output: {e}")

        except subprocess.TimeoutExpired:
            logger.warning("Bandit analysis timed out (30s)")
        except FileNotFoundError:
            logger.warning("Bandit not installed. Run: pip install bandit")

        return results

    except Exception as e:
        logger.error(f"Security analysis failed: {e}")
        # Return empty list on error (graceful degradation)
        return []
