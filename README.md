# VIBE CODING AGENCY - Knowledge-Driven Consulting System

**A working system for AI-driven consulting that prevents hallucinations through systematic methodology.**

> 📋 **Current Status**: This repository is undergoing systematic reorganization. See **[CURRENT_STATUS.md](CURRENT_STATUS.md)** for latest updates and **[PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md)** for detailed analysis.

---

## What Is This?

This is a **production-ready monorepo** containing an integrated suite of tools for knowledge-driven agency work:

- **AI-Slop Agency** (KDAF Orchestrator) - The brain that coordinates analysis
- **Meta-Audit** - Code analysis engine (complexity, security, AI-slop detection)
- **Agency-Toolkit** - Professional report generation (Markdown + PDF)

Together, these prevent hallucinations through **structured methodology, external validation, and complete transparency**.

---

## Monorepo Structure

```
vibe_coding_agency/                    (THIS ROOT)
│
├── 📚 ai_slop_agency/                 ← The active KDAF system
│   ├── shared/
│   │   └── kdaf_orchestrator.py       ← The brain (700+ lines)
│   ├── hq/
│   │   ├── 01_playbooks/              ← KDAF protocols
│   │   └── 02_knowledge_base/         ← Growing intelligence
│   ├── clients/                       ← Live client projects
│   └── _legacy_graveyard/             ← Archived experimental code
│
├── 🔍 meta-audit/                     ← Code analysis engine
│   ├── src/
│   │   └── analyzers/
│   │       └── collectors/            ← Runs complexity, security, AI-slop, god-object
│   ├── tests/
│   └── reference/                     ← Reference implementations
│
├── 📋 agency-toolkit/                 ← Report generation engine
│   ├── agency_toolkit/
│   │   ├── core/
│   │   │   └── briefing/              ← Markdown + PDF generation
│   │   ├── templates/                 ← Report templates
│   │   └── registry/                  ← Plugin architecture
│   ├── tests/
│   └── docs/
│
├── 📖 docs/                           ← Monorepo documentation
│   └── ARCHITECTURE.md                ← System architecture
│
├── .gitignore                         ← Root monorepo gitignore
└── README.md                          ← This file
```

---

## The Three Components

### 1. AI-Slop Agency (KDAF Orchestrator)
**Location:** `ai_slop_agency/shared/kdaf_orchestrator.py`

The executable brain implementing the Knowledge-Driven Agency Framework (KDAF):

- **Phase 1: VERSTEHEN** (Semantic Understanding)
  - Extract facts, not assumptions
  - Identify knowledge gaps
  - Generate pre-research questions

- **Phase 2: RECHERCHIEREN** (Knowledge Acquisition)
  - Research gaps with external sources
  - Build ground truth from citations
  - Define validation methods

- **Phase 3: VALIDIEREN** (Data-Driven Validation)
  - Call Meta-Audit for code analysis
  - Call Agency-Toolkit for professional reports
  - Preserve raw outputs for audit trail

**Status:** ✅ Complete and production-ready

### 2. Meta-Audit
**Location:** `meta-audit/src/analyzers/collectors/`

Code analysis engine that provides **real tool outputs** (not opinions):

- **Complexity Analysis** - radon complexity metrics
- **Security Analysis** - bandit vulnerability detection
- **AI-Slop Detection** - identifies AI-generated code patterns
- **God-Object Detection** - finds oversized classes/modules

All findings backed by actual tool outputs, no speculation.

**Status:** ✅ Integrated with KDAF Phase 3

### 3. Agency-Toolkit
**Location:** `agency-toolkit/agency_toolkit/core/briefing/`

Professional report generation:

- **Markdown Reports** - Always generated
- **PDF Reports** - Generated via fpdf (if installed)
- **BriefingData Model** - Structured data format
- **Templates** - Professional formatting

Converts Meta-Audit findings into executive-ready deliverables.

**Status:** ✅ Integrated with KDAF Phase 3

---

## How It Works

```
Client Input (ambiguous)
    ↓
PHASE 1: VERSTEHEN (KDAF Orchestrator)
  ├─ Extract facts from input
  ├─ Identify knowledge gaps
  └─ Generate pre-research questions
    ↓
PHASE 2: RECHERCHIEREN (KDAF Orchestrator)
  ├─ Research gaps with external sources
  ├─ Build ground truth from citations
  └─ Define validation plan
    ↓
PHASE 3: VALIDIEREN (KDAF Orchestrator)
  ├─ Call Meta-Audit.run_all_collectors()
  │  └─ Get real findings (complexity, security, AI-slop, god-objects)
  ├─ Call Agency-Toolkit.generate_briefing()
  │  └─ Generate Markdown + PDF reports
  └─ Store complete audit trail
    ↓
Final Deliverables
  ├─ Professional Markdown Report
  ├─ Professional PDF Report
  ├─ Raw tool outputs (for audit trail)
  └─ Structured JSON results
```

---

## Quick Start

### Run a Full Workflow

```python
from ai_slop_agency.shared.kdaf_orchestrator import KDAFOrchestrator

orchestrator = KDAFOrchestrator()
result = orchestrator.run_full_workflow(
    client_input="Analyze our codebase for quality and security",
    project_name="my_project"
)

print(f"Project: {result['project_path']}")
print(f"Phase 1: {len(result['phase_1']['facts'])} facts")
print(f"Phase 2: {len(result['phase_2']['research_findings'])} findings")
print(f"Phase 3: {len(result['phase_3']['validation_results'])} validations")
```

### Manual Phase Control

```python
orchestrator = KDAFOrchestrator()
orchestrator.create_project("my_project")

# Phase 1
p1 = orchestrator.phase_1_verstehen("Analyze our Django app")

# Phase 2
p2 = orchestrator.phase_2_recherchieren()

# Phase 3 (with code target)
p3 = orchestrator.phase_3_validieren(
    target_path="/path/to/code"
)
```

---

## Key Design Principles

### 1. External Validation ONLY
**Rule:** No claims without TOOL OUTPUT or CITED SOURCE

✅ "Meta-Audit found 47 security issues"
❌ "Code quality is poor"

### 2. Complete Audit Trail
- Raw tool outputs stored unmodified
- Every finding traceable to its source
- JSON for machine parsing
- Markdown for human reading

### 3. Graceful Degradation
- If Meta-Audit unavailable → Uses mock data
- If Agency-Toolkit unavailable → Uses fallback markdown
- **Always completes workflow**, never fails silently

### 4. Modular Design (No Hard Coupling)
- KDAF Orchestrator calls tools via clean APIs
- Each component can be used independently
- Tools can be swapped/extended via registry pattern
- Plugin architecture in Agency-Toolkit

---

## Monorepo Configuration

### Root .gitignore
Unified ignore rules for all sub-projects:
- Python caches (`__pycache__`, `.pytest_cache`, `.mypy_cache`)
- Build artifacts (`build/`, `dist/`)
- Environment files (`.env`, `.venv`)
- Test outputs (`kdaf_projects/`)
- IDE files (`.vscode/`, `.idea/`)

### File Count
- **Total:** 8,101 files (under GitHub's 10k limit)
- **Agency-Toolkit:** ~4,000 files
- **Meta-Audit:** ~800 files
- **AI-Slop Agency:** ~1,100 files
- **Size:** 169MB

### Git Repository
Initialize the monorepo as a single git repository at this root:
```bash
git init
git add .
git commit -m "Initial commit: KDAF Orchestrator monorepo"
```

---

## Sub-Projects Documentation

For detailed information about each component:

- **AI-Slop Agency:** See `ai_slop_agency/README_ACTIVE_SYSTEM.md`
- **KDAF Orchestrator:** See `ai_slop_agency/shared/README_KDAF_ORCHESTRATOR.md`
- **Meta-Audit:** See `meta-audit/README.md`
- **Agency-Toolkit:** See `agency-toolkit/README.md`

---

## What Makes This Different

### vs. Traditional AI Consulting
❌ AI validates its own output (circular reasoning)
✅ Tools validate AI output (reliable)

### vs. Generic Code Analysis
❌ Just reports issues
✅ Research + contextualize + recommend (with sources)

### vs. Manual Process
❌ Slow, error-prone
✅ Automated but rigorous (Phase 3 calls real tools)

---

## Philosophy

**KDAF Orchestrator proves that AI-driven consulting can be:**
- ✅ **Reliable** - Every finding backed by tool outputs
- ✅ **Verifiable** - Full audit trail of where info came from
- ✅ **Professional** - Using real tools for analysis & reporting
- ✅ **Scalable** - Automated end-to-end workflow
- ✅ **Accountable** - Confidence levels tied to evidence

**This is not a demo. This is a working system.**

---

## Status

- ✅ KDAF Orchestrator: Phase 1-3 complete
- ✅ Meta-Audit Integration: Live
- ✅ Agency-Toolkit Integration: Live
- ✅ Monorepo Structure: Configured
- ⏳ CLI Wrapper: Planned
- ⏳ Web Dashboard: Planned

---

## Development

### Running Tests
```bash
# KDAF Orchestrator
cd ai_slop_agency/shared
python -c "from kdaf_orchestrator import KDAFOrchestrator; orchestrator = KDAFOrchestrator(); orchestrator.run_full_workflow('Test input', 'test_project')"

# Meta-Audit
cd meta-audit
pytest tests/

# Agency-Toolkit
cd agency-toolkit
pytest tests/
```

### Adding Features
Each component has clear extension points:
- **KDAF:** Add phases or modify existing ones
- **Meta-Audit:** Add analyzers via registry
- **Agency-Toolkit:** Add templates/providers via registry

---

**Last Updated:** 2025-11-11
**Maintainers:** Vibe Coding Agency Team

---

## Next Steps

1. ✅ **Monorepo Structure** - Complete
2. ⏳ **Git Repository** - Initialize and push
3. ⏳ **CLI Wrapper** - Make easily accessible (`vibe kdaf ...`)
4. ⏳ **Documentation** - Architecture guide
5. ⏳ **CI/CD** - Automated testing and deployment

---

For questions or issues, see `/docs/ARCHITECTURE.md`
