# 📦 Legacy Graveyard - Historical Archive

**Purpose**: Archive of experimental, prototype, and obsolete code

**Status**: NOT PART OF THE ACTIVE SYSTEM

---

## Structure

### `/archive/` - Obsolete & Experimental Systems
- **01_agency_empty** - Empty agency directory (no content)
- **02_agency_system_complete** - Notebook-based orchestration prototype (replaced by KDAF Orchestrator)
- **03_agency_cli** - Early CLI implementation (superseded)
- **04_simple_motor** - Simple motor prototype (experimental)
- **05_vibe_coding_agency_empty** - Empty vibe coding agency directory
- **06_agency_knowledge_base** - Early knowledge base (merged into hq/)
- **07_client_projects_old** - Old client project structure (see ../clients/ for active projects)
- **08_reference_implementations** - Reference code examples
- **09_kdaf_test_projects** - Test outputs from KDAF Orchestrator testing

### `/prototypes/` - Prototype Implementations
- **01_working_prototypes** - Various working prototypes from development

### `/experiments/` - Experimental Code
- **01_experiments** - Experimental implementations and tests

---

## Why This Exists

During the development of Vibe Coding Agency, multiple approaches were tried:
1. Notebook-based orchestration (agency-system-complete)
2. Simple motor pattern (simple_motor)
3. Various CLI implementations (agency_cli)
4. Multiple knowledge base approaches

These have been **superseded by the KDAF Orchestrator** (`../shared/kdaf_orchestrator.py`), which combines the best parts of each approach into a single, unified system.

---

## The Active System

The **current, production-ready system** consists of:

```
vibe_coding_agency/ai_slop_agency/
├── clients/           ← Live client projects
├── hq/               ← Knowledge base + playbooks (KDAF protocols)
├── shared/           ← KDAF Orchestrator (the brain)
└── _legacy_graveyard/ ← This directory
```

---

## If You Need Legacy Code

This directory is preserved for **historical reference only**. Do NOT use code from here in production.

If you need:
- **Code analysis**: Use `meta-audit/` (active system)
- **Report generation**: Use `agency-toolkit/` (active system)
- **Project orchestration**: Use `shared/kdaf_orchestrator.py` (active system)
- **Knowledge/protocols**: Use `hq/` (active system)

---

## Migration Notes

The KDAF Orchestrator (`shared/kdaf_orchestrator.py`) replaces all functionality from this archive:

| Legacy | Replaced By | Status |
|--------|-------------|--------|
| agency-system-complete (notebooks) | kdaf_orchestrator.py | ✅ Complete replacement |
| agency_cli (old CLI) | kdaf_orchestrator Python API | ✅ Superseded |
| agency_knowledge_base | hq/ directory | ✅ Merged |
| simple_motor | kdaf_orchestrator | ✅ Integrated |

---

**Archived**: 2025-11-11
**Reason**: Cleanup and consolidation to active system
**References**: See `../shared/README_KDAF_ORCHESTRATOR.md`
