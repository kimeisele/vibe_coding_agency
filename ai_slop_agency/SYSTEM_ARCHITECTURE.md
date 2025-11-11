# 🏢 Vibe Coding Agency - System Architecture

**The Complete Picture: Rosinen from All Approaches Combined**

---

## Executive Summary

Du hast 3 verschiedene Systeme gelesen, gemerkt dass sie alle **dasselbe Problem lösen** (aber unterschiedlich), und jetzt hast du **ein einziges, kohärentes System**.

**Das System:**
- **Motor**: `agency-system-complete` (Flask API, Notebook Orchestrator)
- **Philosophie**: `agency_knowledge_base` (Understand → Research → Validate)
- **Bauplan**: `vibe_coding_agency/Masterframework` (6 Phasen für Agentur-Workflow)
- **Schale**: `vibe_coding_agency/agency.py` (CLI zum Orchestrieren)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  EXTERNAL AGENT (Claude Code, GitHub Actions, etc.)        │
└────────────────────┬────────────────────────────────────────┘
                     │ (API Call oder CLI)
┌────────────────────▼────────────────────────────────────────┐
│  VIBE CODING AGENCY                                         │
│                                                             │
│  1. CLI / API (agency.py or Flask REST)                    │
│     ├─ Projekt klassifizieren (NEW or EXISTING)           │
│     ├─ Phase sequenzen laden                              │
│     └─ User durch Workflow führen                         │
│                                                             │
│  2. Notebook Orchestrator (agency-system-complete)          │
│     ├─ Wählt richtiges Notebook-Template                 │
│     ├─ Injiziert Parameter (papermill)                   │
│     └─ Speichert Outputs im Projekt-Ordner              │
│                                                             │
│  3. Notebook Templates (analysis_workflow.ipynb)            │
│     ├─ PHASE 1: Semantic Understanding                    │
│     ├─ PHASE 2: Knowledge Acquisition                     │
│     ├─ PHASE 3: Data-Driven Validation                    │
│     └─ PHASE 4: Report Generation                         │
│                                                             │
│     (All based on agency_knowledge_base protocols)          │
│                                                             │
│  4. Output: JSON + Markdown Reports                        │
│     ├─ project/{name}/state.json (Progress)              │
│     ├─ project/{name}/report.md (Final)                  │
│     └─ project/{name}/executed.ipynb (Audit Trail)       │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │ (Returns validated results)
┌────────────────────▼────────────────────────────────────────┐
│  EXTERNAL AGENT (Now has facts, not hallucinations)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **The Motor** (`agency-system-complete`)

**Location**: `/Users/ss/projects/ai_slop_agency/agency-system-complete/`

**What it does**:
- Runs Jupyter Notebooks as workflow templates (via `papermill`)
- Injects parameters (project_name, client_request, code_path, etc.)
- Saves executed notebooks + outputs in `projects/` folder
- Optional: Serves as Flask REST API for remote agents

**Key Files**:
- `agency-system/orchestrator/core.py` - NotebookOrchestrator class
- `agency-system/api/rest.py` - REST API endpoints
- `agency-system/cli/main.py` - CLI interface
- `agency-system/notebooks/` - Notebook templates

**Why this approach?**
- Notebooks are "executable specifications" (code + documentation together)
- Easy to modify workflows without touching Python code
- Papermill injects parameters cleanly (no string manipulation)
- Output is both human-readable (Jupyter) and machine-readable (JSON)

---

### 2. **The Philosophy** (`agency_knowledge_base`)

**Location**: `/Users/ss/projects/ai_slop_agency/agency_knowledge_base/`

**What it defines**:
- **Core Protocol** (`00_THE_CORE_PROTOCOL.md`) - "No bullshit" principle
- **Semantic Understanding** (`01_semantic_understanding_protocol.md`) - Extract facts from requests
- **Knowledge Acquisition** (`02_knowledge_acquisition_protocol.md`) - Research externally, cite sources
- **Data-Driven Validation** (`03_data_driven_validation_protocol.md`) - Use real tools, not speculation
- **Templates** (`research_backed_document_template.md`) - How reports should look

**Why this?**
- Prevents hallucinations (every claim must be backed by data or sources)
- Creates accountability (audit trail of where info came from)
- Scales to teams (clear methodology = clear expectations)

**How it's integrated**:
- Every notebook phase follows these protocols
- Phase 1 (Understand) implements semantic_understanding_protocol
- Phase 2 (Research) implements knowledge_acquisition_protocol
- Phase 3 (Validate) implements data_driven_validation_protocol
- Phase 4 (Report) uses research_backed_document_template

---

### 3. **The Masterplan** (`vibe_coding_agency/Masterframework`)

**Location**: `/Users/ss/projects/ai_slop_agency/vibe_coding_agency/Masterframework/`

**What it defines**:
- **01.md** - Master framework overview (6 phases for ANY project)
- **02.md** - NEW PROJECT INTAKE template
- **03.md** - EXISTING PROJECT RECOVERY template
- **04.md** - ARCHITECTURE DESIGN template
- **05.md** - IMPLEMENTATION PLAN template
- **06.md** - CODE GENERATION template
- **07.md** - QUALITY ASSURANCE template
- **08.md** - Quick start guide

**The 6 Phases**:

| Phase | For | Output | Next |
|-------|-----|--------|------|
| 1. INTAKE | NEW | PROJECT_BRIEF, REQUIREMENTS, SUCCESS_METRICS, CONSTRAINTS | → 2 |
| 2. ARCHITECTURE | NEW | SYSTEM_ARCHITECTURE, DATA_MODEL, API_SPEC, TECH_STACK | → 3 |
| 3. IMPLEMENTATION | NEW | USER_STORIES, TECHNICAL_TASKS, PROJECT_STRUCTURE, DEPENDENCIES | → 4 |
| 4. CODE GENERATION | NEW | Working code + tests + standards | → 5 |
| 5. QUALITY ASSURANCE | NEW/EXISTING | TEST_REPORT, CODE_REVIEW, DEPLOYMENT_CHECKLIST | ✅ DONE |
| 6. RECOVERY | EXISTING | CODEBASE_AUDIT, ISSUES_INVENTORY, RECOVERY_PLAN | → 3 |

**Why this structure?**
- Clear entry points (NEW or EXISTING project)
- Each phase has clear inputs, outputs, validation criteria
- Prevents "vibe coding" (each phase must complete before next)
- Scales from tiny scripts to massive applications

---

### 4. **The Shell** (`vibe_coding_agency/agency.py`)

**Location**: `/Users/ss/projects/ai_slop_agency/vibe_coding_agency/agency.py`

**What it does**:
- Interactive CLI that guides users through the workflow
- Classifies projects (NEW or EXISTING)
- Loads appropriate phase templates
- Saves project state + artifacts
- Allows resume / pause between phases

**How it works**:
1. User runs `python3 agency.py`
2. CLI asks: NEW or EXISTING?
3. CLI gets project name
4. CLI guides through phase sequence (with user approval between phases)
5. Each phase saves results to `projects/{project-name}/state.json`
6. User can stop/resume anytime

---

## Data Flow

### Example: NEW PROJECT

```
User: python3 agency.py
└─→ CLI: "NEW or EXISTING?" → User: A (NEW)
    └─→ CLI: "Project name?" → User: "task-app"
        └─→ Load Phase 1 Template (02.md INTAKE)
            └─→ Show instructions
            └─→ Collect user input
            └─→ Save to state.json
        └─→ CLI: "Proceed to Phase 2?" → User: y
            └─→ Load Phase 2 Template (04.md ARCHITECTURE)
            └─→ ... (repeat for each phase)

Result: ~/projects/task-app/state.json with all artifacts
```

### Example: CODE ANALYSIS (via Notebook)

```
External Agent (e.g., Claude Code):
  ├─ POST /api/v1/run {notebook_type: "analysis", project: "foo", request: "..."}
  │
  └─→ NotebookOrchestrator:
      ├─ Loads analysis_workflow.ipynb
      ├─ Injects parameters via papermill
      ├─ Executes with subprocess
      │   ├─ PHASE 1: Parse request (no API needed)
      │   ├─ PHASE 2: Research (Google Search API)
      │   ├─ PHASE 3: Validate (subprocess runs flake8, bandit, etc.)
      │   └─ PHASE 4: Generate report (no API needed)
      │
      └─→ Returns JSON:
          {
            "status": "success",
            "project_id": "foo-20251110",
            "notebook_path": "projects/foo/executed.ipynb",
            "report": { ... }
          }
```

---

## Technology Stack

| Layer | Tech | Why |
|-------|------|-----|
| **CLI/API** | Click (CLI) / Flask (REST) | Minimal dependencies, easy to extend |
| **Workflow Execution** | Papermill | Clean parameter injection, no string munging |
| **Notebooks** | Jupyter | Combines code + documentation + outputs |
| **LLM** | Google Gemini / Mistral | User's choice (easily swappable) |
| **Web Search** | Google Custom Search API | Real external sources |
| **Tools** | subprocess | Any CLI tool (flake8, bandit, npm audit, etc.) |
| **Storage** | JSON + Markdown | Human-readable, git-friendly, no database |
| **Language** | Python 3.9+ | Why not? |

---

## Key Design Decisions

### 1. **Notebooks, not just Python**
✅ **Pro**: Code + documentation together, interactive, easy to review
❌ **Con**: Harder to version control than .py files

### 2. **Papermill for parameter injection**
✅ **Pro**: No complex string manipulation, clean audit trail
❌ **Con**: Requires Jupyter

### 3. **Subprocess for tools**
✅ **Pro**: Any CLI tool works (flake8, bandit, npm audit, etc.)
❌ **Con**: Tools must be installed locally

### 4. **No database**
✅ **Pro**: No schema migrations, git-friendly, portable
❌ **Con**: Not suitable for massive-scale analytics

### 5. **Philosophy first, code second**
✅ **Pro**: Prevents hallucinations, creates accountability
❌ **Con**: Takes longer (but the result is defensible)

---

## File Structure

```
ai_slop_agency/
├── agency-system-complete/          # THE MOTOR
│   ├── agency-system/
│   │   ├── cli/main.py              # REST API + CLI entry
│   │   ├── orchestrator/core.py     # NotebookOrchestrator
│   │   ├── api/rest.py              # Flask routes
│   │   └── notebooks/
│   │       └── analysis_workflow.ipynb  # Master template
│   └── projects/                    # Working projects
│       └── {project-name}/
│           ├── state.json           # Progress
│           ├── report.md            # Final output
│           └── executed.ipynb       # Audit trail
│
├── agency_knowledge_base/           # THE PHILOSOPHY
│   ├── 00_THE_CORE_PROTOCOL.md
│   ├── 01_PROTOCOLS/*.md
│   ├── 02_TEMPLATES/*.md
│   └── ... (documentation)
│
└── vibe_coding_agency/              # THE SHELL + MASTERPLAN
    ├── agency.py                    # Interactive CLI
    ├── README.md
    ├── projects/                    # Working projects
    │   └── {project-name}/
    │       └── state.json
    │
    └── Masterframework/             # The 6-phase templates
        ├── 01.md (Master overview)
        ├── 02.md (NEW PROJECT INTAKE)
        ├── 03.md (EXISTING PROJECT RECOVERY)
        ├── 04.md (ARCHITECTURE DESIGN)
        ├── 05.md (IMPLEMENTATION PLAN)
        ├── 06.md (CODE GENERATION)
        ├── 07.md (QUALITY ASSURANCE)
        └── 08.md (Quick start guide)
```

---

## How It All Works Together

### Scenario 1: User via CLI

```bash
$ cd vibe_coding_agency
$ python3 agency.py
> NEW
> my-app
> [Intake questions...]
> [Approve to proceed?] y
> [Architecture questions...]
... etc
→ projects/my-app/state.json contains all artifacts
```

### Scenario 2: External Agent via API

```python
import requests

# Claude Code or GitHub Actions calls the API
response = requests.post(
    "http://localhost:5000/api/v1/run",
    json={
        "project_name": "audit-project",
        "notebook_type": "analysis",
        "client_request": "Security audit needed",
        "code_path": "/path/to/code",
        "tech_stack": "python"
    }
)

# Gets back validated results (no hallucinations!)
result = response.json()
print(result["report"])  # Professional markdown report
```

### Scenario 3: Extension - Add Custom Phase

To add a new phase (e.g., "DEPLOYMENT"):
1. Create `07.md` in Masterframework (template + instructions)
2. Create `deployment_workflow.ipynb` in notebooks/
3. Update `agency.py` Phase enum
4. Done! (CLI automatically picks it up)

---

## The Golden Rule

**Every system follows this flow:**

```
Raw Input
    ↓
UNDERSTAND (Extract facts, identify gaps)
    ↓
RESEARCH (Find external sources, cite them)
    ↓
VALIDATE (Run real tools, get real data)
    ↓
SYNTHESIZE (Combine into report)
    ↓
Output (Professional, defensible, fact-based)
```

No speculation. No hallucinations. Only:
- Facts (from understanding the request)
- Research (from external sources)
- Data (from real tools)
- Synthesis (combining all three)

---

## Next Steps to Use

1. **For Interactive Workflow**:
   ```bash
   cd vibe_coding_agency
   python3 agency.py
   ```

2. **For Automated Analysis**:
   ```bash
   cd agency-system-complete
   python3 cli/main.py serve --port 5000
   # Then call the API from Claude Code or another agent
   ```

3. **To Add New Workflows**:
   - Create a new notebook in `agency-system-complete/agency-system/notebooks/`
   - Follow the 4-phase structure (Understand → Research → Validate → Report)
   - Register in NotebookOrchestrator
   - Done!

---

## Summary

You had three fragmented systems. Now you have **one cohesive architecture**:

- **The Motor** (agency-system-complete) does the heavy lifting
- **The Philosophy** (agency_knowledge_base) ensures quality
- **The Masterplan** (Masterframework) provides structure
- **The Shell** (agency.py) is the user interface

Together: A professional, defensible, scalable system for structured software consulting.

**Welcome to Vibe Coding Agency.** 🚀

