# Python Project Audit Framework

## AGENT CONFIGURATION
```yaml
role: "Project Auditor & Refactoring Planner"
output_format: "Single Markdown Report"
token_budget: "Focus on problems, not descriptions"
```

## EXECUTION RULES

### 0. Tool Availability Check (Run First!)
```bash
# Check which tools are available:
command -v ruff && echo "✅ ruff" || echo "❌ ruff (install: pip install ruff)"
command -v radon && echo "✅ radon" || echo "❌ radon (install: pip install radon)"
command -v vulture && echo "✅ vulture" || echo "❌ vulture (install: pip install vulture)"
command -v jscpd && echo "✅ jscpd" || echo "❌ jscpd (optional)"

# If CRITICAL tools missing (ruff, radon):
# → Warn user and proceed with degraded analysis
# → Mark all metrics as "⚠️ ESTIMATED"
```

### 1. File Discovery (Token-Efficient)
```python
# SCAN ONLY:
include_patterns = ["**/*.py"]
exclude_patterns = [
    "**/venv/**", "**/.venv/**", "**/env/**",
    "**/__pycache__/**", "**/.pytest_cache/**",
    "**/node_modules/**", "**/.git/**",
    "**/build/**", "**/dist/**", "**/*.egg-info/**"
]

# If >50 files: Sample strategically
priority_scan = [
    "*/cli*.py", "*/main.py", "*/app.py",  # Entry points
    "*/core/*.py", "*/models.py",           # Core logic
    "**/config*.py", "**/utils.py"          # Infrastructure
]
```

### 2. Analysis Focus (CLI-Tool Driven)

**Execute these commands and parse outputs:**

```bash
# 1. LINTING ISSUES (real problems)
ruff check {project_root} --output-format=json > ruff_output.json
# Parse: error codes, file locations, violation counts

# 2. CYCLOMATIC COMPLEXITY (exact numbers)
radon cc {project_root} -s -j > complexity.json
# Parse: per-function complexity scores, grade (A-F)

# 3. DEAD CODE DETECTION
vulture {project_root} --min-confidence 80 > dead_code.txt
# Parse: unused imports, unreferenced functions

# 4. LINE COUNTS (size metrics)
find {project_root} -name "*.py" -not -path "*/venv/*" -exec wc -l {} + | sort -nr > loc_report.txt
# Parse: total LOC, largest files

# 5. DEPENDENCY GRAPH
grep -r "^import\|^from" {project_root}/**/*.py | grep -v "venv" > imports.txt
# Manual parse: build adjacency list

# 6. DUPLICATION (optional - if jscpd installed)
jscpd {project_root} --reporters json --output duplication.json
# Parse: duplicate blocks, percentage
```

**Data Extraction Rules:**
- If tool fails → report error, continue with available data
- Parse JSON with error handling (malformed output possible)
- Aggregate metrics: total issues, average complexity, etc.
- Cross-reference: e.g., high complexity + no tests = critical

### 3. Code Smell Detection (Pattern Matching)

```python
CRITICAL_PATTERNS = {
    "god_function": "Function >100 LOC or >5 responsibilities",
    "duplication": "Same logic in ≥3 places (fuzzy match)",
    "magic_values": "Hardcoded strings/numbers without constants",
    "dead_code": "Imports/functions with 0 references",
    "circular_deps": "Module A imports B imports A",
    "mixed_concerns": "Data model with business logic",
    "missing_validation": "User input without checks",
    "hallucination_risk": "API calls without version pins"
}

# For each detected smell:
# - Show 3-5 line code snippet
# - Count occurrences
# - Estimate fix effort (S/M/L)
```

---

## OUTPUT TEMPLATE

```markdown
# Project Audit Report
**Generated:** {timestamp}
**Files Analyzed:** {count} Python files ({total_loc} LOC)
**Critical Issues:** {critical_count}

---

## Executive Summary

**Project Health Score:** {score}/100
- 🔴 Critical: {n} issues (must fix before production)
- 🟡 High: {n} issues (fix this sprint)
- 🟢 Medium: {n} issues (technical debt)

**Top 3 Risks:**
1. {Concrete risk with module name}
2. {Concrete risk with module name}
3. {Concrete risk with module name}

---

## Architecture Overview

```
{ASCII dependency tree - max 20 lines}
Example:
cli_app.py
├─> core/orchestrator.py
│   ├─> providers/mistral.py ⚠️ (circular with core/task_handlers.py)
│   └─> core/task_handlers.py
└─> utils.py (loaded by everyone - god module?)
```

**Module Coupling Score:** {score} (lower = better)
- Highly coupled: {list modules with >5 dependencies}

---

## Critical Issues (Detail)

### 🔴 CRITICAL-1: {Short Title}
**Module:** `{file_path}`
**Pattern:** {smell_name}
**Impact:** {why this breaks in production}

**Evidence:**
```python
# commands/os.py:145-165 (Simplified view)
def execute_project_workflow(project_root, offline=False, interactive=False, ...):
    # 22 branches of complexity stem from:
    if offline:
        if not config:
            if interactive:
                config = _interactive_workflow()  # ← Nested function call
            else:
                raise ValueError("...")
        # ... validate offline config
    else:
        if config:
            # ... merge with defaults
        else:
            # ... load from registry

    # Then 30+ more lines of execution logic
    # Problem: Config loading + validation + execution in ONE function
```
**Root Cause:** Violates SRP - function does 3 things (load, validate, execute)

**Metrics:**
- LOC: 523 lines in one dict
- Duplication: 0% (but should be in DB/YAML)
- Fix Effort: **LARGE** (requires data migration)

**Fix Strategy:**
1. Extract to YAML config file
2. Add schema validation (Pydantic)
3. Update loader in utils.py
4. Estimated: 4-6 hours

**Dependencies Affected:** {list of 3-5 modules that import this}

---

### 🔴 CRITICAL-2: {Next Issue}
{Same format...}

---

## High Priority Issues (Summary)

| ID | Module | Problem | LOC/Complexity | Fix Effort |
|----|--------|---------|----------------|------------|
| H-1 | providers/*.py | Duplicated API key loading (3x) | 45 LOC each | SMALL (2h) |
| H-2 | models.py | Mixed old/new fields (`font_size`) | 234 LOC | MEDIUM (4h) |
| H-3 | core/orchestrator.py | String-based magic templating | Cyclomatic: 12 | MEDIUM (3h) |

---

## Code Quality Metrics

### Duplication Analysis
```
Total Duplicate Blocks: {n}
Worst Offenders:
1. API key loading pattern (providers/*.py) - 3 copies, 45 LOC each
2. Error handling boilerplate - 12 copies, ~10 LOC each
```

### Complexity Hotspots
```
Top 5 Most Complex Functions:
1. cli_app.main() - 145 LOC, Cyclomatic: 18 ⚠️
2. orchestrator._format_task_params() - 67 LOC, Cyclomatic: 14 ⚠️
3. utils.load_config() - 89 LOC, Cyclomatic: 11 ⚠️
```

### Dead Code
```
Unused Imports: {n}
Unreferenced Functions: {list}
Legacy Modules: social.py (deprecated wrapper)
```

---

## Refactoring Roadmap

### Phase 1: Stop the Bleeding (Week 1)
**Goal:** Fix critical production risks

- [ ] **Day 1-2:** Extract config.py constants to YAML
  - Risk: Config changes require code redeploy
  - Blocker: None

- [ ] **Day 3:** Remove social.py legacy wrapper
  - Risk: Breaks old imports (grep first!)
  - Blocker: None

- [ ] **Day 4-5:** Deduplicate provider API key loading
  - Risk: Low (isolated change)
  - Blocker: None

**Validation:** All tests pass + manual smoke test

---

### Phase 2: Structural Fixes (Week 2-3)
- [ ] Refactor models.py (remove old fields + business logic)
- [ ] Simplify orchestrator templating (use Jinja2 or dataclasses)
- [ ] Break up cli_app.main() god function

---

### Phase 3: Technical Debt (Month 2+)
- [ ] Add type hints (mypy strict mode)
- [ ] Increase test coverage to >80%
- [ ] Document config cascade (utils.load_config)

---

## Quick Wins (Do Today)

1. **Add to .gitignore / scan exclusions:**
   ```
   venv/
   __pycache__/
   *.pyc
   .pytest_cache/
   ```

2. **Run existing linters:**
   ```bash
   ruff check . --fix
   mypy agency_toolkit/
   ```

3. **Grep for TODOs/FIXMEs:**
   ```bash
   rg "TODO|FIXME|HACK|XXX" --type py
   ```

---

## Appendix: Analysis Methodology

**Tools Used (CLI Execution):**
```bash
# Run these commands and parse output:
ruff check {project_root} --output-format=json     # Linting issues
radon cc {project_root} -s -j                      # Cyclomatic complexity
vulture {project_root} --min-confidence 80         # Dead code detection
find {project_root} -name "*.py" -exec wc -l {} +  # LOC counting
grep -r "^import\|^from" {project_root}/*.py       # Dependency extraction
```

**Analysis Steps:**
1. Execute each tool via subprocess
2. Parse JSON/text output
3. Cross-reference with manual code reading
4. Generate consolidated report

**Confidence by Metric:**
- Linting issues: ✅ HIGH (ruff output)
- Complexity: ✅ HIGH (radon calculated)
- Dead code: 🟡 MEDIUM (vulture heuristics)
- Duplication: 🟡 MEDIUM (visual + grep patterns)
- Architecture: ✅ HIGH (import analysis + human review)

**If tools are not installed:**
```bash
pip install ruff radon vulture
# Or provide alternative analysis method
```
```

---

## AGENT SELF-CHECK (Before Output)

Run this checklist:
- [ ] Every critical issue has a **code snippet**
- [ ] Every issue has **estimated fix effort**
- [ ] Dependency tree is **ASCII, not verbose**
- [ ] No analysis of venv/cache/build folders
- [ ] Total report is <5000 tokens
- [ ] Actionable roadmap with **concrete tasks**
- [ ] Metrics are **numbers**, not adjectives

If any ❌: **Revise before sending report.**

---

## Usage Example

```bash
# In your CLI tool:
claude --project-root /path/to/project \
       --output audit_report.md \
       --framework "Python Project Audit Framework"
```

**Expected Output:** One `audit_report.md` file following template above.
