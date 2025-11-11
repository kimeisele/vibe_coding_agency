#!/usr/bin/env python3
"""
VIBE CODING AGENCY CLI
======================
The orchestration layer for the Knowledge-Driven Agency Framework (KDAF).

Commands:
  new-project  → Create new KDAF-structured project
  validate     → Run Phase 3 validation tools
  research     → Generate research templates
  report       → Compile final deliverable

Philosophy:
  - NO claims without TOOL OUTPUT or CITED SOURCE
  - External validation ONLY (eliminate circular reasoning)
  - Cumulative intelligence (every project grows /hq/knowledge_base)
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json
import shutil

# Add shared/orchestration to path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from orchestration import WorkflowOrchestrator, StateManager

# Monorepo paths
REPO_ROOT = Path(__file__).parent.parent.parent.absolute()
HQ = REPO_ROOT / "hq"
CLIENTS = REPO_ROOT / "clients"
SHARED = REPO_ROOT / "shared"
TEMPLATE = SHARED / "templates" / "kdaf_project"

class VibeColors:
    """Anti-bullshit color coding"""
    PROVEN = '\033[92m'  # Green - backed by tools/sources
    SPECULATION = '\033[91m'  # Red - needs validation
    INPROGRESS = '\033[93m'  # Yellow - research phase
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_vibe(msg, color=VibeColors.RESET):
    """Print with vibe"""
    print(f"{color}{msg}{VibeColors.RESET}")

def new_project(client_name: str, project_name: str):
    """
    Create new KDAF-structured project.

    Structure enforces:
    - Phase 1: Semantic understanding (no assumptions)
    - Phase 2: Research (external sources only)
    - Phase 3: Validation (tool outputs only)
    """
    print_vibe(f"\n🎯 Creating KDAF project: {project_name}", VibeColors.BOLD)

    # Client directory
    client_dir = CLIENTS / f"client_{client_name}"
    client_dir.mkdir(exist_ok=True)

    # Project directory
    project_dir = client_dir / project_name
    if project_dir.exists():
        print_vibe(f"❌ Project {project_name} already exists!", VibeColors.SPECULATION)
        return

    # Create KDAF structure
    structure = {
        "00_scoping_and_research": {
            "01_input_analysis.md": INPUT_ANALYSIS_TEMPLATE,
            "02_research_log": {
                "docs": {},
                "articles": {},
                "examples": {}
            },
            "03_pre_research_questions.md": PRE_RESEARCH_TEMPLATE
        },
        "01_development": {
            "src": {},
            "tests": {},
            "scripts": {},
            "README.md": DEV_README_TEMPLATE
        },
        "02_validation_and_reports": {
            "tool_outputs": {
                "flake8": {},
                "bandit": {},
                "radon": {},
                "cprofile": {}
            },
            "written_analysis": {}
        },
        "03_deliverables": {},
        "README.md": PROJECT_README_TEMPLATE.format(
            project_name=project_name,
            client_name=client_name,
            date=datetime.now().strftime("%Y-%m-%d")
        )
    }

    create_structure(project_dir, structure)

    print_vibe(f"✓ Project created at: {project_dir}", VibeColors.PROVEN)
    print_vibe(f"\n📋 Next steps:", VibeColors.INPROGRESS)
    print_vibe(f"  1. Fill out: {project_dir}/00_scoping_and_research/01_input_analysis.md")
    print_vibe(f"  2. Run research: vibe research --project {project_name}")
    print_vibe(f"  3. Run validation: vibe validate --project {project_name}")

def create_structure(base_path: Path, structure: dict):
    """Recursively create directory structure with templates"""
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if content:
                path.write_text(content)
            else:
                path.touch()

def validate_project(project_path: Path):
    """
    Run Phase 3 validation tools.

    Core Rule: NO claims without TOOL OUTPUT or CITED SOURCE
    """
    print_vibe(f"\n🔬 Running KDAF Phase 3: Validation", VibeColors.BOLD)

    dev_dir = project_path / "01_development" / "src"
    output_dir = project_path / "02_validation_and_reports" / "tool_outputs"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    if not dev_dir.exists() or not list(dev_dir.glob("**/*.py")):
        print_vibe("⚠️  No Python files found in 01_development/src/", VibeColors.SPECULATION)
        return

    # Run validation stack
    tools = [
        {
            "name": "flake8",
            "cmd": f"flake8 {dev_dir} --max-complexity=10",
            "output": output_dir / "flake8" / f"{timestamp}_linting.txt"
        },
        {
            "name": "bandit",
            "cmd": f"bandit -r {dev_dir} -f json",
            "output": output_dir / "bandit" / f"{timestamp}_security.json"
        },
        {
            "name": "radon",
            "cmd": f"radon cc {dev_dir} -a",
            "output": output_dir / "radon" / f"{timestamp}_complexity.txt"
        }
    ]

    for tool in tools:
        print_vibe(f"\n→ Running {tool['name']}...", VibeColors.INPROGRESS)
        tool['output'].parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                tool['cmd'],
                shell=True,
                capture_output=True,
                text=True
            )

            output_text = result.stdout or result.stderr
            tool['output'].write_text(output_text)

            print_vibe(f"  ✓ Output saved: {tool['output']}", VibeColors.PROVEN)

        except Exception as e:
            print_vibe(f"  ✗ {tool['name']} failed: {e}", VibeColors.SPECULATION)

    print_vibe(f"\n✓ Validation complete!", VibeColors.PROVEN)
    print_vibe(f"📊 Analyze outputs in: {output_dir}", VibeColors.INPROGRESS)

def research_helper(project_path: Path):
    """Generate Phase 2 research checklist"""
    print_vibe(f"\n🔍 KDAF Phase 2: Research Protocol", VibeColors.BOLD)

    checklist = f"""
# Research Checklist (Phase 2)
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## ✓ Official Documentation (PRIMARY SOURCES)
Directive: **NEVER claim without SOURCE**

- [ ] Technology/framework official docs
- [ ] API reference documentation
- [ ] Migration guides (if version change)
- [ ] Security advisories

Sources found:
-

## ✓ Current Best Practices (SECONDARY SOURCES)
Validation: **3+ Sources** + **<{datetime.now().year}** (Currency)

- [ ] Industry blog posts (3+ consensus)
- [ ] Conference talks / tech talks
- [ ] Academic papers (if applicable)

Sources found:
-
-
-

## ✓ Real-World Examples (CASE STUDIES)
Directive: Ground in **PRACTICE**, not theory

- [ ] GitHub repositories using this tech
- [ ] Production use cases at scale
- [ ] Known pitfalls / gotchas

Examples found:
-

## ✓ Tool & Metrics Research
Function: Define VALIDATION PLAN before work begins

- [ ] Profiling tools for this stack
- [ ] Linters and static analyzers
- [ ] Performance benchmarks

Tools identified:
-

---

**Anti-Bullshit Check:**
□ Every recommendation has SOURCE
□ Best practices have 3+ citations
□ Examples are from REAL projects
□ Validation tools are SPECIFIC (not "we should test")
"""

    research_file = project_path / "00_scoping_and_research" / "02_research_checklist.md"
    research_file.write_text(checklist)

    print_vibe(f"✓ Research checklist created: {research_file}", VibeColors.PROVEN)

# Templates
INPUT_ANALYSIS_TEMPLATE = f"""# Phase 1: Input Analysis (Semantic Understanding)
Date: {datetime.now().strftime("%Y-%m-%d")}

## Request Classification
**Type:** [ ] Audit | [ ] Build | [ ] Refactor | [ ] Investigation

## Facts Extracted
<!-- List ONLY objective facts from the request. NO interpretation. -->

1.
2.
3.

## Knowledge Gaps (CRITICAL UNKNOWNS)
<!-- What information is MISSING to proceed? -->

1.
2.
3.

## Constraints & Requirements
**Functional:**
-

**Non-Functional:**
-

**Explicit Constraints:**
-

## Pre-Research Questions
<!-- Questions that MUST be answered in Phase 2 -->

1. **Technical:**
2. **Validation:** How can we MEASURE success?
3. **Scope:**

---

**Anti-Bullshit Check:**
□ No assumptions made
□ Knowledge gaps explicitly listed
□ Validation method identified
"""

PRE_RESEARCH_TEMPLATE = """# Pre-Research Questions

Before starting Phase 2, these questions guide our research:

## 1. Technical Questions


## 2. Validation Questions
How will we PROVE this works?


## 3. Scope Questions
What's in scope vs out of scope?


## 4. Risk Questions
What could go wrong?

"""

DEV_README_TEMPLATE = """# Development Environment

## Setup


## Running Validation
```bash
vibe validate --project <project_name>
```

## Testing


"""

PROJECT_README_TEMPLATE = """# {project_name}

**Client:** {client_name}
**Started:** {date}
**Status:** 🚧 In Progress

## KDAF Status

- [ ] Phase 1: Input Analysis (Semantic Understanding)
- [ ] Phase 2: Knowledge Acquisition (Research)
- [ ] Phase 3: Data-Driven Validation
- [ ] Deliverable: Final Report

## Confidence Assessment

**CURRENT:** UNKNOWN
**Reason:** Not yet validated

## Quick Links

- Input Analysis: `00_scoping_and_research/01_input_analysis.md`
- Research Log: `00_scoping_and_research/02_research_log/`
- Validation Outputs: `02_validation_and_reports/tool_outputs/`
- Deliverables: `03_deliverables/`
"""

def find_project(project_name: str) -> Path:
    """Find project by name in /clients"""
    for client_dir in CLIENTS.iterdir():
        if client_dir.is_dir() and client_dir.name.startswith("client_"):
            project_dir = client_dir / project_name
            if project_dir.exists():
                return project_dir

    print_vibe(f"❌ Project '{project_name}' not found in /clients", VibeColors.SPECULATION)
    sys.exit(1)

def run_workflow(project_name: str, phases: str = "full"):
    """
    Run KDAF workflow (Phase 1 → 2 → 3 → 4)

    Args:
        project_name: Name of project in /clients
        phases: Comma-separated phases (e.g., "1,2,3" or "full")
    """
    print_vibe(f"\n🚀 Running KDAF Workflow", VibeColors.BOLD)

    project_path = find_project(project_name)

    # Parse phases
    if phases == "full":
        phase_list = ['1', '2', '3', '4']
    else:
        phase_list = phases.split(',')

    print_vibe(f"   Project: {project_path}", VibeColors.PROVEN)
    print_vibe(f"   Phases: {', '.join(phase_list)}", VibeColors.PROVEN)

    # Run orchestrator
    orchestrator = WorkflowOrchestrator(project_path)
    result = orchestrator.run_analysis(phase_list)

    # Print summary
    print_vibe(f"\n{'='*60}", VibeColors.BOLD)
    print_vibe(f"📊 WORKFLOW SUMMARY", VibeColors.BOLD)
    print_vibe(f"{'='*60}", VibeColors.BOLD)

    print_vibe(f"\n✅ Phases completed: {len(result['phases_run'])}/{len(phase_list)}", VibeColors.PROVEN)

    if result['errors']:
        print_vibe(f"\n⚠️  Errors: {len(result['errors'])}", VibeColors.SPECULATION)
        for error in result['errors']:
            print_vibe(f"   - {error}", VibeColors.SPECULATION)

    # Final state
    final_state = result['final_state']
    print_vibe(f"\n📋 Final State:", VibeColors.INPROGRESS)
    print_vibe(f"   - Confidence: {final_state['confidence']}", VibeColors.INPROGRESS)
    print_vibe(f"   - Next action: {final_state['next_action']}", VibeColors.INPROGRESS)

    # If Phase 4 complete, show report path
    if '4' in [p['phase'] for p in result['phases_run'] if p['status'] == 'COMPLETE']:
        phase_4_result = [p for p in result['phases_run'] if p['phase'] == '4'][0]['result']
        print_vibe(f"\n📊 Report generated: {phase_4_result['report_path']}", VibeColors.PROVEN)

def show_status(project_name: str):
    """Show project status"""
    print_vibe(f"\n📊 Project Status", VibeColors.BOLD)

    project_path = find_project(project_name)

    state_manager = StateManager(project_path)
    summary = state_manager.get_summary()

    print_vibe(f"\n   Project: {summary['project_name']}", VibeColors.PROVEN)
    print_vibe(f"   Client: {summary['client']}", VibeColors.PROVEN)
    print_vibe(f"   Last updated: {summary['last_updated']}", VibeColors.INPROGRESS)

    print_vibe(f"\n   Phase Status:", VibeColors.BOLD)
    for phase, status in summary['phase_statuses'].items():
        color = VibeColors.PROVEN if status == "COMPLETE" else VibeColors.INPROGRESS
        print_vibe(f"      {phase}: {status}", color)

    print_vibe(f"\n   Confidence: {summary['confidence']}", VibeColors.INPROGRESS)
    print_vibe(f"   Next action: {summary['next_action']}", VibeColors.INPROGRESS)

def main():
    parser = argparse.ArgumentParser(
        description="Vibe Coding Agency - Knowledge-Driven Agency Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibe new-project --client acme_corp --name django_audit
  vibe run --project django_audit --phases full
  vibe run --project django_audit --phases 1,2,3
  vibe status --project django_audit
  vibe validate --project django_audit
  vibe research --project django_audit
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # new-project
    new_parser = subparsers.add_parser('new-project', help='Create new KDAF project')
    new_parser.add_argument('--client', required=True, help='Client name')
    new_parser.add_argument('--name', required=True, help='Project name')

    # run (NEW - The Orchestrator!)
    run_parser = subparsers.add_parser('run', help='Run KDAF workflow (Phase 1→2→3→4)')
    run_parser.add_argument('--project', required=True, help='Project name')
    run_parser.add_argument('--phases', default='full', help='Phases to run: "full" or "1,2,3"')

    # status (NEW - Check project state)
    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('--project', required=True, help='Project name')

    # validate (Legacy - now part of Phase 3)
    validate_parser = subparsers.add_parser('validate', help='Run Phase 3 validation')
    validate_parser.add_argument('--project', required=True, help='Project name')

    # research (Legacy - now part of Phase 2)
    research_parser = subparsers.add_parser('research', help='Generate research checklist')
    research_parser.add_argument('--project', required=True, help='Project name')

    args = parser.parse_args()

    if args.command == 'new-project':
        new_project(args.client, args.name)
    elif args.command == 'run':
        run_workflow(args.project, args.phases)
    elif args.command == 'status':
        show_status(args.project)
    elif args.command == 'validate':
        project_path = find_project(args.project)
        validate_project(project_path)
    elif args.command == 'research':
        project_path = find_project(args.project)
        research_helper(project_path)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
