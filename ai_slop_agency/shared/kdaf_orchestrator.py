#!/usr/bin/env python3
"""
KDAF Orchestrator - Central CLI for Vibe Coding Agency Infrastructure

This orchestrator consolidates all loose scripts into a single, coordinated workflow:
- setup_agency: Consolidate READMEs, create AI_SLOP_WATCHLIST, clean infrastructure
- onboard_client: Create KDAF-compliant client structure
- run_audit: Orchestrate run_real_audit.py
- triage: Orchestrate triage_smart.py
- fix: Orchestrate kdaf-fix

Usage:
    kdaf_orchestrator.py setup-agency
    kdaf_orchestrator.py onboard-client --name "agency-toolkit"
    kdaf_orchestrator.py run-audit --target "agency-toolkit"
    kdaf_orchestrator.py triage --input "examples/real_audit_output/security_*.json"
    kdaf_orchestrator.py fix --input "examples/triage_output/security_critical.json"
"""

import click
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# ============================================================================
# Constants
# ============================================================================

ROOT_DIR = Path(__file__).parent.parent.parent
AI_SLOP_AGENCY = ROOT_DIR / "ai_slop_agency"
HQ = AI_SLOP_AGENCY / "hq"
CLIENTS = AI_SLOP_AGENCY / "clients"
LEGACY = AI_SLOP_AGENCY / "_legacy_graveyard"


# ============================================================================
# Setup Agency Command
# ============================================================================

@click.group()
def cli():
    """KDAF Orchestrator - Central command for agency infrastructure"""
    pass


@cli.command('setup-agency')
def setup_agency():
    """
    Setup agency infrastructure (Task 1):
    1. Consolidate widersprüchliche READMEs into single source of truth
    2. Archive old READMEs to _legacy_graveyard
    3. Create AI_SLOP_WATCHLIST.md (measurable definition of "Dreck")
    """
    click.echo("=" * 80)
    click.echo("KDAF ORCHESTRATOR - SETUP AGENCY")
    click.echo("=" * 80)
    click.echo()

    # Step 1: Create AI_SLOP_WATCHLIST.md
    click.echo("📋 Step 1: Creating AI_SLOP_WATCHLIST.md...")
    watchlist_content = """# AI Slop Watchlist

**Purpose:** Measurable definition of "Dreck" (AI-generated low-quality code) that can be used by meta-audit.

## Categories

### 1. Hardcoded Values
**Pattern:** Hardcoded credentials, IPs, paths, or configuration values
**Examples:**
- `password = "secret123"`
- `host = "0.0.0.0"`
- `path = "/tmp/hardcoded"`

**Detection:** Bandit security checks (B104, B108)
**Severity:** HIGH

### 2. Empty Exception Handlers
**Pattern:** Try-except with pass or empty handler
**Examples:**
```python
try:
    risky_operation()
except:
    pass  # AI slop
```

**Detection:** Bandit B110
**Severity:** MEDIUM

### 3. Shell=True in Subprocess
**Pattern:** Using shell=True without input validation
**Examples:**
```python
subprocess.run(cmd, shell=True)  # Dangerous
```

**Detection:** Bandit B604
**Severity:** CRITICAL

### 4. Assert in Production Code
**Pattern:** Using assert for validation (removed in optimized bytecode)
**Examples:**
```python
assert user.is_authenticated  # Will be removed with -O
```

**Detection:** Bandit B101
**False Positive:** Acceptable in tests/
**Severity:** MEDIUM

### 5. God Objects
**Pattern:** Classes/modules with excessive complexity
**Metrics:**
- Lines of code > 500
- Cyclomatic complexity > 20
- Methods > 30

**Detection:** Radon complexity + meta-audit god_object
**Severity:** HIGH

## Usage

This watchlist can be used with meta-audit:
```bash
python run_real_audit.py --target agency-toolkit
python triage_smart.py examples/real_audit_output/security_*.json
```

## Evolution

This watchlist will grow as we identify new patterns. Each pattern must be:
1. Measurable (detected by tools)
2. Actionable (can be fixed)
3. Documented (examples provided)

**Last Updated:** """ + datetime.now().strftime("%Y-%m-%d")

    watchlist_path = HQ / "AI_SLOP_WATCHLIST.md"
    watchlist_path.write_text(watchlist_content)
    click.echo(f"  ✓ Created: {watchlist_path}")
    click.echo()

    # Step 2: Create consolidated README for ai_slop_agency
    click.echo("📚 Step 2: Creating ai_slop_agency/README.md (Single Source of Truth)...")

    agency_readme = """# AI Slop Agency - KDAF System

**Single Source of Truth for agency infrastructure and client structure**

## What Is This?

This is the orchestration layer for the Vibe Coding Agency - a Knowledge-Driven consulting system that prevents hallucinations through systematic methodology.

## Directory Structure

```
ai_slop_agency/
├── shared/
│   └── kdaf_orchestrator.py      ← The central CLI orchestrator
├── hq/
│   ├── 01_playbooks/              ← KDAF protocols and workflows
│   ├── 02_knowledge_base/         ← Growing intelligence base
│   └── AI_SLOP_WATCHLIST.md       ← Measurable quality definition
├── clients/
│   ├── CLIENT_TEMPLATE/           ← Template for new clients
│   └── <client-name>/             ← Individual client projects
│       ├── 00_INTAKE/             ← Initial requirements
│       ├── 01_AUDIT_DATA/         ← Raw analysis results
│       ├── 02_REFACTORING/        ← Curated fixes for kdaf-fix
│       └── 03_DELIVERABLES/       ← Final reports and artifacts
└── _legacy_graveyard/             ← Archived experimental code
```

## The Orchestrator

The `kdaf_orchestrator.py` is the central command for all operations:

### Setup Commands

```bash
# Setup agency infrastructure
./ai_slop_agency/shared/kdaf_orchestrator.py setup_agency

# Onboard new client
./ai_slop_agency/shared/kdaf_orchestrator.py onboard_client --name "agency-toolkit"
```

### Analysis Workflow

```bash
# 1. Run audit (calls run_real_audit.py)
./ai_slop_agency/shared/kdaf_orchestrator.py run_audit --target "agency-toolkit"

# 2. Triage findings (calls triage_smart.py)
./ai_slop_agency/shared/kdaf_orchestrator.py triage --input "examples/real_audit_output/security_*.json"

# 3. Apply fixes (calls kdaf-fix)
./ai_slop_agency/shared/kdaf_orchestrator.py fix --input "examples/triage_output/security_critical.json"
```

## The Three Scripts (Now Orchestrated)

Previously, these were loose scripts. Now they're coordinated by the orchestrator:

1. **run_real_audit.py** (The Diagnostiker) - Calls meta-audit collectors
2. **triage_smart.py** (The Triage-Arzt) - Filters false positives
3. **tools/kdaf-fix** (The Chirurg) - Applies fixes interactively

## KDAF Principles

### 1. Knowledge-Driven
- No hallucinations - only tool outputs and cited sources
- Complete audit trail
- Measurable quality (AI_SLOP_WATCHLIST.md)

### 2. Phase-Based Structure
- **00_INTAKE** - Gather requirements
- **01_AUDIT_DATA** - Raw tool outputs (security.json, complexity.json, etc.)
- **02_REFACTORING** - Curated fixes ready for kdaf-fix
- **03_DELIVERABLES** - Final reports and artifacts

### 3. Single Source of Truth
- This README is the authoritative documentation
- All workflows go through the orchestrator
- No conflicting documentation

## Getting Started

1. **Setup the agency:**
   ```bash
   ./ai_slop_agency/shared/kdaf_orchestrator.py setup_agency
   ```

2. **Onboard your first client:**
   ```bash
   ./ai_slop_agency/shared/kdaf_orchestrator.py onboard_client --name "my-client"
   ```

3. **Run analysis:**
   ```bash
   ./ai_slop_agency/shared/kdaf_orchestrator.py run_audit --target "my-client"
   ```

## Status

- ✅ Orchestrator CLI built
- ✅ Directory structure established
- ✅ AI_SLOP_WATCHLIST.md created
- ✅ Single Source of Truth established

**Last Updated:** """ + datetime.now().strftime("%Y-%m-%d")

    agency_readme_path = AI_SLOP_AGENCY / "README.md"
    agency_readme_path.write_text(agency_readme)
    click.echo(f"  ✓ Created: {agency_readme_path}")
    click.echo()

    # Step 3: Archive old conflicting docs (if they exist)
    click.echo("📦 Step 3: Archiving old conflicting READMEs...")

    old_docs = [
        ROOT_DIR / "README_ACTIVE_SYSTEM.md",
        ROOT_DIR / "SYSTEM_ARCHITECTURE.md",
    ]

    archived_count = 0
    for doc in old_docs:
        if doc.exists():
            archive_path = LEGACY / doc.name
            doc.rename(archive_path)
            click.echo(f"  ✓ Archived: {doc.name} → _legacy_graveyard/")
            archived_count += 1

    if archived_count == 0:
        click.echo("  ℹ No conflicting docs found to archive")

    click.echo()

    # Summary
    click.echo("=" * 80)
    click.echo("✅ SETUP COMPLETE")
    click.echo("=" * 80)
    click.echo()
    click.echo("Created:")
    click.echo(f"  ✓ {watchlist_path}")
    click.echo(f"  ✓ {agency_readme_path}")
    click.echo(f"  ✓ Directory structure: hq/, clients/, _legacy_graveyard/")
    if archived_count > 0:
        click.echo(f"  ✓ Archived {archived_count} old docs")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review AI_SLOP_WATCHLIST.md")
    click.echo("  2. Run: ./ai_slop_agency/shared/kdaf_orchestrator.py onboard_client --name 'agency-toolkit'")
    click.echo()


# ============================================================================
# Onboard Client Command
# ============================================================================

@cli.command('onboard-client')
@click.option('--name', required=True, help='Client name (e.g., "agency-toolkit")')
def onboard_client(name: str):
    """
    Onboard new client (Task 2):
    1. Create CLIENT_TEMPLATE if it doesn't exist
    2. Copy template to clients/<name>
    3. Create KDAF-compliant phase structure
    """
    click.echo("=" * 80)
    click.echo(f"KDAF ORCHESTRATOR - ONBOARD CLIENT: {name}")
    click.echo("=" * 80)
    click.echo()

    # Step 1: Ensure CLIENT_TEMPLATE exists
    template_dir = CLIENTS / "CLIENT_TEMPLATE"
    if not template_dir.exists():
        click.echo("📋 Step 1: Creating CLIENT_TEMPLATE...")
        _create_client_template()
        click.echo(f"  ✓ Created: {template_dir}")
    else:
        click.echo("📋 Step 1: CLIENT_TEMPLATE already exists")

    click.echo()

    # Step 2: Create client directory
    client_dir = CLIENTS / name

    if client_dir.exists():
        click.echo(f"⚠️  Client '{name}' already exists at: {client_dir}")
        if not click.confirm("Overwrite?"):
            click.echo("Aborted.")
            return

    click.echo(f"📁 Step 2: Creating client structure for '{name}'...")

    # Copy template
    import shutil
    if client_dir.exists():
        shutil.rmtree(client_dir)

    shutil.copytree(template_dir, client_dir)

    # Update client-specific README
    client_readme = client_dir / "README.md"
    if client_readme.exists():
        content = client_readme.read_text()
        content = content.replace("CLIENT_TEMPLATE", name)
        content = content.replace("<client-name>", name)
        client_readme.write_text(content)

    click.echo(f"  ✓ Created: {client_dir}")
    click.echo()

    # Summary
    click.echo("=" * 80)
    click.echo("✅ CLIENT ONBOARDED")
    click.echo("=" * 80)
    click.echo()
    click.echo(f"Client '{name}' ready at: {client_dir}")
    click.echo()
    click.echo("Structure:")
    for phase_dir in sorted(client_dir.glob("*")):
        if phase_dir.is_dir():
            click.echo(f"  ✓ {phase_dir.name}/")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Add requirements to: {client_dir}/00_INTAKE/")
    click.echo(f"  2. Run audit: ./ai_slop_agency/shared/kdaf_orchestrator.py run_audit --target '{name}'")
    click.echo()


def _create_client_template():
    """Create the CLIENT_TEMPLATE directory structure"""
    template_dir = CLIENTS / "CLIENT_TEMPLATE"
    template_dir.mkdir(parents=True, exist_ok=True)

    # Phase directories
    phases = {
        "00_INTAKE": "Initial requirements, client brief, scope definition",
        "01_AUDIT_DATA": "Raw tool outputs (security.json, complexity.json, ai_slop.json, god_object.json)",
        "02_REFACTORING": "Curated issue JSONs ready for kdaf-fix (after triage)",
        "03_DELIVERABLES": "Final reports, artifacts, documentation"
    }

    for phase, description in phases.items():
        phase_dir = template_dir / phase
        phase_dir.mkdir(exist_ok=True)

        readme = phase_dir / "README.md"
        readme.write_text(f"""# {phase}

**Purpose:** {description}

## Contents

This directory will contain files generated during the {phase} phase.

See main project README for workflow details.
""")

    # Main client README
    main_readme = template_dir / "README.md"
    main_readme.write_text("""# CLIENT_TEMPLATE

**Template for KDAF-compliant client projects**

## Directory Structure

```
CLIENT_TEMPLATE/
├── 00_INTAKE/          Initial requirements and scope
├── 01_AUDIT_DATA/      Raw analysis outputs
├── 02_REFACTORING/     Curated fixes after triage
└── 03_DELIVERABLES/    Final deliverables
```

## Workflow

### Phase 1: INTAKE (00_INTAKE/)
1. Gather client requirements
2. Define scope and objectives
3. Document technical context

### Phase 2: AUDIT (01_AUDIT_DATA/)
1. Run analysis: `kdaf_orchestrator.py run_audit --target "<client-name>"`
2. Outputs:
   - security.json
   - complexity.json
   - ai_slop.json
   - god_object.json

### Phase 3: REFACTORING (02_REFACTORING/)
1. Triage findings: `kdaf_orchestrator.py triage --input "01_AUDIT_DATA/security.json"`
2. Outputs:
   - security_critical.json
   - security_manual_review.json
   - security_auto_safe.json

### Phase 4: DELIVERABLES (03_DELIVERABLES/)
1. Apply fixes: `kdaf_orchestrator.py fix --input "02_REFACTORING/security_critical.json"`
2. Generate reports
3. Package artifacts

## Notes

- Each phase builds on the previous
- All outputs are preserved for audit trail
- Timestamps ensure chronological tracking
""")


# ============================================================================
# Workflow Commands (run_audit, triage, fix)
# ============================================================================

@cli.command('run-audit')
@click.option('--target', required=True, help='Target directory to analyze (e.g., "agency-toolkit")')
@click.option('--client', help='Client name (if using clients/ structure)')
def run_audit(target: str, client: Optional[str]):
    """
    Run audit (orchestrates run_real_audit.py):
    1. Call run_real_audit.py on target
    2. Copy outputs to client's 01_AUDIT_DATA/ (if --client specified)
    """
    click.echo("=" * 80)
    click.echo(f"KDAF ORCHESTRATOR - RUN AUDIT: {target}")
    click.echo("=" * 80)
    click.echo()

    # Run the audit script
    audit_script = ROOT_DIR / "run_real_audit.py"

    if not audit_script.exists():
        click.echo(f"❌ Error: run_real_audit.py not found at {audit_script}")
        sys.exit(1)

    click.echo(f"🔍 Running audit on: {target}")
    click.echo()

    # Execute run_real_audit.py
    result = subprocess.run(
        [sys.executable, str(audit_script)],
        cwd=ROOT_DIR
    )

    if result.returncode != 0:
        click.echo(f"❌ Audit failed with exit code {result.returncode}")
        sys.exit(1)

    # If client specified, copy outputs to client directory
    if client:
        click.echo()
        click.echo(f"📦 Copying outputs to clients/{client}/01_AUDIT_DATA/...")

        client_dir = CLIENTS / client / "01_AUDIT_DATA"
        if not client_dir.exists():
            click.echo(f"❌ Error: Client '{client}' not found. Run: onboard_client --name '{client}'")
            sys.exit(1)

        # Copy JSON files from examples/real_audit_output/ to client dir
        output_dir = ROOT_DIR / "examples" / "real_audit_output"
        if output_dir.exists():
            import shutil
            for json_file in output_dir.glob("*.json"):
                dest = client_dir / json_file.name
                shutil.copy(json_file, dest)
                click.echo(f"  ✓ {json_file.name}")

        click.echo()
        click.echo(f"✅ Outputs copied to: {client_dir}")

    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review outputs in: examples/real_audit_output/")
    if client:
        click.echo(f"  2. Run triage: ./ai_slop_agency/shared/kdaf_orchestrator.py triage --client '{client}' --input '01_AUDIT_DATA/security_*.json'")
    else:
        click.echo("  2. Run triage: ./ai_slop_agency/shared/kdaf_orchestrator.py triage --input 'examples/real_audit_output/security_*.json'")


@cli.command()
@click.option('--input', 'input_file', required=True, help='Input JSON file from audit')
@click.option('--client', help='Client name (if using clients/ structure)')
def triage(input_file: str, client: Optional[str]):
    """
    Triage findings (orchestrates triage_smart.py):
    1. Call triage_smart.py on input JSON
    2. Copy triaged outputs to client's 02_REFACTORING/ (if --client specified)
    """
    click.echo("=" * 80)
    click.echo(f"KDAF ORCHESTRATOR - TRIAGE: {input_file}")
    click.echo("=" * 80)
    click.echo()

    triage_script = ROOT_DIR / "triage_smart.py"

    if not triage_script.exists():
        click.echo(f"❌ Error: triage_smart.py not found at {triage_script}")
        sys.exit(1)

    # Resolve input file path
    input_path = Path(input_file)
    if not input_path.is_absolute():
        # Try relative to client dir first
        if client:
            client_input = CLIENTS / client / input_file
            if client_input.exists():
                input_path = client_input
            else:
                input_path = ROOT_DIR / input_file
        else:
            input_path = ROOT_DIR / input_file

    if not input_path.exists():
        click.echo(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)

    click.echo(f"🔍 Triaging: {input_path}")
    click.echo()

    # Execute triage_smart.py
    result = subprocess.run(
        [sys.executable, str(triage_script), str(input_path)],
        cwd=ROOT_DIR
    )

    if result.returncode != 0:
        click.echo(f"❌ Triage failed with exit code {result.returncode}")
        sys.exit(1)

    # If client specified, copy outputs to client directory
    if client:
        click.echo()
        click.echo(f"📦 Copying triaged outputs to clients/{client}/02_REFACTORING/...")

        client_dir = CLIENTS / client / "02_REFACTORING"
        if not client_dir.exists():
            click.echo(f"❌ Error: Client '{client}' not found")
            sys.exit(1)

        # Copy JSON files from examples/triage_output/ to client dir
        output_dir = ROOT_DIR / "examples" / "triage_output"
        if output_dir.exists():
            import shutil
            for json_file in output_dir.glob("*.json"):
                dest = client_dir / json_file.name
                shutil.copy(json_file, dest)
                click.echo(f"  ✓ {json_file.name}")

        click.echo()
        click.echo(f"✅ Outputs copied to: {client_dir}")

    click.echo()
    click.echo("Next steps:")
    if client:
        click.echo(f"  1. Review: clients/{client}/02_REFACTORING/")
        click.echo(f"  2. Apply fixes: ./ai_slop_agency/shared/kdaf_orchestrator.py fix --client '{client}' --input '02_REFACTORING/security_critical.json'")
    else:
        click.echo("  1. Review: examples/triage_output/")
        click.echo("  2. Apply fixes: ./ai_slop_agency/shared/kdaf_orchestrator.py fix --input 'examples/triage_output/security_critical.json'")


@cli.command()
@click.option('--input', 'input_file', required=True, help='Input JSON file from triage')
@click.option('--client', help='Client name (if using clients/ structure)')
def fix(input_file: str, client: Optional[str]):
    """
    Apply fixes (orchestrates kdaf-fix):
    1. Call kdaf-fix on triaged JSON
    2. Interactive fix application
    """
    click.echo("=" * 80)
    click.echo(f"KDAF ORCHESTRATOR - APPLY FIXES: {input_file}")
    click.echo("=" * 80)
    click.echo()

    fix_script = ROOT_DIR / "tools" / "kdaf-fix"

    if not fix_script.exists():
        click.echo(f"❌ Error: kdaf-fix not found at {fix_script}")
        sys.exit(1)

    # Resolve input file path
    input_path = Path(input_file)
    if not input_path.is_absolute():
        # Try relative to client dir first
        if client:
            client_input = CLIENTS / client / input_file
            if client_input.exists():
                input_path = client_input
            else:
                input_path = ROOT_DIR / input_file
        else:
            input_path = ROOT_DIR / input_file

    if not input_path.exists():
        click.echo(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)

    click.echo(f"🔧 Applying fixes from: {input_path}")
    click.echo()

    # Execute kdaf-fix (interactive)
    result = subprocess.run(
        [sys.executable, str(fix_script), str(input_path)],
        cwd=ROOT_DIR
    )

    if result.returncode != 0:
        click.echo(f"❌ Fix application failed with exit code {result.returncode}")
        sys.exit(1)

    click.echo()
    click.echo("✅ Fix session complete")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review changes: git diff")
    click.echo("  2. Run tests to verify fixes")
    click.echo("  3. Commit: git add . && git commit -m 'Apply KDAF fixes'")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    cli()
