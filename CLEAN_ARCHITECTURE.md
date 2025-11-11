# Vibe Coding Agency - Clean Architecture

**Date:** 2025-11-11  
**Status:** Cleaned and organized after systematic analysis

---

## Overview

This is a **monorepo** containing three integrated packages that work together to implement the Knowledge-Driven Agency Framework (KDAF).

---

## Repository Structure

```
vibe_coding_agency/                    (ROOT)
│
├── 📦 PACKAGES (The three main components)
│   ├── meta-audit/                    Code analysis engine
│   │   ├── src/meta_audit/           Python package
│   │   ├── tests/                    Test suite
│   │   └── pyproject.toml            Package configuration
│   │
│   ├── agency-toolkit/               Report generation
│   │   ├── agency_toolkit/           Python package
│   │   ├── tests/                    Test suite
│   │   ├── templates/                Report templates
│   │   └── pyproject.toml            Package configuration
│   │
│   └── ai_slop_agency/               KDAF orchestrator
│       ├── shared/                   Core orchestration
│       │   ├── kdaf_orchestrator.py  Main workflow engine
│       │   ├── cli/                  CLI tools
│       │   ├── api/                  API interface
│       │   └── orchestration/        Workflow management
│       ├── hq/                       Agency knowledge base
│       │   ├── 00_company/           Principles & manifesto
│       │   ├── 01_playbooks/         Process guides (Phase 1-3)
│       │   └── 02_knowledge_base/    Growing intelligence
│       ├── clients/                  Client projects
│       │   └── CLIENT_TEMPLATE/      Template structure
│       └── _legacy_graveyard/        Archived experiments
│
├── 🆕 explore_agent/                 Autonomous exploration (new)
│   ├── src/explore_agent/           Python package
│   ├── setup.py                     Package setup
│   └── README.md                    Documentation
│
├── 🛠️ TOOLS (Root-level automation)
│   ├── run_real_audit.py            Main audit script
│   ├── triage_smart.py              Triage findings
│   └── triage_analysis.py           Analysis tool
│
├── 📚 DOCUMENTATION
│   ├── README.md                    Main documentation
│   ├── CURRENT_STATUS.md            Current state tracker
│   ├── PROJECT_ANALYSIS.md          Comprehensive analysis
│   ├── META_AUDIT_COMPARISON.md     Duplication analysis
│   ├── docs/
│   │   ├── ARCHITECTURE.md          System architecture
│   │   └── archive/                 Historical reports
│   └── examples/                    Example outputs
│
└── 🔧 CONFIGURATION
    └── .gitignore                   Monorepo ignore rules
```

---

## Component Details

### 1. Meta-Audit (Code Analysis Engine)

**Location:** `/meta-audit/`  
**Purpose:** Real tool-based code analysis (no AI opinions)

**Features:**
- Complexity analysis (radon)
- Security scanning (bandit)
- AI-slop pattern detection
- God-object detection
- Professional report generation

**Key Files:**
```
meta-audit/
├── src/meta_audit/
│   ├── analyzers/
│   │   └── collectors/      # Complexity, security, AI-slop
│   ├── generators/          # Report generation
│   ├── core/models.py       # Data models (Pydantic v2)
│   └── cli/main.py          # CLI entry point
├── tests/                   # Comprehensive test suite
└── pyproject.toml          # Dependencies: pydantic>=2.5, radon, bandit
```

**Usage:**
```bash
cd meta-audit
pip install -e ".[dev]"
python -m meta_audit analyze --path /path/to/code
```

**Status:** ✅ Clean, uses modern Pydantic v2

---

### 2. Agency-Toolkit (Report Generation)

**Location:** `/agency-toolkit/`  
**Purpose:** Professional deliverable generation

**Features:**
- Markdown report generation
- PDF report generation (fpdf2)
- BriefingData models
- Professional templates
- Provider system (Google, Mistral, etc.)

**Key Files:**
```
agency-toolkit/
├── agency_toolkit/
│   ├── core/briefing/      # Report generation engine
│   ├── templates/          # Markdown/PDF templates
│   ├── providers/          # LLM providers
│   └── cli_app.py          # CLI entry point
├── tests/                  # Unit, integration, UAT tests
└── pyproject.toml         # Dependencies: pydantic>=2.0, fpdf2
```

**Usage:**
```bash
cd agency-toolkit
pip install -e ".[dev]"
toolkit generate-briefing --data results.json
```

**Status:** ✅ Clean, comprehensive test suite

---

### 3. AI-Slop Agency (KDAF Orchestrator)

**Location:** `/ai_slop_agency/`  
**Purpose:** Workflow orchestration and project management

**Features:**
- 3-Phase KDAF workflow (Verstehen → Recherchieren → Validieren)
- Project structure templates
- State management
- Integration with meta-audit and agency-toolkit

**Key Files:**
```
ai_slop_agency/
├── shared/
│   ├── kdaf_orchestrator.py   # 700+ line main orchestrator
│   ├── cli/vibe.py            # CLI commands
│   └── orchestration/         # Workflow engine
├── hq/
│   ├── 01_playbooks/          # Phase 1, 2, 3 protocols
│   └── 02_knowledge_base/     # Cumulative intelligence
└── clients/                   # Active client projects
```

**Usage:**
```python
from ai_slop_agency.shared.kdaf_orchestrator import KDAFOrchestrator

orchestrator = KDAFOrchestrator()
result = orchestrator.run_full_workflow(
    client_input="Analyze codebase for quality",
    project_name="my_project"
)
```

**Status:** ✅ Clean, well-documented

---

### 4. Explore Agent (NEW)

**Location:** `/explore_agent/`  
**Purpose:** Autonomous codebase exploration

**Features:**
- Plan-Execute-Synthesize loop
- LLM-driven planning
- Temporary RAG store
- Safety constraints

**Status:** 🆕 Recently added, integration TBD

---

## How Components Work Together

### Workflow Integration

```
User Request
     ↓
ai_slop_agency/kdaf_orchestrator.py
     ├─ Phase 1: Understand (semantic analysis)
     ├─ Phase 2: Research (external sources)
     └─ Phase 3: Validate
          ├─ Calls: meta-audit (analyze code)
          └─ Calls: agency-toolkit (generate report)
     ↓
Deliverables (Markdown + PDF)
```

### Dependency Graph

```
ai_slop_agency
    ↓ uses
meta-audit (for Phase 3 validation)
    ↓ uses
agency-toolkit (for professional reports)
```

---

## Package Dependencies

### Meta-Audit Dependencies
```toml
pydantic>=2.5      # Data models (modern v2)
radon>=6.0.1       # Complexity analysis
bandit>=1.7.5      # Security scanning
click>=8.0         # CLI framework
rich>=13.0         # Rich terminal output
```

### Agency-Toolkit Dependencies
```toml
pydantic>=2.0.0    # Data models
fpdf2>=2.7.0       # PDF generation
typer[all]>=0.9.0  # CLI framework
pillow>=10.0.0     # Image handling
```

### Integration
Both packages use **Pydantic v2** - fully compatible!

---

## Development Setup

### Install All Packages (Development Mode)

```bash
# Meta-Audit
cd meta-audit
pip install -e ".[dev]"
pytest

# Agency-Toolkit
cd ../agency-toolkit
pip install -e ".[dev]"
pytest

# AI-Slop Agency (orchestrator only, no separate package)
cd ../ai_slop_agency
# No installation needed - uses other packages
```

### Run Full Workflow

```bash
# From root directory
python run_real_audit.py

# Or use KDAF orchestrator directly
python ai_slop_agency/shared/kdaf_orchestrator.py setup_agency
```

---

## Testing

### Meta-Audit Tests
```bash
cd meta-audit
pytest tests/unit/              # Fast unit tests
pytest tests/integration/       # Integration tests
pytest tests/production/        # Production workflow
```

### Agency-Toolkit Tests
```bash
cd agency-toolkit
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/smoke/             # Smoke tests
pytest tests/regression/        # Regression tests
pytest tests/uat/               # User acceptance tests
```

---

## Recent Cleanup (2025-11-11)

### What Was Removed

1. **Duplicate Code (2.2 MB saved)**
   - Removed `/ai_slop_agency/shared/tools_capsule_audit/` (entire package)
   - Was complete duplicate of `/meta-audit/` but with older Pydantic v1

2. **Documentation Sprawl**
   - Moved 9 historical status reports to `docs/archive/`
   - Created clear current documentation structure

3. **Total Files Removed:** 331 files
   - Python files: ~80 (duplicates)
   - Documentation: ~250 (mostly reference docs)

### What Was Kept

- `/meta-audit/` at root (canonical version)
- All unique functionality
- All tests
- All client projects
- All knowledge base

---

## Best Practices

### Adding New Features

1. **Choose the Right Package:**
   - Code analysis features → `meta-audit/`
   - Report generation → `agency-toolkit/`
   - Workflow/orchestration → `ai_slop_agency/`

2. **Follow Package Structure:**
   - Each package is self-contained
   - Inter-package imports via installed packages
   - No circular dependencies

3. **Testing:**
   - Add tests in package's test directory
   - Follow existing test patterns
   - Run tests before committing

### Making Changes

1. **Read Current Docs First:**
   - `CURRENT_STATUS.md` - What's happening now
   - `PROJECT_ANALYSIS.md` - Known issues
   - Package READMEs - Component details

2. **Avoid Creating Duplicates:**
   - Check if functionality exists elsewhere
   - Reuse existing code
   - Update existing instead of copying

3. **Document Changes:**
   - Update `CURRENT_STATUS.md`
   - Update package READMEs if needed
   - Add to changelog

---

## File Counts (After Cleanup)

```
Total Files:        ~680 (down from 1,014)
Python Files:       ~420 (down from 499)
Size:              ~14 MB (down from 16.2 MB)

Package Breakdown:
  meta-audit:       2.4 MB  (~80 Python files)
  agency-toolkit:   5.4 MB  (~250 Python files)
  ai_slop_agency:   6.1 MB  (~80 Python files, down from 8.3 MB)
  explore_agent:    116 KB  (~10 Python files)
```

---

## Key Design Principles

### 1. No Duplication
- Single source of truth for each component
- Reuse, don't recreate
- Keep canonical versions at obvious locations

### 2. External Validation Only
- No AI opinions without tool backing
- Every claim has source or tool output
- Raw outputs stored unmodified

### 3. Modular Design
- Each package can work independently
- Clear APIs between components
- Plugin architecture where appropriate

### 4. Professional Quality
- Real tools (radon, bandit, not opinions)
- Professional report templates
- Comprehensive test coverage

---

## Migration Notes

### From Old Structure (Pre-Cleanup)

**Old:** Code imported from `tools_capsule_audit`  
**New:** Import from `meta-audit`

```python
# OLD (broken now)
sys.path.insert(0, "ai_slop_agency/shared/tools_capsule_audit/src")
from meta_audit.analyzers.collectors import run_all_collectors

# NEW (correct)
sys.path.insert(0, "meta-audit/src")
from meta_audit.analyzers.collectors import run_all_collectors

# BEST (if installed as package)
from meta_audit.analyzers.collectors import run_all_collectors
```

---

## Future Improvements

### Planned
- [ ] Unified CLI (`vibe` command for all tools)
- [ ] Proper monorepo tooling (poetry/pants)
- [ ] CI/CD pipeline
- [ ] Integration tests across packages
- [ ] Explore agent integration with KDAF

### Possible
- [ ] Web dashboard
- [ ] Real-time collaboration
- [ ] Plugin marketplace
- [ ] Cloud deployment

---

## Questions?

- **Architecture:** See this file or `PROJECT_ANALYSIS.md`
- **Current Status:** See `CURRENT_STATUS.md`
- **Package Details:** See README in each package directory
- **History:** See `docs/archive/`

---

**Last Updated:** 2025-11-11  
**Maintainer:** Vibe Coding Agency Team  
**Status:** ✅ Clean, organized, ready for development
