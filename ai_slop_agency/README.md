# AI Slop Agency - KDAF System

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

**Last Updated:** 2025-11-11