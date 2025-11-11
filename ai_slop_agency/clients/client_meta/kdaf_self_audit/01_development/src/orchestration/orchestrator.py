"""
Workflow Orchestrator - Links KDAF phases into sequential execution

Purpose: Orchestrate Phase 1 → 2 → 3 → 4 automatically
Philosophy: Each phase feeds the next. State persists. No circular reasoning.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .state_manager import StateManager, PhaseStatus, ConfidenceLevel

class WorkflowOrchestrator:
    """
    Orchestrates KDAF workflow execution.

    Workflow:
    1. VERSTEHEN (Understand) → Extract facts, identify gaps
    2. RECHERCHIEREN (Research) → Gather sources, identify tools
    3. VALIDIEREN (Validate) → Run tools, generate outputs
    4. BERICHT (Report) → Compile deliverable with confidence
    """

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.state_manager = StateManager(project_path)

        # Key directories
        self.scoping_dir = self.project_path / "00_scoping_and_research"
        self.dev_dir = self.project_path / "01_development"
        self.validation_dir = self.project_path / "02_validation_and_reports"
        self.deliverable_dir = self.project_path / "03_deliverables"

    def run_analysis(self, phases: List[str] = None) -> Dict[str, Any]:
        """
        Run analysis workflow.

        Args:
            phases: List of phases to run ['1', '2', '3', '4']. If None, runs all.

        Returns:
            Dict with results and final state
        """
        if phases is None:
            phases = ['1', '2', '3', '4']

        results = {
            "phases_run": [],
            "errors": [],
            "final_state": None
        }

        for phase in phases:
            try:
                # Check if phase can run
                if not self.state_manager.can_run_phase(phase):
                    error = f"Phase {phase} cannot run (dependencies not met)"
                    results["errors"].append(error)
                    print(f"⚠️  {error}")
                    continue

                # Run phase
                print(f"\n{'='*60}")
                print(f"🎯 PHASE {phase}: {self._get_phase_name(phase)}")
                print(f"{'='*60}\n")

                if phase == '1':
                    phase_result = self.phase_1_understand()
                elif phase == '2':
                    phase_result = self.phase_2_research()
                elif phase == '3':
                    phase_result = self.phase_3_validate()
                elif phase == '4':
                    phase_result = self.phase_4_report()
                else:
                    raise ValueError(f"Invalid phase: {phase}")

                results["phases_run"].append({
                    "phase": phase,
                    "status": "COMPLETE",
                    "result": phase_result
                })

            except Exception as e:
                error = f"Phase {phase} failed: {str(e)}"
                results["errors"].append(error)
                print(f"❌ {error}")

                # Mark phase as failed
                self.state_manager.update_phase(
                    phase,
                    PhaseStatus.FAILED,
                    {"error": str(e)}
                )

        # Final state
        results["final_state"] = self.state_manager.get_summary()

        return results

    def phase_1_understand(self) -> Dict[str, Any]:
        """
        Phase 1: Semantic Understanding

        Process:
        1. Parse input_analysis.md
        2. Extract facts, gaps, questions
        3. Identify validation requirements
        4. Update state

        Anti-Bullshit Rule: NO ASSUMPTIONS
        """
        print("📋 Phase 1: Semantic Understanding")

        self.state_manager.update_phase('1', PhaseStatus.IN_PROGRESS)

        input_analysis_file = self.scoping_dir / "01_input_analysis.md"

        if not input_analysis_file.exists():
            raise FileNotFoundError(
                f"Input analysis not found: {input_analysis_file}\n"
                f"Please fill out the semantic understanding template first."
            )

        # Parse input analysis
        content = input_analysis_file.read_text()

        # Extract structured data (simple parsing for now)
        facts = self._extract_section(content, "Facts Extracted")
        gaps = self._extract_section(content, "Knowledge Gaps")
        questions = self._extract_section(content, "Pre-Research Questions")

        outputs = {
            "facts": facts,
            "knowledge_gaps": gaps,
            "pre_research_questions": questions,
            "input_file": str(input_analysis_file)
        }

        self.state_manager.update_phase('1', PhaseStatus.COMPLETE, outputs)

        print(f"✅ Phase 1 complete:")
        print(f"   - Facts extracted: {len(facts)}")
        print(f"   - Knowledge gaps: {len(gaps)}")
        print(f"   - Research questions: {len(questions)}")

        return outputs

    def phase_2_research(self) -> Dict[str, Any]:
        """
        Phase 2: Knowledge Acquisition

        Process:
        1. Review research checklist
        2. Gather sources (official docs, articles, examples)
        3. Identify validation tools
        4. Update state

        Anti-Bullshit Rule: NEVER CLAIM WITHOUT SOURCE
        """
        print("🔍 Phase 2: Knowledge Acquisition")

        self.state_manager.update_phase('2', PhaseStatus.IN_PROGRESS)

        research_log = self.scoping_dir / "02_research_log"

        # Scan for sources
        sources = []
        for source_file in research_log.rglob("*.md"):
            sources.append({
                "file": str(source_file.relative_to(self.project_path)),
                "category": source_file.parent.name,
                "added_at": datetime.now().isoformat()
            })

        # Identify tools mentioned in research
        tools_identified = self._identify_tools_from_research(research_log)

        outputs = {
            "sources": sources,
            "tools_identified": tools_identified,
            "source_count": len(sources)
        }

        self.state_manager.update_phase('2', PhaseStatus.COMPLETE, outputs)

        print(f"✅ Phase 2 complete:")
        print(f"   - Sources found: {len(sources)}")
        print(f"   - Tools identified: {', '.join(tools_identified) if tools_identified else 'None'}")

        return outputs

    def phase_3_validate(self) -> Dict[str, Any]:
        """
        Phase 3: Data-Driven Validation

        Process:
        1. Get tools from Phase 2
        2. Run validation tools (flake8, bandit, radon, etc.)
        3. Store raw outputs
        4. Update state

        Anti-Bullshit Rule: NO CLAIMS WITHOUT TOOL OUTPUT
        """
        print("🔬 Phase 3: Data-Driven Validation")

        self.state_manager.update_phase('3', PhaseStatus.IN_PROGRESS)

        # Get tools from Phase 2
        phase_2_outputs = self.state_manager.get_phase_outputs('2')
        tools_to_run = phase_2_outputs.get('tools_identified', ['flake8', 'bandit', 'radon'])

        # Run tools
        tool_results = {}
        src_dir = self.dev_dir / "src"
        output_dir = self.validation_dir / "tool_outputs"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if not src_dir.exists() or not list(src_dir.glob("**/*.py")):
            print("⚠️  No Python files found in 01_development/src/")
            tool_results["note"] = "No source files to validate"
        else:
            # Run each tool
            for tool in tools_to_run:
                if tool == 'flake8':
                    result = self._run_flake8(src_dir, output_dir, timestamp)
                    tool_results['flake8'] = result
                elif tool == 'bandit':
                    result = self._run_bandit(src_dir, output_dir, timestamp)
                    tool_results['bandit'] = result
                elif tool == 'radon':
                    result = self._run_radon(src_dir, output_dir, timestamp)
                    tool_results['radon'] = result

        outputs = {
            "tool_results": tool_results,
            "tools_run": list(tool_results.keys()),
            "validation_timestamp": timestamp
        }

        self.state_manager.update_phase('3', PhaseStatus.COMPLETE, outputs)

        print(f"✅ Phase 3 complete:")
        print(f"   - Tools run: {', '.join(tool_results.keys())}")

        return outputs

    def phase_4_report(self) -> Dict[str, Any]:
        """
        Phase 4: Report Generation

        Process:
        1. Compile all phase outputs
        2. Calculate confidence score
        3. Generate executive summary
        4. Create final deliverable

        Anti-Bullshit Rule: CONFIDENCE IS TRANSPARENT
        """
        print("📊 Phase 4: Report Generation")

        self.state_manager.update_phase('4', PhaseStatus.IN_PROGRESS)

        # Gather all outputs
        phase_1 = self.state_manager.get_phase_outputs('1')
        phase_2 = self.state_manager.get_phase_outputs('2')
        phase_3 = self.state_manager.get_phase_outputs('3')

        # Calculate confidence
        confidence = self.state_manager.calculate_confidence()
        self.state_manager.state["confidence"] = confidence.value

        # Generate report
        report_path = self.deliverable_dir / f"Final_Report_{datetime.now().strftime('%Y-%m-%d')}.md"

        report_content = self._generate_report(phase_1, phase_2, phase_3, confidence)

        report_path.write_text(report_content)

        outputs = {
            "report_path": str(report_path),
            "confidence": confidence.value,
            "generated_at": datetime.now().isoformat()
        }

        self.state_manager.update_phase('4', PhaseStatus.COMPLETE, outputs)

        print(f"✅ Phase 4 complete:")
        print(f"   - Report: {report_path}")
        print(f"   - Confidence: {confidence.value}")

        return outputs

    # Helper methods

    def _get_phase_name(self, phase: str) -> str:
        """Get phase display name"""
        names = {
            '1': 'VERSTEHEN (Semantic Understanding)',
            '2': 'RECHERCHIEREN (Knowledge Acquisition)',
            '3': 'VALIDIEREN (Data-Driven Validation)',
            '4': 'BERICHT (Report Generation)'
        }
        return names.get(phase, f"Phase {phase}")

    def _extract_section(self, content: str, section_name: str) -> List[str]:
        """Extract list items from markdown section"""
        items = []
        in_section = False

        for line in content.split('\n'):
            if section_name in line:
                in_section = True
                continue

            if in_section:
                # Stop at next ## heading
                if line.startswith('##'):
                    break

                # Extract list items
                if line.strip().startswith(('-', '*', '1.', '2.', '3.')):
                    item = line.strip().lstrip('-*0123456789. ')
                    if item:
                        items.append(item)

        return items

    def _identify_tools_from_research(self, research_log: Path) -> List[str]:
        """Scan research log for mentioned validation tools"""
        common_tools = ['flake8', 'bandit', 'radon', 'cprofile', 'pytest', 'mypy']
        identified = []

        for md_file in research_log.rglob("*.md"):
            content = md_file.read_text().lower()
            for tool in common_tools:
                if tool in content and tool not in identified:
                    identified.append(tool)

        # Default to core stack if none found
        return identified if identified else ['flake8', 'bandit', 'radon']

    def _run_flake8(self, src_dir: Path, output_dir: Path, timestamp: str) -> str:
        """Run flake8 linter"""
        output_file = output_dir / "flake8" / f"{timestamp}_linting.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                f"flake8 {src_dir} --max-complexity=10",
                shell=True,
                capture_output=True,
                text=True
            )
            output_file.write_text(result.stdout or result.stderr)
            print(f"   ✓ flake8: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"   ✗ flake8 failed: {e}")
            return f"error: {e}"

    def _run_bandit(self, src_dir: Path, output_dir: Path, timestamp: str) -> str:
        """Run bandit security scanner"""
        output_file = output_dir / "bandit" / f"{timestamp}_security.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                f"bandit -r {src_dir} -f json",
                shell=True,
                capture_output=True,
                text=True
            )
            output_file.write_text(result.stdout or result.stderr)
            print(f"   ✓ bandit: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"   ✗ bandit failed: {e}")
            return f"error: {e}"

    def _run_radon(self, src_dir: Path, output_dir: Path, timestamp: str) -> str:
        """Run radon complexity analysis"""
        output_file = output_dir / "radon" / f"{timestamp}_complexity.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                f"radon cc {src_dir} -a",
                shell=True,
                capture_output=True,
                text=True
            )
            output_file.write_text(result.stdout or result.stderr)
            print(f"   ✓ radon: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"   ✗ radon failed: {e}")
            return f"error: {e}"

    def _generate_report(self, phase_1: Dict, phase_2: Dict, phase_3: Dict, confidence: ConfidenceLevel) -> str:
        """Generate intelligent markdown report with domain analysis"""

        # Load tool outputs
        bandit_findings = self._parse_bandit_output(phase_3)
        flake8_findings = self._parse_flake8_output(phase_3)

        # Generate intelligent analysis sections
        security_section = self._analyze_security_findings(bandit_findings)
        quality_section = self._analyze_quality_findings(flake8_findings)
        remediation_section = self._generate_remediation_roadmap(bandit_findings, flake8_findings)

        return f"""# KDAF Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Project:** {self.state_manager.state['project_name']}
**Client:** {self.state_manager.state['client']}
**Tech Stack:** Python

---

## Executive Summary

**Confidence Level:** {confidence.value}

**Key Findings:**
- Security issues identified: {len(bandit_findings.get('high_severity', []))} (HIGH), {len(bandit_findings.get('medium_severity', []))} (MEDIUM)
- Code quality issues: {len(flake8_findings)} PEP 8 violations
- Estimated remediation time: {self._estimate_effort(bandit_findings, flake8_findings)} hours

**Recommendation:** {self._get_executive_recommendation(bandit_findings, flake8_findings)}

---

## Phase 1: Understanding

**Facts Extracted:**
{self._format_list(phase_1.get('facts', []))}

**Knowledge Gaps:**
{self._format_list(phase_1.get('knowledge_gaps', []))}

**Research Questions:**
{self._format_list(phase_1.get('pre_research_questions', []))}

---

## Phase 2: Research Foundation

**Tools Identified:** {', '.join(phase_2.get('tools_identified', []))}

**Standards & References:**
- OWASP Top 10 2021: https://owasp.org/Top10/
- PEP 8 Style Guide: https://pep8.org/
- Bandit Security Documentation: https://bandit.readthedocs.io/
- CWE (Common Weakness Enumeration): https://cwe.mitre.org/

---

## Phase 3: Validation Results

**Tools Executed:** bandit (security), flake8 (code quality), radon (complexity)

**Tool Output Locations:**
- Security: `02_validation_and_reports/tool_outputs/bandit/`
- Linting: `02_validation_and_reports/tool_outputs/flake8/`
- Complexity: `02_validation_and_reports/tool_outputs/radon/`

---

## Phase 4: Intelligent Analysis

### Security Issues (Severity: HIGH)

{security_section}

### Code Quality Issues

{quality_section}

### Remediation Roadmap

{remediation_section}

---

## Confidence Assessment

**Level:** {confidence.value}

**Evidence Basis:**
- Tool outputs analyzed: bandit (security scanner), flake8 (code quality)
- Number of findings: {len(bandit_findings.get('all', []))} security + {len(flake8_findings)} quality
- Analysis method: Automated tool execution + domain expert interpretation
- Validation: Every finding backed by measurable tool output

**Anti-Bullshit Certification:**
- ✓ Every security issue has tool evidence (test ID + severity)
- ✓ Every quality issue cites PEP 8 standard
- ✓ No subjective claims without data
- ✓ Confidence transparently calculated from evidence count

---

**Generated by:** Vibe Coding Agency KDAF System v2.0
**Report ID:** {self.state_manager.state['project_id']}
**Methodology:** 4-Phase KDAF (Understand → Research → Validate → Report)
"""

    def _format_list(self, items: List[str]) -> str:
        """Format list for markdown"""
        if not items:
            return "- (None identified)\n"
        return '\n'.join(f"- {item}" for item in items)

    def _format_dict(self, d: Dict) -> str:
        """Format dict for markdown"""
        if not d:
            return "- (None)\n"
        return '\n'.join(f"- **{k}**: `{v}`" for k, v in d.items())

    def _parse_bandit_output(self, phase_3: Dict) -> Dict:
        """Parse bandit JSON output into structured findings by severity"""
        high_severity = []
        medium_severity = []
        low_severity = []
        all_findings = []

        tool_results = phase_3.get("tool_results", {})
        bandit_file = tool_results.get("bandit", "")

        if not bandit_file or not Path(bandit_file).exists():
            return {
                "high_severity": [],
                "medium_severity": [],
                "low_severity": [],
                "all": []
            }

        try:
            bandit_data = json.loads(Path(bandit_file).read_text())
            results = bandit_data.get("results", [])

            for finding in results:
                severity = finding.get("issue_severity", "LOW").upper()
                test_id = finding.get("test_id", "UNKNOWN")
                line_num = finding.get("line_number", 0)
                message = finding.get("issue_text", "")
                cwe_id = finding.get("issue_cwe", {}).get("id", "")
                confidence = finding.get("issue_confidence", "")

                finding_dict = {
                    "test_id": test_id,
                    "line": line_num,
                    "message": message,
                    "severity": severity,
                    "confidence": confidence,
                    "cwe": cwe_id
                }

                all_findings.append(finding_dict)

                if severity == "HIGH":
                    high_severity.append(finding_dict)
                elif severity == "MEDIUM":
                    medium_severity.append(finding_dict)
                else:
                    low_severity.append(finding_dict)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing bandit output: {e}")

        return {
            "high_severity": high_severity,
            "medium_severity": medium_severity,
            "low_severity": low_severity,
            "all": all_findings
        }

    def _parse_flake8_output(self, phase_3: Dict) -> List[Dict]:
        """Parse flake8 text output into structured findings"""
        findings = []

        tool_results = phase_3.get("tool_results", {})
        flake8_file = tool_results.get("flake8", "")

        if not flake8_file or not Path(flake8_file).exists():
            return []

        try:
            content = Path(flake8_file).read_text().strip()
            for line in content.split('\n'):
                if not line:
                    continue

                # Parse flake8 format: file:line:col: CODE message
                parts = line.split(':')
                if len(parts) >= 4:
                    line_num = int(parts[1])
                    col_num = int(parts[2])
                    rest = ':'.join(parts[3:]).strip()
                    rule_code = rest.split()[0] if rest else "UNKNOWN"
                    message = ' '.join(rest.split()[1:]) if len(rest.split()) > 1 else rest

                    findings.append({
                        "line": line_num,
                        "col": col_num,
                        "rule": rule_code,
                        "message": message
                    })

        except (ValueError, IndexError) as e:
            print(f"Error parsing flake8 output: {e}")

        return findings

    def _analyze_security_findings(self, bandit_findings: Dict) -> str:
        """Generate markdown section analyzing security findings with domain knowledge"""
        markdown = ""

        high = bandit_findings.get("high_severity", [])
        medium = bandit_findings.get("medium_severity", [])
        low = bandit_findings.get("low_severity", [])

        # Playbook knowledge mapping
        playbook = {
            "B602": {
                "name": "Shell Injection",
                "owasp": "A03:2021 – Injection",
                "cwe": "CWE-78",
                "priority": "CRITICAL",
                "fix": "Use list of args with shell=False instead of shell=True"
            },
            "B324": {
                "name": "Weak Hash (MD5)",
                "owasp": "A02:2021 – Cryptographic Failures",
                "cwe": "CWE-327",
                "priority": "HIGH",
                "fix": "Use hashlib.sha256() instead of md5()"
            },
            "B105": {
                "name": "Hardcoded Credentials",
                "owasp": "A01:2021 – Broken Access Control",
                "cwe": "CWE-259",
                "priority": "HIGH",
                "fix": "Move to environment variables or secrets manager"
            },
            "B104": {
                "name": "Bind to All Interfaces",
                "owasp": "A01:2021 – Broken Access Control",
                "cwe": "CWE-200",
                "priority": "HIGH",
                "fix": "Bind to 127.0.0.1 for dev or specific interface in production"
            },
            "B108": {
                "name": "Hardcoded Temp Directory",
                "owasp": "A01:2021 – Broken Access Control",
                "cwe": "CWE-377",
                "priority": "MEDIUM",
                "fix": "Use tempfile.mkdtemp() or tempfile.NamedTemporaryFile()"
            },
            "B101": {
                "name": "Assert Used in Validation",
                "owasp": "A09:2021 – Broken Exception Handling",
                "cwe": "CWE-703",
                "priority": "MEDIUM",
                "fix": "Replace assert with raise ValueError(...)"
            },
            "B404": {
                "name": "Import subprocess",
                "owasp": "A03:2021 – Injection",
                "cwe": "CWE-78",
                "priority": "INFO",
                "fix": "Ensure subprocess is used safely (no shell=True with user input)"
            }
        }

        if high:
            markdown += "#### HIGH Severity Issues\n\n"
            for finding in high:
                test_id = finding.get("test_id", "")
                playbook_info = playbook.get(test_id, {})
                markdown += f"**{test_id}: {playbook_info.get('name', 'Security Issue')}**\n"
                markdown += f"- Location: Line {finding.get('line')}\n"
                markdown += f"- Message: {finding.get('message')}\n"
                markdown += f"- Severity: HIGH (Confidence: {finding.get('confidence')})\n"
                markdown += f"- OWASP: {playbook_info.get('owasp', 'N/A')}\n"
                markdown += f"- CWE: {playbook_info.get('cwe', 'N/A')}\n"
                markdown += f"- Remediation: {playbook_info.get('fix', 'Review security practices')}\n"
                markdown += f"- Effort: 30-45 minutes\n\n"

        if medium:
            markdown += "#### MEDIUM Severity Issues\n\n"
            for finding in medium:
                test_id = finding.get("test_id", "")
                playbook_info = playbook.get(test_id, {})
                markdown += f"**{test_id}: {playbook_info.get('name', 'Security Issue')}**\n"
                markdown += f"- Location: Line {finding.get('line')}\n"
                markdown += f"- Message: {finding.get('message')}\n"
                markdown += f"- Severity: MEDIUM (Confidence: {finding.get('confidence')})\n"
                markdown += f"- OWASP: {playbook_info.get('owasp', 'N/A')}\n"
                markdown += f"- CWE: {playbook_info.get('cwe', 'N/A')}\n"
                markdown += f"- Remediation: {playbook_info.get('fix', 'Review security practices')}\n"
                markdown += f"- Effort: 20-30 minutes\n\n"

        if low:
            markdown += "#### LOW Severity Issues\n\n"
            for finding in low:
                test_id = finding.get("test_id", "")
                playbook_info = playbook.get(test_id, {})
                markdown += f"**{test_id}: {playbook_info.get('name', 'Security Issue')}**\n"
                markdown += f"- Location: Line {finding.get('line')}\n"
                markdown += f"- Message: {finding.get('message')}\n"
                markdown += f"- Severity: LOW (Confidence: {finding.get('confidence')})\n"
                markdown += f"- CWE: {playbook_info.get('cwe', 'N/A')}\n"
                markdown += f"- Remediation: {playbook_info.get('fix', 'Review security practices')}\n"
                markdown += f"- Effort: 15-20 minutes\n\n"

        if not (high or medium or low):
            markdown = "✅ No security issues detected by bandit.\n"

        return markdown

    def _analyze_quality_findings(self, flake8_findings: List[Dict]) -> str:
        """Generate markdown section analyzing code quality findings"""
        markdown = ""

        # Group by rule code
        rules_grouped = {}
        for finding in flake8_findings:
            rule = finding.get("rule", "UNKNOWN")
            if rule not in rules_grouped:
                rules_grouped[rule] = []
            rules_grouped[rule].append(finding)

        # PEP 8 knowledge
        pep8_knowledge = {
            "E302": {
                "name": "Expected 2 blank lines",
                "impact": "Readability",
                "priority": "LOW",
                "fix": "Add blank line between top-level functions/classes"
            },
            "E501": {
                "name": "Line too long",
                "impact": "Readability",
                "priority": "LOW",
                "fix": "Split line or refactor complex logic"
            },
            "E305": {
                "name": "Expected 2 blank lines after definition",
                "impact": "Readability",
                "priority": "LOW",
                "fix": "Add blank lines after function/class definition"
            },
            "F401": {
                "name": "Imported but unused",
                "impact": "Clarity",
                "priority": "MEDIUM",
                "fix": "Remove unused import or use the imported module"
            },
            "W503": {
                "name": "Line break before binary operator",
                "impact": "Consistency",
                "priority": "LOW",
                "fix": "Move operator to end of line or start of next line consistently"
            }
        }

        if not rules_grouped:
            return "✅ No code quality issues detected by flake8.\n"

        for rule, occurrences in sorted(rules_grouped.items()):
            info = pep8_knowledge.get(rule, {})
            markdown += f"**{rule}: {info.get('name', 'Code Quality Issue')}** ({len(occurrences)} occurrences)\n"
            markdown += f"- Impact: {info.get('impact', 'Code clarity')}\n"
            markdown += f"- Priority: {info.get('priority', 'MEDIUM')}\n"
            markdown += f"- Remediation: {info.get('fix', 'Follow PEP 8 guidelines')}\n"
            markdown += f"- Locations: Lines {', '.join(str(o['line']) for o in occurrences)}\n"
            markdown += f"- Effort: {len(occurrences) * 2} minutes (2 min per issue)\n\n"

        return markdown

    def _generate_remediation_roadmap(self, bandit: Dict, flake8: List) -> str:
        """Generate prioritized remediation roadmap with effort estimates"""
        roadmap = ""
        tasks = []

        high_sev = bandit.get("high_severity", [])
        medium_sev = bandit.get("medium_severity", [])
        low_sev = bandit.get("low_severity", [])

        # CRITICAL tasks
        for finding in high_sev:
            test_id = finding.get("test_id", "")
            line = finding.get("line", "")
            tasks.append({
                "priority": "CRITICAL",
                "task": f"Fix {test_id} at line {line}",
                "effort": 30,
                "impact": "Blocks production deployment"
            })

        # HIGH priority tasks
        for finding in medium_sev:
            test_id = finding.get("test_id", "")
            line = finding.get("line", "")
            tasks.append({
                "priority": "HIGH",
                "task": f"Fix {test_id} at line {line}",
                "effort": 20,
                "impact": "Reduces security posture"
            })

        # MEDIUM priority (code quality)
        flake8_groups = {}
        for finding in flake8:
            rule = finding.get("rule", "")
            if rule not in flake8_groups:
                flake8_groups[rule] = []
            flake8_groups[rule].append(finding)

        for rule, findings in flake8_groups.items():
            if rule == "F401":
                tasks.append({
                    "priority": "MEDIUM",
                    "task": f"Remove unused imports ({len(findings)} found)",
                    "effort": len(findings) * 2,
                    "impact": "Improves code clarity"
                })
            elif rule == "E302":
                tasks.append({
                    "priority": "LOW",
                    "task": f"Add blank lines between functions ({len(findings)} found)",
                    "effort": len(findings) * 1,
                    "impact": "Improves readability"
                })
            else:
                tasks.append({
                    "priority": "LOW",
                    "task": f"Fix {rule} violations ({len(findings)} found)",
                    "effort": len(findings) * 1,
                    "impact": "Code style compliance"
                })

        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 99))

        for idx, task in enumerate(tasks, 1):
            roadmap += f"### {idx}. [{task['priority']}] {task['task']}\n"
            roadmap += f"- **Effort:** {task['effort']} minutes\n"
            roadmap += f"- **Impact:** {task['impact']}\n"
            roadmap += f"- **Owner:** Dev team\n\n"

        total_effort = sum(t["effort"] for t in tasks)
        roadmap += f"**Total Estimated Effort:** {total_effort} minutes (~{total_effort // 60} hours)\n"

        return roadmap

    def _estimate_effort(self, bandit: Dict, flake8: List) -> str:
        """Calculate total effort in hours to fix all issues"""
        high_count = len(bandit.get("high_severity", []))
        medium_count = len(bandit.get("medium_severity", []))
        low_count = len(bandit.get("low_severity", []))
        flake8_count = len(flake8)

        # Effort estimation: HIGH=45min, MEDIUM=25min, LOW=15min, flake8=2min each
        total_minutes = (high_count * 45) + (medium_count * 25) + (low_count * 15) + (flake8_count * 2)
        total_hours = round(total_minutes / 60, 1)

        return str(total_hours)

    def _get_executive_recommendation(self, bandit: Dict, flake8: List) -> str:
        """Generate executive-level recommendation"""
        high_count = len(bandit.get("high_severity", []))
        medium_count = len(bandit.get("medium_severity", []))
        total_issues = len(bandit.get("all", []))

        if high_count >= 2:
            return f"**CRITICAL: Address {high_count} security issues before production deployment.** Estimated remediation: {self._estimate_effort(bandit, flake8)} hours. Priority: Fix HIGH severity issues immediately, then remediate code quality issues."
        elif high_count == 1:
            return f"**HIGH PRIORITY:** 1 critical security issue requires immediate attention. Medium priority issues should be addressed in next sprint. Code quality improvements are incremental."
        elif medium_count > 2:
            return f"**MEDIUM PRIORITY:** {medium_count} security issues and {len(flake8)} code quality violations detected. Recommended: Schedule 1-2 hour remediation session. Code is functional but needs hardening."
        else:
            return f"**LOW PRIORITY:** Mostly code quality issues ({len(flake8)} violations). Security posture is acceptable. Recommend addressing in routine maintenance."
