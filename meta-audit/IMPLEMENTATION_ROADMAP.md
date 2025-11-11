# Capsule Audit - Complete Implementation Roadmap

**Last Updated:** 2025-11-10

**Purpose:** Single source of truth for the complete journey from prototype (v0.2.0) to production-ready tool (v1.0+)

---

## The Big Picture: 3 Phases

```
┌─────────────────────────────────────────────────────────────┐
│ MVP (Sprint 1-3, ~3 weeks)                                  │
├─────────────────────────────────────────────────────────────┤
│ Säule A: Real Data Collection (Phase 1)                     │
│ ├─ Radon (Complexity)                                       │
│ ├─ Bandit (Security)                                        │
│ └─ AI-Slop (Pattern Matching)                               │
│                                                              │
│ Säule B: Structured Reporting (Phase 2-3)                   │
│ ├─ AnalysisResult Model                                     │
│ ├─ Report Generator (CSV, JSON, YAML)                       │
│ └─ CLI Integration                                          │
│                                                              │
│ Säule C: Capsule System (Multi-Project)                    │
│ ├─ ProjectCapsule Model                                     │
│ ├─ Config System                                            │
│ └─ Batch Analysis                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Core Hardening (2 weeks)                           │
├─────────────────────────────────────────────────────────────┤
│ ✓ Token Transparency & Cost Tracking                        │
│ ✓ Provider Flexibility (Google, Mistral, Ollama)            │
│ ✓ SLO Definition & Performance Benchmarks                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Framework Vision (3+ weeks)                        │
├─────────────────────────────────────────────────────────────┤
│ ✓ Project Steward (Multi-Agent Orchestration)               │
│ ✓ Specialist Persona Library (QA, Security, Refactor)       │
│ ✓ Multi-Agent QA-Refactor Loop                              │
│ ✓ Recursive Criticism & Improvement (RCI)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Document Structure

This repo now has 4 key planning documents:

| Document | Purpose | Audience | Status |
|----------|---------|----------|--------|
| **MVP_BLUEPRINT.md** | Strategic plan for MVP (3 Säulen) | Both | ✓ DONE |
| **POST_MVP_ROADMAP.md** | Detailed plan for Phase 4 & 5 | Both | ✓ DONE |
| **SPRINT_1_TASKS.md** | Concrete code tasks for Sprint 1 | Developer | ✓ DONE |
| **This file** | Overall navigation + status | Both | ✓ CURRENT |

---

## Sprint 1: Data Collection Layer (Säule A)

**Duration:** 1-2 weeks (3-5 working days)

**Goal:** Phase 1 with real analyzers (Radon, Bandit, AI-Slop)

**Current:** Collectors are stubs returning mock data

**Deliverable:** Collectors return real AnalysisResult-like dictionaries

### Tasks

1. **Task 1.1:** Update `pyproject.toml` with `radon`, `bandit` dependencies
2. **Task 1.2:** Implement Complexity Analyzer (use radon library)
3. **Task 1.3:** Implement Security Analyzer (use bandit library)
4. **Task 1.4:** Implement AI-Slop Analyzer (pattern matching)
5. **Task 1.5:** Create Collector Registry + Parallel Executor
6. **Task 1.6:** Update CLI to use new collectors
7. **Task 1.7:** Unit Tests for each collector
8. **Task 1.8:** Integration Test for complete Phase 1

**Success:** `meta-audit analyze --path /project` returns real data (not mock)

**Location:** `SPRINT_1_TASKS.md` (detailed code instructions)

---

## Sprint 2: Structured Reporting (Säule B)

**Duration:** 1 week (estimated after Sprint 1)

**Goal:** Convert raw collector data into structured AnalysisResults and Reports

**Deliverable:** Reports in CSV, JSON, YAML, Terminal format

### Tasks

1. Properly use AnalysisResult Pydantic Model
2. Create Report Generator (aggregation logic)
3. Implement report exports (CSV, JSON, YAML, Rich Table)
4. Integrate `--format`, `--output-file` CLI flags
5. Optional: `--advise` flag for LLM synthesis (Phase 2)
6. Unit + Integration tests

**Success:** `meta-audit analyze --path /project --format json --output-file report.json` works

**Location:** `MVP_BLUEPRINT.md` → "Säule B: Analysis & Reporting"

---

## Sprint 3: Capsule System & Config (Säule C)

**Duration:** 1 week (estimated after Sprint 2)

**Goal:** Multi-project support via configuration

**Deliverable:** Define multiple projects in config, analyze all in batch

### Tasks

1. Fill ProjectCapsule model correctly
2. Activate phoenix_config system
3. Implement `capsule create` command
4. Implement `analyze --config myconfig.yaml` for batch processing
5. Support for multiple project definitions
6. Cross-project summary report
7. Unit + Integration tests

**Success:** `meta-audit analyze --config projects.yaml` processes 3+ projects

**Location:** `MVP_BLUEPRINT.md` → "Säule C: Capsule System"

---

## After MVP: Phase 4 & 5

Once MVP is stable:

### Phase 4: Core Hardening (2 weeks)
- Token transparency & cost tracking
- Provider flexibility (prove Mistral works same as Google)
- SLO definition & performance benchmarks

**Location:** `POST_MVP_ROADMAP.md` → "Phase 4"

### Phase 5: Framework Vision (3+ weeks)
- Project Steward (multi-agent orchestration)
- Specialist personas (QA, Security, Refactor)
- QA-Refactor loop
- Recursive Criticism & Improvement

**Location:** `POST_MVP_ROADMAP.md` → "Phase 5"

---

## Guard Rails (Throughout All Phases)

### 1. Token-Efficiency (Prevent Explosion)
- Phase 1: 0 tokens (all static analysis)
- Phase 2: Optional `--advise` flag (only for HIGH/CRITICAL)
- Phase 4: Token tracking + cost estimates

### 2. Provider Flexibility
- No provider-specific code outside `providers/`
- Config-driven provider selection (Google, Mistral, Ollama)
- Phase 4: Integration test proving provider interchangeability

### 3. Regression Control
- Modular components (each independently testable)
- Pydantic models enforce data contracts
- Comprehensive test suite (unit + integration + performance)

### 4. Skalierbarkeit
- Collectors run in parallel (ThreadPoolExecutor)
- SLO: 1000 files < 60 seconds (Phase 1)
- Graceful degradation if one collector fails

---

## How to Use This Roadmap

### For Planning/Discussion
→ Read `MVP_BLUEPRINT.md` (3 Säulen overview)

### For Understanding Post-MVP Vision
→ Read `POST_MVP_ROADMAP.md` (Phase 4 & 5 details)

### For Coding (Developer)
→ Read `SPRINT_1_TASKS.md` (concrete code instructions)

### For Overall Status
→ Read this file (navigation + current progress)

---

## Current Project Status (Nach Sprint 2 ✅)

| Component | v0.2.0 Status | v0.3.0-beta (Sprint 1 DONE) | v0.3.0 (After S2 ✅) | v0.3.1 (S3 Target) | v1.0 Target |
|-----------|---|---|---|---|---|
| Collectors (Phase 1) | ❌ Stub | ✅ REAL - radon, bandit, ai-slop | ✅ List[AnalysisResult] models | ✅ Works with capsules | ✅ Optimized (P4) |
| Reporting (Phase 2-3) | ❌ LLM text | ❌ TODO | ✅ JSON + Terminal (DONE) | ✅ Corpus reports (S3) | ✅ Multi-format (P4) |
| Capsule System | ❌ Models only | ❌ TODO | ⚠️ Models ready | ✅ Full (S3) | ✅ Batch processing |
| Batch Processing | ❌ None | ❌ None | ❌ None | ✅ Parallel (S3) | ✅ Distributed (P4) |
| Multi-Agent | ❌ None | ❌ None | ❌ None | ❌ None | ✅ Full orchestration (P5) |
| Tests | ❌ None | ✅ 30/30 PASS | ✅ 43/43 PASS (S2) | ✅ 68/68 target (S3) | ✅ 90+ Comprehensive |
| Provider Flexibility | ✅ Architected | ✅ Architected | ✅ Ready (S2) | ✅ Ready | ✅ Proven (P4) |
| Token Tracking | ❌ None | ❌ None | ❌ None | ❌ None | ✅ Complete (P4) |
| CLI Phase 1 | ❌ Broken | ✅ WORKING | ✅ + Reports (DONE) | ✅ + Capsule cmds (S3) | ✅ Full featured |

---

## Sprint 2 Results: Option A Successfully Implemented ✅

**Decision Made:** Collectors return AnalysisResult Pydantic-Modelle.

**Achievements:**
- ✅ All 3 collectors refactored to return `List[AnalysisResult]`
- ✅ Report class with JSON + Terminal/Rich export
- ✅ CLI integrated with --format and --output-file flags
- ✅ 43/43 unit + integration tests passing
- ✅ Strict data contracts prevent "Wildwuchs"

**Report Formats Delivered:**
1. ✅ **JSON** - Structured, machine-readable, source of truth
2. ✅ **Terminal/Rich Table** - User-friendly CLI output with colors
3. ⏳ **YAML** (Sprint 3)
4. ⏳ **CSV** (Sprint 3)

---

## Sprint 3 Goal: Multi-Project Management (Säule C)

**Focus:** From single-project analysis to batch processing via ProjectCapsule system.

**Key Tasks:**
1. Implement `capsule create` command for project snapshots
2. Update `analyze` command for corpus mode
3. Create CorpusAnalysisReport for aggregating multi-project findings
4. Prepare cross-project pattern detection framework

**Expected Outcomes:**
- ✅ Batch analysis of multiple projects
- ✅ Corpus-level reporting with per-project breakdowns
- ✅ Framework ready for Phase 4/5 multi-agent analysis
- ✅ 68/68+ tests passing

**Location:** `SPRINT_3_TASKS.md` (detailed implementation plan)

---

## Key Decisions

### 1. MVP = 3 Säulen (not 5-phase waterfall)
- More agile
- Parallel work possible
- Delivers value faster

### 2. Sprint 1 = Collectors first (not Agent hardening)
- Agent needs real data to be useful
- Collectors are independent
- Low risk of breaking existing code

### 3. Phase 4 before Phase 5
- Harden existing features first
- Prove token efficiency & provider flexibility
- Reduce risk for multi-agent features

### 4. Guard Rails built-in from Day 1
- Not an afterthought
- Token control prevents cost surprises
- Modular design prevents "Wildwuchs"

---

## Next Steps

### Immediate (Sprint 3 Ready to Code)
1. ✅ Sprint 1 complete (Collectors with real libraries)
2. ✅ Sprint 2 complete (Structured reporting with Option A)
3. **→ START SPRINT 3 (Capsule system & batch processing)**

**To Start Sprint 3:**
- Read `SPRINT_3_TASKS.md` for detailed implementation plan
- Review ProjectCapsule model in `src/meta_audit/core/models.py`
- Task 3.1: Implement `capsule create` command

### After Sprint 3 Complete
1. MVP is fully functional ✅
2. All 3 Säulen implemented (A: Data Collection, B: Reporting, C: Capsule System)
3. Decide: Phase 4 (hardening) or Phase 5 (vision)?
4. Start Phase 4 (Token Tracking, Provider Flexibility)

### After MVP is Stable
1. Phase 4: Core Hardening (2 weeks)
   - Token transparency & cost tracking
   - Provider flexibility proof-of-concept
   - SLO definition & performance benchmarks
2. Phase 5: Framework Vision (3+ weeks)
   - Multi-Agent orchestration
   - Cross-project analysis
   - Recursive Criticism & Improvement (RCI)

---

## Quick Reference: File Paths

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| MVP Blueprint | `MVP_BLUEPRINT.md` | 3 Säulen plan | ✅ Reference |
| Post-MVP Roadmap | `POST_MVP_ROADMAP.md` | Phase 4 & 5 details | ✅ Ready |
| Sprint 1 Tasks | `SPRINT_1_TASKS.md` | Data Collection (Phase 1) | ✅ COMPLETE |
| Sprint 2 Tasks | `SPRINT_2_TASKS.md` | Structured Reporting (Phase 2-3) | ✅ COMPLETE |
| Sprint 3 Tasks | `SPRINT_3_TASKS.md` | Capsule System & Batch (Phase 3) | 📋 READY |
| This Roadmap | `IMPLEMENTATION_ROADMAP.md` | Overall navigation | 📋 Current |
| Original blueprint | `refined_blueprint.json` | Archive (v2) | 📦 Archive |
| Reference docs | `reference/README.md` | Architecture patterns | 📚 Reference |

---

## Questions?

- **"What's the difference between Säule A, B, C?"** → See `MVP_BLUEPRINT.md`
- **"What was Sprint 2 about?"** → See `SPRINT_2_TASKS.md` - Structured Reporting with Pydantic models
- **"What's next after Sprint 2?"** → See `SPRINT_3_TASKS.md` - Capsule System & Batch Processing
- **"How will we handle token costs?"** → See `POST_MVP_ROADMAP.md` Phase 4.1
- **"What should I code for Sprint 3?"** → See `SPRINT_3_TASKS.md` Task 3.1+ (capsule create)
- **"How do we prevent wildwuchs?"** → See Guard Rails section and Option A decision above

---

## Version History

| Version | Date | What Changed |
|---------|------|---|
| 1.0 | 2025-11-10 | Initial roadmap (Sprint 1-2 plans) |
| 1.1 | 2025-11-10 | Updated after Sprint 2 completion; added Sprint 3 plan |
| 1.2 | 2025-11-10 | Updated status table; Sprint 3 ready to start |

