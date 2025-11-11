# Agency Toolkit: Production Hardening Roadmap

**Goal**: Transform AI-generated prototype into a portfolio-grade, production-ready application.

**Philosophy**: Fix once, verify always. Every change must have a test. Every test must reflect real-world usage.

---

## 🔴 CRITICAL RECOVERY REQUIRED (BLOCKING ALL FURTHER WORK)

**Status**: ⚠️ **BLOCKIERT** - Deleted Tests & Unvalidated Performance SLO

### The Problem

During Epic 2.5 & 4.0 implementation (2025-11-09), **critical UAT tests were deleted** to achieve "green" test suite status:

- ❌ `tests/integration/test_social_campaign.py` — Deleted (50-post batch UAT)
- ❌ `tests/integration/test_performance.py` — Deleted (100-post <5min SLO)
- ⚠️ **Unvalidated Critical Requirement**: "100 posts in < 5 minutes" is documented but NOT tested

**Root Cause**: The tests were failing because they relied on a non-existent API (`generate_social_post`). Instead of fixing the API, the tests were deleted.

**Impact**:
- No validation that batch workflows work end-to-end
- Critical SLO unproven before production
- False "green" test signal masks real gaps

### Recovery Actions (MUST COMPLETE BEFORE EPIC 4.0)

#### Epic 2.5.7: Restore UAT Tests ⚠️ IMMEDIATE PRIORITY

**Estimated Time**: 4 hours

**Tasks**:
- [ ] **Test 1: Batch Campaign** (`tests/uat/test_batch_campaign.py`)
  - Load CSV with 100 posts
  - Measure total execution time
  - Assert duration < 300 seconds (5 minutes)
  - **MOCK** image generation (use `@patch` decorator, don't call Pollinations)
  - Verify file creation and PNG validity

- [ ] **Test 2: Social Campaign** (`tests/uat/test_social_campaign.py`)
  - 50-post batch with all styles (modern, bold, minimal)
  - All posts generate successfully
  - Verify all files exist and are valid PNG
  - Check dimensions (1080x1080 for square format)
  - **MOCK** Pollinations provider

- [ ] **Test 3: Performance Benchmarks** (`tests/uat/test_performance.py`)
  - Throughput benchmark: posts/second (target: >10)
  - Latency benchmark: P95 < 2 seconds
  - Memory profiling: 1000-post batch uses constant memory (<100MB growth)
  - **MOCK** all external APIs

**Key Requirement**: All tests must use `@patch` or `unittest.mock` to avoid external API calls. No real Pollinations/Mistral requests.

**Exit Criteria**:
- ✅ All 3 tests passing
- ✅ 100-post SLO validated or clearly documented as limitation
- ✅ No external API calls in tests

#### Epic 4.0.2: SLO Documentation ⚠️ REQUIRED BEFORE RELEASE

**Estimated Time**: 2 hours

**Tasks**:
- [ ] Create `docs/PERFORMANCE.md` documenting SLOs:
  ```markdown
  ## Performance SLOs (Validated 2025-11-XX)

  | Metric | Target | Measured | Status |
  |--------|--------|----------|--------|
  | Throughput | >10 posts/sec | ??? | ⏳ PENDING |
  | P95 Latency | <2 seconds | ??? | ⏳ PENDING |
  | 100-post batch | <5 minutes | ??? | ⏳ PENDING |
  ```

- [ ] Update README.md with "Performance Guarantees" section
- [ ] Document any gaps between desired & achievable SLOs
- [ ] Add CI check that blocks releases if SLOs regress >10%

**Exit Criteria**:
- ✅ All SLOs documented
- ✅ README updated with performance guarantees
- ✅ CI includes SLO validation

### Blocking Checklist (MUST ✅ BEFORE EPIC 4.0 CONTINUATION)

```
[ ] Epic 2.5.7 Complete: Restored test_batch_campaign.py (MOCKED)
[ ] Epic 2.5.7 Complete: Restored test_social_campaign.py (MOCKED)
[ ] Epic 2.5.7 Complete: Restored test_performance.py (MOCKED)
[ ] Epic 4.0.2 Complete: SLO documented in PERFORMANCE.md
[ ] Epic 4.0.2 Complete: README updated with performance metrics
[ ] All 521+ unit tests passing
[ ] All 4 UAT scenarios passing
[ ] No "green signal" from hiding failures
```

**Next Step**: Do NOT proceed to Epic 4.0.3+ until all boxes are checked.

---

## 📊 EXECUTIVE SUMMARY (Updated 2025-11-09)

### Current Status
- ✅ **Epic 1.0 (Load Config)**: Complete - CC 20 → 3
- ✅ **Epic 1.1 (Typer/Reporter)**: Complete - Type error fixed via DI
- ✅ **Epic 1.2 (Security)**: Complete - 3/4 CVEs resolved (torch pending platform support)
- ✅ **Epic 2.0 (Task Handlers)**: Complete - Plugin system migrated
- ✅ **Epic 2.2 (Config Management)**: Complete
- ✅ **Epic 3.1 (os.py refactor)**: Complete - CC 17 → 3
- ✅ **Epic 3.2 (validate.py refactor)**: Complete - CC 17 → 9
- 📊 **Test Suite**: 350/350 passing (core tests)
- 🔒 **Security**: 3/4 CVEs fixed, 1 blocked by PyTorch availability

### Revised 3-Week Plan
```
Week 1: FOUNDATION + SECURITY
  ✅ Epic 1 & 2 refactoring (DONE)
  ✅ Epic 2.2 (DONE)
  ✅ P0: Security updates (DONE - 3/4 CVEs fixed)
  🟡 P1: Error handling (4h) ← IN PROGRESS

Week 2: WORKFLOW ENGINE ← YOU ARE HERE
  🔥 Epic 2.5: Workflow Engine Stabilization (Est. 22h)
  Result: v0.3.0 (Core feature production-ready)

Week 3: ORGANIZATION & POLISH
  🔵 Prompts system (Epic 2.1) (7h)
  🎨 UX Improvements (Epic 3.1) (7h)
  📊 Performance (Epic 3.2) (10h)
  Result: v0.4.0 (ready for PyPI)
```

---

## PHASE 2: WORKFLOW ENGINE STABILIZATION (Week 2) 🔥

### Epic 2.5: Stabilize Workflow Engine ("Grand Agency OS")
**Why**: The orchestrator (`core/orchestrator.py`) is the core value proposition but has **zero test coverage** and known architectural complexity (dual-context system). Must be battle-tested before production.

**Critical Files**:
- `core/orchestrator.py` - Main execution engine
- `core/os_executor.py` - Workflow loader and validator
- `core/dependency_resolver.py` - Module ordering
- `tasks/*.py` - Task handler plugins
- `registry/seeds/*.json` - Workflow definitions

---

#### Story 2.5.1: Test the Orchestrator Core 🧪 **HIGHEST PRIORITY**
**Why**: `core/orchestrator.py` has **no tests** despite being mission-critical. The dual-context system (step_context vs raw_context) is error-prone and undocumented in tests.

**Tasks**:
- [ ] Create `tests/core/test_orchestrator.py`
- [ ] **Test 1: Basic Task Execution**
  - Execute a 3-task module with simple params
  - Verify all tasks complete successfully
  - Verify TaskResult objects are correct
- [ ] **Test 2: Context Templating (step_context)**
  - Task 1 outputs "Hello"
  - Task 2 has param `"text": "{output1}"`
  - Verify Task 2 receives "Hello" after substitution
- [ ] **Test 3: Raw Context for Lists** ⚠️ CRITICAL
  - Task 1 outputs `["tag1", "tag2", "tag3"]`
  - Verify `step_context["output1"]` == `"tag1, tag2, tag3"` (string)
  - Verify `raw_context["output1"]` == `["tag1", "tag2", "tag3"]` (list)
  - Task 2 tries to iterate → must use `context.get_raw()`
- [ ] **Test 4: Error Handling**
  - Task 2 of 5 raises exception
  - Verify subsequent tasks don't execute
  - Verify TaskResult has error=True
- [ ] **Test 5: Circular Dependencies**
  - Call `dependency_resolver.py` with circular deps
  - Verify it raises an error (already implemented in DFS algorithm)
- [ ] **Test 6: Multiple Modules**
  - Execute 2 modules where Module B depends on Module A
  - Verify execution order is correct
  - Verify Module B can access Module A's outputs

**Exit Criteria**:
- ✅ 6 tests passing
- ✅ Coverage of `core/orchestrator.py` > 80%
- ✅ The "hybrid context gotcha" is proven with tests

**Estimated Time**: 8 hours

**CLI Agent Prompt**:
```
Create comprehensive tests for core/orchestrator.py. Focus on:
1. Basic 3-task execution chain
2. Template substitution with {placeholders}
3. THE CRITICAL TEST: Verify step_context converts lists to strings, raw_context preserves them
4. Error propagation when a task fails
5. Module dependency ordering
6. Circular dependency detection

Reference the TaskContext class in tasks/base.py for get() vs get_raw() behavior.
Run: pytest tests/core/test_orchestrator.py -xvs --cov=agency_toolkit/core/orchestrator.py
Target: 80%+ coverage
```

---

#### Story 2.5.2: Test the Workflow Executor 📋
**Why**: `core/os_executor.py` loads workflows, validates them, and calls the orchestrator. Currently untested.

**Tasks**:
- [ ] Create `tests/core/test_os_executor.py`
- [ ] **Test 1: Load Valid Workflow**
  - Load a simple solution from `registry/seeds/solutions.json`
  - Verify modules are parsed correctly
- [ ] **Test 2: Detect Invalid Solution ID**
  - Try to load non-existent solution
  - Verify it raises appropriate error
- [ ] **Test 3: Validate Module References**
  - Solution references a module that doesn't exist
  - Verify `workflow_loader.validate_registry()` catches it
- [ ] **Test 4: Execute Full Workflow**
  - Execute a 2-module workflow end-to-end
  - Verify files are created in output_dir
  - Verify final report contains all task results

**Exit Criteria**:
- ✅ 4 tests passing
- ✅ Coverage of `core/os_executor.py` > 70%

**Estimated Time**: 5 hours

**CLI Agent Prompt**:
```
Create tests for core/os_executor.py covering:
1. Loading valid workflows from registry/seeds/
2. Detecting invalid solution/module IDs
3. Registry validation (cross-references)
4. Full end-to-end workflow execution

Use fixtures to create minimal test workflows (1-2 modules).
Run: pytest tests/core/test_os_executor.py -xvs --cov=agency_toolkit/core/os_executor.py
```

---

#### Story 2.5.3: Add Observability 📊
**Why**: Running workflows is a black box. Need visibility into what's executing.

**Tasks**:
- [ ] Add structured logging to `core/orchestrator.py`:
  ```python
  # At start of execute_module
  log.info("module_started", module_id=module['id'], task_count=len(module['tasks']))

  # Before each task
  log.info("task_executing", tool=task['tool'], output_key=task.get('output_key'))

  # After each task
  log.info("task_completed", output_key=task.get('output_key'), duration_ms=elapsed)
  ```
- [ ] Add progress indicator using `rich.progress`:
  ```python
  from rich.progress import Progress, SpinnerColumn, TextColumn

  with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
      task = progress.add_task(f"Executing module {module['id']}", total=len(module['tasks']))
      # ... update progress after each task
  ```
- [ ] Add `--verbose` flag to `commands/os.py` that enables DEBUG logging
- [ ] Test: Run a 5-task workflow with `--verbose` and verify logs appear

**Exit Criteria**:
- ✅ All major orchestrator events are logged
- ✅ Progress bar shows during execution
- ✅ `toolkit os init --verbose` shows detailed logs

**Estimated Time**: 4 hours

**CLI Agent Prompt**:
```
Add observability to core/orchestrator.py:
1. Add structured logging (loguru) for module_started, task_executing, task_completed
2. Add rich.progress bar showing "Task X of Y"
3. Add --verbose flag to commands/os.py that sets log level to DEBUG
4. Test with a multi-task workflow

Use the existing log object (already imported from utils).
```

---

#### Story 2.5.4: Improve Error Handling 🛡️
**Why**: Current error handling is basic try/except. Need graceful degradation.

**Tasks**:
- [ ] Add task-level error modes in workflow JSON:
  ```json
  {"tool": "ai", "on_error": "continue", "params": {...}}
  ```
  - `"stop"` (default): Halt workflow on error
  - `"continue"`: Log error, skip task, continue workflow
- [ ] Update `orchestrator.py:_execute_task`:
  ```python
  try:
      result = handler.execute(params, context)
  except Exception as e:
      if task.get('on_error') == 'continue':
          log.warning("task_failed_continuing", error=str(e))
          return TaskResult(success=False, error=str(e))
      raise
  ```
- [ ] Add retry logic (optional):
  ```python
  @retry(stop=stop_after_attempt(3), wait=wait_exponential())
  def _execute_task_with_retry(self, task, context):
      ...
  ```
- [ ] Create a `WorkflowExecutionReport` dataclass:
  ```python
  @dataclass
  class WorkflowReport:
      total_tasks: int
      successful: int
      failed: int
      skipped: int
      errors: list[str]
  ```
- [ ] Test: Workflow with 1 failing task and `on_error: continue` completes successfully

**Exit Criteria**:
- ✅ Workflows can continue after non-critical task failures
- ✅ Final report shows success/failure/skip counts
- ✅ Tests verify `on_error` behavior

**Estimated Time**: 5 hours

**CLI Agent Prompt**:
```
Add error resilience to core/orchestrator.py:
1. Support on_error: "continue" in task JSON
2. Update _execute_task to handle continue vs stop
3. Create WorkflowExecutionReport dataclass
4. Add tests for graceful failure handling

Optional: Add @retry decorator for transient failures (use tenacity library).
```

---

#### Story 2.5.5: Validate Workflow JSON Schema ✅
**Why**: `registry/seeds/*.json` files have no validation. Invalid JSON causes runtime errors.

**Tasks**:
- [ ] Create `schemas/solution.schema.json`:
  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "archetype_id", "modules"],
    "properties": {
      "id": {"type": "string", "pattern": "^solution-"},
      "archetype_id": {"type": "string"},
      "modules": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["id", "title", "tasks"],
          "properties": {
            "tasks": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["tool"],
                "properties": {
                  "tool": {"enum": ["ai", "social", "briefing", "structure"]},
                  "params": {"type": "object"},
                  "output_key": {"type": "string"}
                }
              }
            }
          }
        }
      }
    }
  }
  ```
- [ ] Add validation in `core/workflow_loader.py`:
  ```python
  import jsonschema

  def validate_solution(solution: dict):
      with open('schemas/solution.schema.json') as f:
          schema = json.load(f)
      jsonschema.validate(solution, schema)
  ```
- [ ] Add `toolkit validate workflow <path>` command
- [ ] Test: Load invalid JSON and verify it's caught before execution

**Exit Criteria**:
- ✅ All workflow JSON validates against schema
- ✅ Invalid workflows are rejected at load time
- ✅ CLI command for manual validation

**Estimated Time**: 3 hours

**CLI Agent Prompt**:
```
Create JSON Schema validation for workflows:
1. Create schemas/solution.schema.json defining workflow structure
2. Add validation in core/workflow_loader.py using jsonschema
3. Add 'toolkit validate workflow' command in commands/validate.py
4. Test with valid and invalid workflow files

Install jsonschema if needed: pip install jsonschema
```

---

#### Story 2.5.6: Document the Workflow System 📚
**Why**: README probably doesn't explain workflows. Need clear documentation.

**Tasks**:
- [ ] Create `docs/WORKFLOWS.md`:
  - What is the workflow engine?
  - How to write a workflow JSON
  - How task chaining works with `output_key` and `{placeholders}`
  - How to use `get_raw()` for lists in custom handlers
  - Available task handlers (`ai`, `social`, `briefing`, `structure`)
- [ ] Add 3 example workflows in `examples/workflows/`:
  - `simple-campaign.json` (1 module, 3 tasks)
  - `multi-module.json` (2 modules with dependencies)
  - `error-handling.json` (demonstrates `on_error: continue`)
- [ ] Update main `README.md`:
  - Add "Workflow Orchestration" section
  - Link to `docs/WORKFLOWS.md`
  - Show quick example: `toolkit os init --from-json examples/workflows/simple-campaign.json`
- [ ] Add inline code comments explaining dual-context in `orchestrator.py`

**Exit Criteria**:
- ✅ A new developer can write a workflow JSON without reading source code
- ✅ README has workflow section with examples
- ✅ `docs/WORKFLOWS.md` exists

**Estimated Time**: 3 hours

**CLI Agent Prompt**:
```
Create workflow documentation:
1. Write docs/WORKFLOWS.md explaining workflow system architecture
2. Create 3 example workflows in examples/workflows/
3. Add "Workflow Orchestration" section to README.md
4. Add code comments in orchestrator.py explaining step_context vs raw_context

Focus on practical examples, not just theory.
```

---

## ⚠️ ARCHITECTURAL SAFEGUARDS

### Add Runtime Type Check for Context (OPTIONAL but RECOMMENDED)
**Location**: `tasks/base.py:TaskContext.get()`

**Why**: The dual-context is the #1 gotcha. Add a safeguard to catch misuse.

**Implementation**:
```python
def get(self, key: str) -> str:
    """Get string-formatted value from step_context.

    WARNING: If you need a list/dict, use get_raw() instead!
    """
    val = self.step_context.get(key)
    if isinstance(val, (list, dict)):
        raise TypeError(
            f"Key '{key}' contains {type(val).__name__}. "
            f"Use context.get_raw('{key}') to access structured data."
        )
    return val
```

**Test**:
```python
def test_context_get_raises_on_complex_types():
    context = TaskContext(config=..., step_context={"items": [1, 2, 3]}, raw_context={"items": [1, 2, 3]})

    with pytest.raises(TypeError, match="Use context.get_raw"):
        context.get("items")

    assert context.get_raw("items") == [1, 2, 3]  # This works
```

**Estimated Time**: 1 hour

---

## REVISED DELIVERY SCHEDULE

| Week | Phase | Deliverable | Success Metric |
|------|-------|-------------|----------------|
| **Week 1** | Stabilize | ✅ COMPLETE | All tests passing, 3/4 CVEs fixed |
| **Week 2** | Workflow Engine | Tests + Observability + Error Handling + Validation + Docs | 80%+ coverage on orchestrator, workflows validated |
| **Week 3** | Polish | Prompts + UX + Performance | Ready for PyPI |

---

## TOTAL TIME ESTIMATE FOR EPIC 2.5

| Story | Hours | Priority |
|-------|-------|----------|
| 2.5.1: Orchestrator Tests | 8 | 🔥 CRITICAL |
| 2.5.2: Executor Tests | 5 | 🔥 CRITICAL |
| 2.5.3: Observability | 4 | 🟡 HIGH |
| 2.5.4: Error Handling | 5 | 🟡 HIGH |
| 2.5.5: JSON Validation | 3 | 🟢 MEDIUM |
| 2.5.6: Documentation | 3 | 🟢 MEDIUM |
| **TOTAL** | **28h** | 3.5 days |

---

## PHASE 3: PROFESSIONAL POLISH (Week 3) ✨

### Epic 3.3: Pre-Release Cleanup 🧹
**Why**: Before PyPI, the codebase must be production-grade. No TODOs, no dead code, consistent patterns everywhere.

#### Story 3.3.1: Code Audit & Cleanup (4 hours)
**Tasks**:
- [ ] **Search for TODO/FIXME/HACK comments**:
  ```bash
  rg "TODO|FIXME|HACK|XXX" --type py
  ```
  - Fix or create GitHub issues for each
  - Remove placeholder comments
- [ ] **Remove dead code**:
  ```bash
  vulture agency_toolkit/  # Finds unused code
  ```
  - Delete unused functions/classes
  - Remove commented-out code blocks
- [ ] **Standardize docstrings**:
  - All public functions need docstrings
  - Use Google style consistently
  - Example:
    ```python
    def generate(text: str, style: str) -> Path:
        """Generate a social media post image.

        Args:
            text: The post text content
            style: Visual style (minimal, bold, gradient)

        Returns:
            Path to the generated image file

        Raises:
            ValidationError: If text exceeds character limit
        """
    ```
- [ ] **Fix type hints**:
  ```bash
  mypy agency_toolkit/ --strict
  ```
  - Add missing type hints
  - Fix `Any` types where possible
- [ ] **Verify all imports**:
  ```bash
  isort agency_toolkit/ --check-only
  autoflake --remove-all-unused-imports --recursive agency_toolkit/
  ```

**Exit Criteria**:
- ✅ 0 TODO comments remain
- ✅ `mypy --strict` passes
- ✅ `vulture` reports <5% dead code
- ✅ All public APIs have docstrings

**CLI Agent Prompt**:
```
Run a comprehensive code audit:
1. Find all TODO/FIXME comments and either fix or file issues
2. Run vulture to find dead code and remove it
3. Add docstrings to all public functions (Google style)
4. Run mypy --strict and fix type issues
5. Clean up imports with isort and autoflake

Report findings before making changes.
```

---

#### Story 3.3.2: Dependency Audit (2 hours)
**Why**: Unused dependencies bloat the package. Security vulnerabilities must be resolved.

**Tasks**:
- [ ] **Check for unused dependencies**:
  ```bash
  pip-audit  # Already done, but verify
  pipdeptree  # Show dependency tree
  ```
- [ ] **Pin all versions in `pyproject.toml`**:
  ```toml
  dependencies = [
      "typer==0.9.0",  # Not "typer>=0.9.0"
      "pydantic==2.5.0",
      # ... etc
  ]
  ```
- [ ] **Create `requirements-dev.txt`** for development tools:
  ```
  pytest>=7.4.0
  pytest-cov>=4.1.0
  ruff>=0.1.0
  mypy>=1.7.0
  pre-commit>=3.5.0
  ```
- [ ] **Verify minimum Python version**:
  - Test install on Python 3.10, 3.11, 3.12
  - Update `requires-python = ">=3.10"` if needed

**Exit Criteria**:
- ✅ All dependencies pinned
- ✅ No unused packages in `pyproject.toml`
- ✅ `pip-audit` clean (except torch if unfixable)
- ✅ Tested on Python 3.10+

**CLI Agent Prompt**:
```
Audit dependencies in pyproject.toml:
1. Run pipdeptree to see what's actually used
2. Pin all version numbers (no >= ranges)
3. Create requirements-dev.txt for dev tools
4. Test pip install on Python 3.10, 3.11, 3.12

Report any unused or problematic dependencies.
```

---

#### Story 3.3.3: Fix Pre-Commit Hooks (2 hours) ⚠️ BLOCKING
**Status**: Currently broken, bypassed with `--no-verify`

**Tasks**:
- [ ] **Debug current pre-commit failure**:
  ```bash
  pre-commit run --all-files --verbose
  ```
  - Fix `questionary` import issue (if that's the cause)
  - Update `.pre-commit-config.yaml` hooks
- [ ] **Essential hooks to keep**:
  ```yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v4.5.0
      hooks:
        - id: trailing-whitespace
        - id: end-of-file-fixer
        - id: check-yaml
        - id: check-json
        - id: check-merge-conflict

    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.6
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.7.1
      hooks:
        - id: mypy
          additional_dependencies: [types-all]
  ```
- [ ] **Test hooks work**:
  ```bash
  pre-commit install
  git commit -m "test" --allow-empty
  ```

**Exit Criteria**:
- ✅ `pre-commit run --all-files` passes
- ✅ Commits trigger hooks automatically
- ✅ No more `--no-verify` needed

**CLI Agent Prompt**:
```
Fix broken pre-commit hooks:
1. Run pre-commit run --all-files --verbose to see exact error
2. Fix any import issues (questionary?)
3. Update .pre-commit-config.yaml with essential hooks only (ruff, mypy, trailing-whitespace)
4. Test with a dummy commit

Do NOT bypass hooks. Fix the root cause.
```

---

#### Story 3.3.4: README Polish (3 hours) 📝
**Why**: README is the project's first impression. Must be crystal clear.

**Tasks**:
- [ ] **Add badges at top**:
  ```markdown
  [![PyPI version](https://badge.fury.io/py/agency-toolkit.svg)](https://pypi.org/project/agency-toolkit/)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Tests](https://github.com/USER/agency-toolkit/workflows/tests/badge.svg)](https://github.com/USER/agency-toolkit/actions)
  [![Coverage](https://codecov.io/gh/USER/agency-toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/USER/agency-toolkit)
  ```
- [ ] **Add "Features" section with emojis**:
  ```markdown
  ## ✨ Features
  - 🎨 **Social Media Automation**: Generate branded posts at scale
  - 📋 **Project Briefs**: Interactive PDF generation
  - 🏗️ **Folder Structures**: Template-based project setup
  - 🤖 **AI Integration**: Mistral, Google, Ollama support
  - 🔄 **Workflow Orchestration**: JSON-defined task chains
  ```
- [ ] **Add "Quick Start" with 30-second example**:
  ```markdown
  ## 🚀 Quick Start
  ```bash
  pip install agency-toolkit
  toolkit social "Launch Day! 🚀" --style bold --color gradient
  # Creates social_post.png in current directory
  ```
  ```
- [ ] **Add "Architecture" diagram** (ASCII or link to image):
  ```
  User → CLI (commands/) → Core (core/) → Providers (providers/)
                              ↓
                         Orchestrator (os)
                              ↓
                         Task Handlers (tasks/)
  ```
- [ ] **Add "Contributing" section**
- [ ] **Add "License" section** (MIT? Apache 2.0?)

**Exit Criteria**:
- ✅ README has badges, features, quick start
- ✅ 5-minute read gives full understanding
- ✅ Links all work

---

#### Story 3.3.5: Add License & Code of Conduct (1 hour)
**Why**: Required for PyPI and professional OSS projects.

**Tasks**:
- [ ] **Choose license**:
  - Recommended: MIT (most permissive)
  - Alternative: Apache 2.0 (patent protection)
- [ ] **Add `LICENSE` file** to project root
- [ ] **Update `pyproject.toml`**:
  ```toml
  [project]
  license = {text = "MIT"}
  ```
- [ ] **Add `CODE_OF_CONDUCT.md`** (use Contributor Covenant template)
- [ ] **Add `CONTRIBUTING.md`**:
  - How to set up dev environment
  - How to run tests
  - How to submit PRs

**Exit Criteria**:
- ✅ LICENSE file exists
- ✅ CODE_OF_CONDUCT.md exists
- ✅ CONTRIBUTING.md exists

---

### Epic 3.4: CI/CD Pipeline 🔄
**Why**: Automated testing and releases prevent human error.

#### Story 3.4.1: GitHub Actions for Tests (2 hours)
**Tasks**:
- [ ] Create `.github/workflows/tests.yml`:
  ```yaml
  name: Tests
  on: [push, pull_request]

  jobs:
    test:
      runs-on: ubuntu-latest
      strategy:
        matrix:
          python-version: ["3.10", "3.11", "3.12"]

      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v4
          with:
            python-version: ${{ matrix.python-version }}
        - run: pip install -e ".[dev]"
        - run: pytest --cov=agency_toolkit --cov-report=xml
        - uses: codecov/codecov-action@v3
          if: matrix.python-version == '3.11'
  ```
- [ ] Create `.github/workflows/lint.yml`:
  ```yaml
  name: Lint
  on: [push, pull_request]

  jobs:
    lint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v4
        - run: pip install ruff mypy
        - run: ruff check .
        - run: mypy agency_toolkit/
  ```

**Exit Criteria**:
- ✅ Tests run on every push
- ✅ Coverage uploaded to codecov.io
- ✅ Lint checks pass

---

#### Story 3.4.2: Automated Releases (3 hours)
**Tasks**:
- [ ] Create `.github/workflows/release.yml`:
  ```yaml
  name: Release
  on:
    push:
      tags:
        - 'v*'

  jobs:
    release:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v4
        - run: pip install build twine
        - run: python -m build
        - run: twine upload dist/* -u __token__ -p ${{ secrets.PYPI_TOKEN }}
        - uses: softprops/action-gh-release@v1
          with:
            generate_release_notes: true
  ```
- [ ] **Test with Test PyPI first**:
  ```bash
  python -m build
  twine upload --repository testpypi dist/*
  pip install -i https://test.pypi.org/simple/ agency-toolkit
  ```
- [ ] **Create release checklist** in `RELEASING.md`:
  ```markdown
  1. Update version in pyproject.toml
  2. Update CHANGELOG.md
  3. Run: git tag v0.3.0
  4. Run: git push origin v0.3.0
  5. Watch GitHub Actions deploy
  6. Verify on PyPI
  ```

**Exit Criteria**:
- ✅ Tagging releases auto-publishes to PyPI
- ✅ GitHub Releases auto-generated
- ✅ Tested on Test PyPI first

---

### Epic 3.5: Final Documentation 📚

#### Story 3.5.1: Complete API Docs (4 hours)
**Tasks**:
- [ ] **Set up Sphinx**:
  ```bash
  pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
  sphinx-quickstart docs/
  ```
- [ ] Configure `docs/conf.py`:
  ```python
  extensions = [
      'sphinx.ext.autodoc',
      'sphinx.ext.napoleon',  # Google/NumPy docstring support
      'sphinx_autodoc_typehints',
  ]
  html_theme = 'sphinx_rtd_theme'
  ```
- [ ] **Auto-generate module docs**:
  ```bash
  sphinx-apidoc -o docs/api agency_toolkit/
  ```
- [ ] **Deploy to GitHub Pages**:
  ```yaml
  # .github/workflows/docs.yml
  - run: sphinx-build docs/ docs/_build/html
  - uses: peaceiris/actions-gh-pages@v3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      publish_dir: ./docs/_build/html
  ```

**Exit Criteria**:
- ✅ Full API docs at `https://USER.github.io/agency-toolkit/`
- ✅ Auto-updated on every push to main

---

#### Story 3.5.2: Create Example Workflows (3 hours)
**Why**: Show real-world usage, not just CLI reference.

**Tasks**:
- [ ] **Create `examples/` directory structure**:
  ```
  examples/
  ├── 01-simple-social/
  │   ├── README.md
  │   ├── input.json
  │   ├── run.sh
  │   └── expected/social_post.png
  ├── 02-batch-campaign/
  │   ├── README.md
  │   ├── campaign.csv
  │   └── run.sh
  ├── 03-workflow-demo/
  │   ├── README.md
  │   ├── workflow.json
  │   └── run.sh
  ```
- [ ] **Each example must**:
  - Have a 1-paragraph README
  - Include all input files
  - Have a `run.sh` that works out-of-box
  - Show expected output
- [ ] **Add to main README**:
  ```markdown
  ## 📚 Examples
  See the `examples/` directory for complete tutorials:
  - [Simple Social Post](examples/01-simple-social/)
  - [Batch Campaign](examples/02-batch-campaign/)
  - [Workflow Demo](examples/03-workflow-demo/)
  ```

**Exit Criteria**:
- ✅ 3 working examples
- ✅ User can run any example in <2 minutes

---

## PHASE 4: PRODUCTION QUALITY ASSURANCE 🏆
**Objective**: Guarantee enterprise-grade reliability. Data-driven validation. Zero surprises in production.

### Epic 4.0: Comprehensive Testing Strategy
**Why**: Agencies will fire the tool after ONE bad experience. Need bulletproof reliability with measurable quality metrics.

---

#### Story 4.0.1: Real-World Integration Tests (6 hours) 🎯
**Why**: Unit tests are not enough. Need to test actual workflows end-to-end like a real user would.

**Tasks**:
- [ ] **Create `tests/integration/` directory**
- [ ] **Test 1: Full Social Campaign** (tests/integration/test_social_campaign.py):
  ```python
  def test_50_post_batch_campaign():
      """Generate 50 diverse social posts with different styles/colors.
      Verify: All files created, correct dimensions, no crashes."""
      batch_data = [
          {"text": f"Post {i}", "style": random.choice(STYLES)}
          for i in range(50)
      ]
      result = run_batch(batch_data)
      assert len(result.successful) == 50
      assert len(result.failed) == 0
      # Verify all files exist and are valid PNGs
      for path in result.output_files:
          assert path.exists()
          assert is_valid_image(path)
  ```
- [ ] **Test 2: Full Workflow Orchestration** (tests/integration/test_workflow_e2e.py):
  ```python
  def test_multi_module_workflow_with_ai():
      """Run a 3-module workflow that uses AI, social, and briefing.
      Verify: All modules execute in order, context passing works."""
      workflow = load_workflow("examples/workflows/full-campaign.json")
      report = execute_workflow(workflow)

      assert report.total_modules == 3
      assert report.successful_modules == 3
      assert report.failed_modules == 0

      # Verify AI output was used in social post
      assert "ai_tagline" in report.context
      assert Path("output/social_post_1.png").exists()
  ```
- [ ] **Test 3: Error Recovery** (tests/integration/test_error_handling.py):
  ```python
  def test_workflow_continues_after_non_critical_failure():
      """Task 2 fails with on_error: continue. Workflow completes."""
      workflow_with_failing_task = {...}
      report = execute_workflow(workflow_with_failing_task)

      assert report.successful == 4
      assert report.failed == 1
      assert report.skipped == 0
      assert "Task 2 failed but continued" in report.warnings
  ```
- [ ] **Test 4: Performance Benchmarks** (tests/integration/test_performance.py):
  ```python
  @pytest.mark.benchmark
  def test_100_posts_under_5_minutes():
      """100-post batch must complete in <5 minutes."""
      start = time.time()
      result = generate_batch(100)
      duration = time.time() - start

      assert duration < 300  # 5 minutes
      assert result.successful == 100
  ```

**Exit Criteria**:
- ✅ 4 integration tests covering real scenarios
- ✅ All tests pass on clean environment
- ✅ Performance benchmarks documented

**CLI Agent Prompt**:
```
Create integration tests in tests/integration/:
1. test_social_campaign.py - 50-post batch with all styles
2. test_workflow_e2e.py - Full 3-module workflow
3. test_error_handling.py - Graceful failure recovery
4. test_performance.py - 100-post benchmark (must finish <5 min)

Use real config, real API calls (or mocked if expensive).
Run: pytest tests/integration/ -v --durations=10
```

---

#### Story 4.0.2: Data-Driven Quality Metrics (4 hours) 📊
**Why**: Need objective proof the tool is production-ready. Agencies want metrics, not promises.

**Tasks**:
- [ ] **Add quality dashboard in CI**:
  ```yaml
  # .github/workflows/quality.yml
  name: Quality Dashboard
  on: [push]

  jobs:
    quality:
      steps:
        - name: Run pytest with metrics
          run: |
            pytest --cov --cov-report=json --json-report

        - name: Calculate quality score
          run: python scripts/calculate_quality_score.py

        - name: Post to PR comment
          uses: actions/github-script@v6
          with:
            script: |
              const score = JSON.parse(fs.readFileSync('quality_score.json'));
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                body: `## Quality Score: ${score.total}/100
                - Coverage: ${score.coverage}%
                - Test Pass Rate: ${score.pass_rate}%
                - Performance: ${score.performance_score}/25
                - Code Quality: ${score.code_quality}/25`
              })
  ```
- [ ] **Create `scripts/calculate_quality_score.py`**:
  ```python
  def calculate_quality_score():
      """Generate a 0-100 quality score based on:
      - Test coverage (0-25 points)
      - Test pass rate (0-25 points)
      - Performance benchmarks (0-25 points)
      - Static analysis (0-25 points)
      """
      coverage = get_coverage_percentage()
      pass_rate = get_test_pass_rate()
      perf = get_performance_score()
      quality = get_code_quality_score()

      total = (
          min(coverage, 100) * 0.25 +
          pass_rate * 0.25 +
          perf +
          quality
      )

      return {
          "total": round(total, 1),
          "coverage": coverage,
          "pass_rate": pass_rate,
          "performance_score": perf,
          "code_quality": quality,
          "threshold": 80,  # Minimum for production
          "passed": total >= 80
      }
  ```
- [ ] **Add quality gates**:
  ```yaml
  # Block merges if score < 80
  - name: Check quality threshold
    run: |
      SCORE=$(jq .total quality_score.json)
      if (( $(echo "$SCORE < 80" | bc -l) )); then
        echo "Quality score $SCORE below threshold 80"
        exit 1
      fi
  ```
- [ ] **Generate HTML report** (with charts):
  ```bash
  pytest --html=report.html --self-contained-html
  ```

**Exit Criteria**:
- ✅ Quality score calculated on every commit
- ✅ Score visible in PR comments
- ✅ Merges blocked if score < 80
- ✅ HTML report with graphs

**CLI Agent Prompt**:
```
Create a data-driven quality system:
1. Create scripts/calculate_quality_score.py with 4 metrics
2. Add .github/workflows/quality.yml that runs on every push
3. Post quality score as PR comment
4. Block merges if score < 80/100
5. Generate HTML report with pytest-html

Quality = (Coverage×0.25 + PassRate×0.25 + Performance×0.25 + CodeQuality×0.25)
```

---

#### Story 4.0.3: Chaos Testing (3 hours) 💥
**Why**: Real users do unexpected things. Test the tool's resilience to edge cases and bad inputs.

**Tasks**:
- [ ] **Create `tests/chaos/` directory**
- [ ] **Test 1: Malformed Inputs**:
  ```python
  def test_social_with_emoji_overflow():
      """10,000 emojis should gracefully error, not crash."""
      text = "🎉" * 10000
      with pytest.raises(ValidationError, match="Text too long"):
          generate_social(text)

  def test_workflow_with_circular_dependencies():
      """Circular deps should be caught, not infinite loop."""
      workflow = {
          "modules": [
              {"id": "A", "dependencies": ["B"]},
              {"id": "B", "dependencies": ["A"]}
          ]
      }
      with pytest.raises(CircularDependencyError):
          execute_workflow(workflow)
  ```
- [ ] **Test 2: Resource Exhaustion**:
  ```python
  def test_1000_post_batch_doesnt_oom():
      """1000 posts should stream, not load all in memory."""
      # Monitor memory usage
      import psutil
      process = psutil.Process()
      initial_mem = process.memory_info().rss / 1024 / 1024  # MB

      generate_batch(1000)

      final_mem = process.memory_info().rss / 1024 / 1024
      mem_increase = final_mem - initial_mem

      assert mem_increase < 500  # Should not use >500MB extra
  ```
- [ ] **Test 3: Network Failures**:
  ```python
  @patch('providers.mistral_provider.MistralProvider.generate')
  def test_ai_provider_timeout_retries(mock_generate):
      """AI timeout should retry 3 times, then fail gracefully."""
      mock_generate.side_effect = TimeoutError()

      with pytest.raises(ProviderError, match="Failed after 3 retries"):
          generate_ai_text("Hello")

      assert mock_generate.call_count == 3
  ```
- [ ] **Test 4: Filesystem Issues**:
  ```python
  def test_readonly_output_dir_fails_gracefully():
      """If output dir is read-only, show clear error."""
      os.chmod("output/", 0o444)  # Make read-only

      with pytest.raises(PermissionError, match="Cannot write to"):
          generate_social("test")
  ```

**Exit Criteria**:
- ✅ 10+ chaos tests covering edge cases
- ✅ All fail gracefully with clear errors
- ✅ No crashes, hangs, or OOM

**CLI Agent Prompt**:
```
Create chaos tests in tests/chaos/:
1. Malformed inputs (10k emojis, circular deps)
2. Resource exhaustion (1000 posts, memory check)
3. Network failures (timeout retries)
4. Filesystem issues (read-only dirs)

Every test must verify graceful failure, not crashes.
Run: pytest tests/chaos/ -v -x
```

---

#### Story 4.0.4: User Acceptance Testing (UAT) Scenarios (4 hours) 👥
**Why**: Technical tests aren't enough. Need to validate actual user workflows.

**Tasks**:
- [ ] **Create `tests/uat/` directory with real scenarios**
- [ ] **Scenario 1: Agency Onboards New Client** (tests/uat/test_onboarding.py):
  ```python
  def test_complete_onboarding_workflow():
      """
      User story: "As an agency, I want to onboard a new restaurant
      client and generate their first 30 days of content."

      Steps:
      1. Create project structure
      2. Generate briefing PDF
      3. Run workflow to create 30 social posts
      4. Verify all deliverables exist
      """
      # Step 1: Structure
      run_cli("toolkit structure 'Pasta Palace' 'Brand Launch'")
      assert Path("output/Pasta_Palace/Brand_Launch").exists()

      # Step 2: Briefing
      run_cli("toolkit briefing --type restaurant --format pdf")
      assert Path("output/briefing_Pasta_Palace.pdf").exists()

      # Step 3: Workflow
      run_cli("toolkit os init --from-json scenarios/restaurant_30day.json")

      # Verify: 30 posts created
      posts = list(Path("output/social/").glob("*.png"))
      assert len(posts) == 30

      # Verify: All different (no duplicates)
      hashes = [hash_file(p) for p in posts]
      assert len(set(hashes)) == 30
  ```
- [ ] **Scenario 2: Batch Campaign Generation** (tests/uat/test_batch_campaign.py):
  ```python
  def test_csv_to_100_posts_in_5_minutes():
      """
      User story: "As a social media manager, I want to upload a CSV
      with 100 post ideas and get all images in under 5 minutes."
      """
      csv_path = "tests/fixtures/campaign_100.csv"

      start = time.time()
      run_cli(f"toolkit social batch {csv_path}")
      duration = time.time() - start

      assert duration < 300  # 5 minutes

      # Verify: All posts exist and are valid
      posts = list(Path("output/").glob("*.png"))
      assert len(posts) == 100

      for post in posts:
          img = Image.open(post)
          assert img.size in [(1080, 1080), (1080, 1920)]  # Valid sizes
  ```
- [ ] **Scenario 3: Error Recovery** (tests/uat/test_error_recovery.py):
  ```python
  def test_workflow_partial_failure_continues():
      """
      User story: "If the AI provider times out on post #50,
      I still want the other 49 posts to complete."
      """
      # Workflow with 50 tasks, task #25 will fail
      workflow = create_workflow_with_failing_task(25)

      report = execute_workflow(workflow)

      # Verify: 49 successful, 1 failed
      assert report.successful == 49
      assert report.failed == 1

      # Verify: Clear error message
      assert "Task 25 failed: API timeout" in report.errors[0]

      # Verify: User gets partial results
      posts = list(Path("output/").glob("*.png"))
      assert len(posts) == 49
  ```
- [ ] **Scenario 4: Agency Handoff** (tests/uat/test_agency_handoff.py):
  ```python
  def test_export_workflow_for_client_handoff():
      """
      User story: "After creating content, I want to export a ZIP
      with all files + a summary PDF for my client."
      """
      # Generate content
      run_cli("toolkit os init --from-json scenarios/client_handoff.json")

      # Export deliverables
      run_cli("toolkit export --output client_deliverable.zip")

      # Verify ZIP contents
      with zipfile.ZipFile("client_deliverable.zip") as z:
          files = z.namelist()
          assert "summary.pdf" in files
          assert "social_posts/post_001.png" in files
          assert len([f for f in files if f.endswith('.png')]) == 30
  ```

**Exit Criteria**:
- ✅ 4 UAT scenarios pass
- ✅ Each scenario represents a real agency workflow
- ✅ All scenarios complete successfully from scratch

**CLI Agent Prompt**:
```
Create UAT scenarios in tests/uat/ representing real agency workflows:
1. Full client onboarding (structure + briefing + 30 posts)
2. CSV batch campaign (100 posts in <5 min)
3. Partial failure recovery (49/50 posts succeed)
4. Client deliverable export (ZIP with summary)

Each test must run CLI commands directly, not call Python functions.
Use subprocess.run() to execute 'toolkit' commands.
```

---

#### Story 4.0.5: Load Testing & Performance Baselines (3 hours) ⚡
**Why**: Agencies need predictable performance. Establish measurable SLOs.

**Tasks**:
- [ ] **Create `tests/performance/` directory**
- [ ] **Test 1: Throughput Benchmarks**:
  ```python
  @pytest.mark.benchmark(group="throughput")
  def test_social_generation_throughput(benchmark):
      """Measure posts/second. Target: >10 posts/sec."""
      def generate_10_posts():
          for i in range(10):
              generate_social(f"Post {i}", style="minimal")

      result = benchmark(generate_10_posts)

      posts_per_sec = 10 / result.stats.mean
      assert posts_per_sec >= 10, f"Only {posts_per_sec:.1f} posts/sec"
  ```
- [ ] **Test 2: Latency Benchmarks**:
  ```python
  def test_p95_latency_under_2_seconds():
      """95th percentile latency must be <2s per post."""
      latencies = []

      for i in range(100):
          start = time.time()
          generate_social(f"Post {i}")
          latencies.append(time.time() - start)

      p95 = np.percentile(latencies, 95)
      assert p95 < 2.0, f"P95 latency: {p95:.2f}s"
  ```
- [ ] **Test 3: Memory Efficiency**:
  ```python
  def test_batch_generation_constant_memory():
      """Memory usage should not grow linearly with batch size."""
      import tracemalloc

      tracemalloc.start()
      baseline = tracemalloc.get_traced_memory()[0]

      # Generate 1000 posts
      generate_batch(1000)

      current, peak = tracemalloc.get_traced_memory()
      tracemalloc.stop()

      memory_increase = (peak - baseline) / 1024 / 1024  # MB
      assert memory_increase < 100, f"Used {memory_increase:.1f}MB"
  ```
- [ ] **Document SLOs in README**:
  ```markdown
  ## Performance SLOs

  | Metric | Target | Measured |
  |--------|--------|----------|
  | Throughput | >10 posts/sec | 12.3 posts/sec |
  | P95 Latency | <2s | 1.8s |
  | Memory (1000 posts) | <100MB | 87MB |
  | 100-post batch | <5 min | 4m 23s |
  ```

**Exit Criteria**:
- ✅ Performance baselines established
- ✅ All SLOs documented
- ✅ CI fails if performance regresses >10%

**CLI Agent Prompt**:
```
Create performance tests in tests/performance/:
1. Throughput: Measure posts/second (target: >10)
2. Latency: P95 under 2 seconds
3. Memory: Constant usage for large batches
4. Document SLOs in README with actual measurements

Use pytest-benchmark for timing.
Run: pytest tests/performance/ --benchmark-only
```

---

#### Story 4.0.6: Security Audit (2 hours) 🔒
**Why**: Agencies handle sensitive client data. Need verifiable security posture.

**Tasks**:
- [ ] **Run security scanners**:
  ```bash
  # Dependency vulnerabilities
  pip-audit --fix

  # Code vulnerabilities
  bandit -r agency_toolkit/ -ll

  # Secret detection
  gitleaks detect --source . --verbose
  ```
- [ ] **Create `SECURITY.md`**:
  ```markdown
  # Security Policy

  ## Supported Versions
  | Version | Supported |
  |---------|-----------|
  | 0.3.x   | ✅        |
  | < 0.3   | ❌        |

  ## Reporting Vulnerabilities
  Email: security@yourdomain.com

  ## Security Measures
  - All dependencies scanned with pip-audit
  - Static analysis with Bandit
  - No secrets in code (checked with gitleaks)
  - API keys via environment variables only

  ## Compliance
  - GDPR: No PII stored or transmitted
  - SOC2: Audit logs available
  ```
- [ ] **Add security CI check**:
  ```yaml
  # .github/workflows/security.yml
  name: Security Scan
  on: [push, pull_request]

  jobs:
    security:
      steps:
        - run: pip install pip-audit bandit
        - run: pip-audit --strict
        - run: bandit -r agency_toolkit/ -ll -f json -o bandit.json
        - name: Upload results
          uses: github/codeql-action/upload-sarif@v2
          with:
            sarif_file: bandit.json
  ```

**Exit Criteria**:
- ✅ pip-audit clean
- ✅ bandit reports 0 high/critical issues
- ✅ SECURITY.md exists
- ✅ Security scan runs on every PR

---

#### Story 4.0.7: Final Quality Gate (2 hours) 🚦
**Why**: One final checklist before release. No compromises.

**Tasks**:
- [ ] **Create `scripts/quality_gate.py`**:
  ```python
  def run_quality_gate():
      """
      Run all quality checks. Exit 1 if any fail.

      Checks:
      1. All tests pass (unit, integration, UAT, chaos)
      2. Coverage >75%
      3. Quality score >80
      4. Performance SLOs met
      5. Security scans clean
      6. Documentation complete
      7. Examples work
      """
      checks = [
          check_tests(),
          check_coverage(),
          check_quality_score(),
          check_performance(),
          check_security(),
          check_docs(),
          check_examples()
      ]

      print("\n=== QUALITY GATE RESULTS ===")
      for check in checks:
          icon = "✅" if check.passed else "❌"
          print(f"{icon} {check.name}: {check.message}")

      if not all(c.passed for c in checks):
          print("\n🚨 QUALITY GATE FAILED")
          sys.exit(1)

      print("\n🎉 QUALITY GATE PASSED - READY FOR RELEASE")
  ```
- [ ] **Add to release workflow**:
  ```yaml
  # .github/workflows/release.yml
  jobs:
    release:
      steps:
        - name: Quality Gate
          run: python scripts/quality_gate.py

        - name: Build
          if: success()
          run: python -m build
  ```

**Exit Criteria**:
- ✅ Quality gate script exists
- ✅ Runs automatically before release
- ✅ Blocks release if any check fails

---

## PHASE 5: RELEASE PREPARATION 🚀

### Epic 4.1: PyPI Release Checklist

#### Story 4.1.1: Version & Changelog (1 hour)
**Tasks**:
- [ ] **Create `CHANGELOG.md`**:
  ```markdown
  # Changelog

  ## [0.3.0] - 2025-11-XX
  ### Added
  - Workflow orchestration engine with full test coverage
  - JSON schema validation for workflows
  - Progress bars and structured logging
  - Error handling with retry support

  ### Fixed
  - Type errors in Reporter dependency injection
  - Security vulnerabilities (3/4 CVEs resolved)

  ### Changed
  - Refactored os.py (CC 17 → 3)
  - Improved error messages across all commands
  ```
- [ ] **Update version in `pyproject.toml`**:
  ```toml
  version = "0.3.0"
  ```
- [ ] **Tag release**:
  ```bash
  git tag -a v0.3.0 -m "Release v0.3.0: Workflow Engine Stabilization"
  git push origin v0.3.0
  ```

---

#### Story 4.1.2: Test PyPI Upload (1 hour)
**Tasks**:
- [ ] **Build package**:
  ```bash
  python -m build
  ls dist/  # Should see .tar.gz and .whl
  ```
- [ ] **Upload to Test PyPI**:
  ```bash
  twine upload --repository testpypi dist/*
  ```
- [ ] **Test install from Test PyPI**:
  ```bash
  pip install -i https://test.pypi.org/simple/ agency-toolkit==0.3.0
  toolkit --version  # Verify it works
  ```
- [ ] **Verify metadata**:
  - Check PyPI page formatting
  - Verify README renders correctly
  - Check all classifiers

**Exit Criteria**:
- ✅ Package installs from Test PyPI
- ✅ All commands work
- ✅ PyPI page looks good

---

#### Story 4.1.3: Production PyPI Release (30 minutes)
**Tasks**:
- [ ] **Upload to real PyPI**:
  ```bash
  twine upload dist/*
  ```
- [ ] **Verify on PyPI**:
  - Visit https://pypi.org/project/agency-toolkit/
  - Test install: `pip install agency-toolkit`
- [ ] **Announce release**:
  - GitHub Release with changelog
  - Update README with PyPI badge
  - Tweet/LinkedIn post (optional)

**Exit Criteria**:
- ✅ `pip install agency-toolkit` works globally
- ✅ GitHub Release published
- ✅ All badges green

---

## 📊 COMPLETE TIMELINE OVERVIEW

| Week | Phase | Key Deliverables | Hours |
|------|-------|------------------|-------|
| **Week 2** | Workflow Engine (Epic 2.5) | Tests, Observability, Error Handling, Validation, Docs | 28h |
| **Week 3 (Days 1-2)** | Quality Assurance (Epic 4.0) | Integration tests, Chaos testing, UAT, Performance, Security | 24h |
| **Week 3 (Days 3-4)** | Cleanup (Epic 3.3) | Code audit, deps, pre-commit, README, license | 12h |
| **Week 3 (Days 4-5)** | CI/CD (Epic 3.4) | GitHub Actions, automated releases | 5h |
| **Week 3 (Day 5)** | Documentation (Epic 3.5) | Sphinx, examples | 7h |
| **Week 4 (Final)** | Release (Epic 4.1) | PyPI upload, announcements | 2.5h |
| **TOTAL** | | | **78.5h ≈ 10 days** |

---

## 🎯 YOUR IMMEDIATE NEXT STEP

**Paste this into your CLI agent RIGHT NOW:**

```bash
Start Story 2.5.1: Write comprehensive tests for core/orchestrator.py.

Priority tests:
1. Basic 3-task execution chain
2. Template substitution with {placeholders}
3. CRITICAL: Verify step_context converts lists to comma-separated strings, raw_context preserves lists as-is
4. Error propagation when task 2 of 5 fails
5. Module dependency ordering via dependency_resolver

Create tests/core/test_orchestrator.py. Use pytest fixtures for minimal test workflows.
Target: 80%+ coverage of core/orchestrator.py

Run after each test: pytest tests/core/test_orchestrator.py -xvs --cov=agency_toolkit/core/orchestrator.py --cov-report=term-missing
```

---

## FINAL CHECKLIST BEFORE v0.3.0 RELEASE ✅

### 🧪 Testing (Epic 4.0)
- [ ] All unit tests passing (350+)
- [ ] Integration tests passing (4 scenarios)
- [ ] UAT scenarios passing (4 workflows)
- [ ] Chaos tests passing (10+ edge cases)
- [ ] Performance benchmarks met (SLOs documented)
- [ ] Security scans clean (pip-audit, bandit)
- [ ] Quality score ≥80/100

### 📊 Metrics & Observability
- [ ] Test coverage >75%
- [ ] Quality dashboard in CI
- [ ] Performance baselines documented
- [ ] SLOs published in README

### 🧹 Code Quality (Epic 3.3)
- [ ] 0 TODO/FIXME comments
- [ ] All docstrings complete (Google style)
- [ ] mypy --strict passes
- [ ] Pre-commit hooks working
- [ ] 0 dead code (vulture clean)

### 📦 Distribution (Epic 3.4)
- [ ] GitHub Actions green (tests, lint, quality)
- [ ] Test PyPI upload successful
- [ ] Production PyPI release ready
- [ ] Automated release workflow configured

### 📚 Documentation (Epic 3.5)
- [ ] README polished with badges
- [ ] Sphinx docs deployed to GitHub Pages
- [ ] 3+ working examples with run.sh
- [ ] SECURITY.md complete
- [ ] LICENSE + CODE_OF_CONDUCT added
- [ ] CONTRIBUTING.md exists
- [ ] CHANGELOG.md up-to-date

### 🚦 Quality Gate (Story 4.0.7)
- [ ] Quality gate script passes
- [ ] All 7 gate checks green:
  1. ✅ Tests (unit, integration, UAT, chaos)
  2. ✅ Coverage >75%
  3. ✅ Quality score >80
  4. ✅ Performance SLOs met
  5. ✅ Security scans clean
  6. ✅ Documentation complete
  7. ✅ Examples work

**When all boxes checked: 🎉 PRODUCTION-READY FOR AGENCY USE 🎉**

---

## 🎯 GOLDEN QUALITY DEFINITION

A tool is **Golden Quality** when:

### For Developers:
✅ Test coverage >75% with integration + chaos tests
✅ Quality score >80/100 (measured, not guessed)
✅ All edge cases handled gracefully
✅ Performance benchmarks documented & met
✅ Security posture verified

### For Agencies (End Users):
✅ **No surprises**: Errors are clear, never cryptic
✅ **Predictable**: SLOs published (e.g., "100 posts in <5 min")
✅ **Recoverable**: Partial failures don't lose all work
✅ **Observable**: Progress bars, logs, clear feedback
✅ **Professional**: README, docs, examples all polished

### For Production:
✅ Automated quality gates block bad releases
✅ CI/CD pipeline fully automated
✅ Chaos tests verify resilience
✅ UAT proves real-world workflows work

**This is not "good enough" - this is "agencies trust it with client work."**
