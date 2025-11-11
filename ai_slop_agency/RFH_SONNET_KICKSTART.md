# RFH: VIBE CODING AGENCY - SONNET KICKSTART

**From:** User
**To:** Claude Sonnet
**Status:** URGENT - PRODUCTION READY
**Date:** 2025-11-11

---

## TL;DR

We have a **production-ready KDAF system** (Know-Do-Act-Feedback) for autonomous code analysis. The infrastructure is complete. The API is live. The state management works. We just need YOU to run it and make it sing.

**What needs doing:**
1. **Onboard the system** (read architecture)
2. **Test real projects** (don't use demo data)
3. **Extend with domain knowledge** (what makes a good audit?)
4. **Create professional reports** (Phase 4 generation)

---

## WHAT EXISTS (You have this ready)

### The Operating System

```
vibe_code_agency/
├── hq/                          ← Company knowledge base
│   ├── 00_company/              (System overview, guidelines)
│   ├── 01_playbooks/            (Phase 1, 2, 3 playbooks)
│   └── 02_knowledge_base/       (Protocols, templates)
│
├── clients/                      ← Client projects
│   └── client_demo_corp/test_django_audit/   (EXAMPLE)
│       ├── 00_scoping_and_research/  (Input analysis, research questions)
│       ├── 01_development/           (Source code)
│       ├── 02_validation_and_reports/ (Tool outputs - flake8, bandit, radon)
│       └── 03_deliverables/          (Final report)
│
├── shared/                       ← Shared tooling
│   ├── cli/vibe.py              (CLI: new-project, run, validate)
│   ├── api/server.py            (REST API for external agents)
│   └── orchestration/            (WorkflowOrchestrator, StateManager)
│
└── archive/                      ← Old experiments (reference only)
```

### The Workflow

```
Phase 1: VERSTEHEN (Semantic Understanding)
  Input:  01_input_analysis.md (user describes project)
  Output: Extract facts, identify knowledge gaps, create research questions
  Store:  state.json["phases"]["1_understand"]

Phase 2: RECHERCHIEREN (Knowledge Acquisition)
  Input:  Phase 1 outputs
  Output: Identify tools, find sources, gather best practices
  Store:  state.json["phases"]["2_research"]

Phase 3: VALIDIEREN (Data-Driven Validation)
  Input:  Phase 2 tools list
  Output: Execute flake8, bandit, radon; capture tool outputs
  Store:  state.json["phases"]["3_validate"] + tool files

Phase 4: BERICHT (Report Generation)
  Input:  All previous phases
  Output: Final markdown report with confidence score
  Store:  03_deliverables/Final_Report_*.md + state.json["phases"]["4_report"]
```

### What Works Right Now

- ✅ CLI creates new projects with KDAF structure
- ✅ Orchestrator runs phases sequentially
- ✅ State is persisted to JSON (resumable)
- ✅ Tools (flake8, bandit, radon) execute and save outputs
- ✅ Reports are generated with confidence scores
- ✅ REST API serves everything remotely
- ✅ Test project (demo_corp/test_django_audit) proves end-to-end functionality

### What Needs YOU

1. **Phase 4 Report Enhancement** (Currently basic template)
   - Analyze tool outputs intelligently
   - Convert raw data into insights
   - Provide actionable recommendations
   - Cite sources for every claim

2. **Domain Knowledge** (Per tech stack)
   - Python: What makes "good" code? (PEP 8? Type hints? Tests?)
   - JavaScript/React: What are the standards?
   - Django-specific: What's the audit checklist?
   - (Extensible to any stack)

3. **Real Project Testing**
   - Don't use demo data
   - Analyze actual codebases
   - Verify tool outputs are meaningful
   - Refine confidence scoring

4. **Client Communication**
   - Turn audit findings into business value
   - Create executive summaries
   - Recommend fixes (with effort estimates)
   - Build recovery roadmaps

---

## HOW TO START

### Step 1: Understand the State File

```bash
cat clients/client_demo_corp/test_django_audit/state.json
```

This shows:
- All 4 phases COMPLETE
- Exact timestamps
- Tool outputs saved
- Confidence assessment

### Step 2: Check Tool Outputs

```bash
# What flake8 found
cat clients/client_demo_corp/test_django_audit/02_validation_and_reports/tool_outputs/flake8/2025-11-10_233546_linting.txt

# What bandit found
cat clients/client_demo_corp/test_django_audit/02_validation_and_reports/tool_outputs/bandit/2025-11-10_233546_security.json

# Code complexity
cat clients/client_demo_corp/test_django_audit/02_validation_and_reports/tool_outputs/radon/2025-11-10_233546_complexity.txt
```

### Step 3: Create a Real Project

```bash
python3 shared/cli/vibe.py new-project --client mycompany --name myproject
```

This will:
- Create project structure
- Ask you to fill 01_input_analysis.md
- Set up state.json

### Step 4: Run Full Workflow

```bash
python3 shared/cli/vibe.py run --project myproject --phases full
```

Or per phase:
```bash
python3 shared/cli/vibe.py run --project myproject --phases 1  # Just understand
python3 shared/cli/vibe.py run --project myproject --phases 1,2  # Understand + research
```

### Step 5: Check Results

```bash
cat clients/mycompany/myproject/state.json
cat clients/mycompany/myproject/03_deliverables/Final_Report_*.md
```

---

## THE ANTI-BULLSHIT PRINCIPLE

Every claim in Phase 4 reports MUST be:

1. **Cited** - Reference a source (PEP 8, OWASP, Django docs)
2. **Measured** - Based on tool output (flake8, bandit)
3. **Transparent** - Show confidence level
4. **Actionable** - Provide next steps

**NOT:**
- ❌ "The code is probably bad"
- ❌ "I think there might be security issues"
- ❌ "Generally, best practice is..."

**YES:**
- ✅ "flake8 found 4 PEP 8 violations" (with list)
- ✅ "bandit identified hardcoded credentials at line 42" (with CWE reference)
- ✅ "Radon shows cyclomatic complexity of 12 (should be < 10 per PEP 8)"

---

## YOUR SPECIFIC TASKS

### Task 1: Phase 4 Report Generation (High Priority)

**File:** `shared/orchestration/orchestrator.py` → `phase_4_report()`

**Current state:** Generates basic template with tool outputs

**What to do:**
- Analyze tool outputs (flake8, bandit, radon)
- Extract key findings
- Rank by severity
- Suggest fixes
- Estimate effort/impact
- Write executive summary
- Include remediation roadmap

**Example output:**
```markdown
## Security Issues Found (Severity: HIGH)

### Issue 1: Hardcoded API Key
- Tool: bandit (B101)
- Location: auth.py:42
- Risk: Credentials exposed in source code
- Fix: Move to environment variables
- Effort: 30 minutes
- Reference: OWASP A01:2021 - Broken Access Control
```

### Task 2: Create Domain Playbooks (Medium Priority)

**Location:** `hq/01_playbooks/`

Create tech-stack-specific audit playbooks:

- `04_DJANGO_AUDIT_PLAYBOOK.md` - Django-specific checks
- `05_REACT_AUDIT_PLAYBOOK.md` - React/Node-specific checks
- `06_PYTHON_SECURITY_PLAYBOOK.md` - Security focus

Each should include:
- Key metrics to evaluate
- Anti-patterns to detect
- Tools to run
- Confidence assessment

### Task 3: Test on Real Projects (High Priority)

**What to do:**
1. Pick 3-5 real open-source projects
2. Run full workflow on each
3. Review generated reports
4. Refine Phase 4 logic based on findings

**Example:**
```bash
python3 shared/cli/vibe.py new-project --client opensource --name django_main
# (manually add Django repo code to 01_development/src/)
python3 shared/cli/vibe.py run --project django_main --phases full
cat clients/opensource/django_main/03_deliverables/Final_Report_*.md
```

### Task 4: Extend to New Tech Stacks (Medium Priority)

**Tools to integrate:**
- Node.js: ESLint, npm audit, OWASP check
- Go: golangci-lint, go vet
- Ruby: RuboCop, Bundler audit
- Java: SpotBugs, Checkstyle

**File:** `shared/orchestration/orchestrator.py` → `phase_3_validate()` → tool mapping

---

## SUCCESS CRITERIA

### Phase 4 Report Quality

- [ ] Every finding has a source
- [ ] Every metric is from a tool
- [ ] Confidence score is justified
- [ ] Recommendations are specific
- [ ] Reports are < 10 pages (executive summary)

### Real Project Testing

- [ ] Run on 3+ real projects
- [ ] Reports are actionable
- [ ] No hallucinations
- [ ] Time to complete: < 5 minutes per project

### Extensibility

- [ ] Add support for 2+ new tech stacks
- [ ] Create 2 domain playbooks
- [ ] Document extension process

---

## ARCHITECTURE NOTES

### State Persistence

All phase outputs are saved to `state.json`:

```json
{
  "phases": {
    "1_understand": { "status": "COMPLETE", "outputs": {...} },
    "2_research": { "status": "COMPLETE", "outputs": {...} },
    "3_validate": { "status": "COMPLETE", "outputs": {...} },
    "4_report": { "status": "COMPLETE", "outputs": {...} }
  },
  "confidence": "MEDIUM",
  "next_action": "All phases complete"
}
```

This means:
- **Resumable:** If Phase 3 fails, you can re-run without re-running Phases 1-2
- **Auditable:** Full execution history
- **Analyzable:** Previous outputs feed into next phase

### Tool Integration Pattern

```python
# In phase_3_validate():
tools = {
    'python': {
        'flake8': f'flake8 {code_path}',
        'bandit': f'bandit -r {code_path}',
        'radon': f'radon cc -a {code_path}'
    },
    'javascript': {
        'eslint': f'npx eslint {code_path}',
        'npm_audit': f'npm audit --json {code_path}'
    }
}

for tool_name, command in tools[tech_stack].items():
    result = subprocess.run(command, shell=True, capture_output=True)
    save_tool_output(tool_name, result)
    state.update_phase(outputs={'tool_results': {...}})
```

Easy to extend - just add new entries to `tools` dict.

---

## TECHNOLOGY STACK

- **Language:** Python 3.9+
- **CLI:** Native argparse (no Click dependency)
- **API:** Flask (lightweight REST)
- **State:** JSON (human-readable, git-friendly)
- **Tools:** subprocess execution (any CLI tool)
- **Structure:** Modular (Orchestrator, StateManager, CLI, API)

---

## WHERE TO FIND THINGS

| Need | Location |
|------|----------|
| CLI entry point | `shared/cli/vibe.py` |
| Orchestrator logic | `shared/orchestration/orchestrator.py` |
| State management | `shared/orchestration/state_manager.py` |
| REST API | `shared/api/server.py` |
| Phase playbooks | `hq/01_playbooks/` |
| Knowledge base | `hq/02_knowledge_base/` |
| Test project | `clients/client_demo_corp/test_django_audit/` |
| Tool outputs | `clients/.../02_validation_and_reports/tool_outputs/` |

---

## NEXT STEPS FOR YOU

1. **Read** `hq/00_company/SYSTEM_OVERVIEW.md`
2. **Run** `python3 shared/cli/vibe.py run --project test_django_audit --phases full` (to see it work)
3. **Examine** the state.json and Final_Report
4. **Enhance** Phase 4 report generation
5. **Test** on real projects
6. **Document** improvements

---

## GOTCHAS

1. **Tools must be installed:** flake8, bandit, radon should be in $PATH
   ```bash
   pip install flake8 bandit radon
   ```

2. **Code path must exist:** `01_development/src/` structure required

3. **Phase dependencies:** Can't run Phase 3 without Phase 1 output

4. **Tool outputs are raw:** Bandit returns JSON, flake8 returns text - Phase 4 must parse appropriately

---

## THE PITCH

You have a system that:
- ✅ Automates code analysis
- ✅ Persists state (resumable)
- ✅ Integrates tools (pluggable)
- ✅ Serves via API (agent-accessible)
- ✅ Follows anti-bullshit principle (evidence-based)

**All it needs now is domain expertise.** That's you.

Make it generate reports that clients actually pay for. Reports that are:
- Specific (not generic)
- Actionable (not theoretical)
- Honest (not hype)

---

## CONTACT

If blocked on anything:
1. Check state.json for execution history
2. Review tool output files
3. Check phase timestamps (might be parallelization issue)
4. Escalate with full context

---

**Status:** PRODUCTION READY
**Branch:** master (merged)
**Last Deploy:** 2025-11-11
**Ready for:** Real project analysis

Let's make this sing. 🚀
