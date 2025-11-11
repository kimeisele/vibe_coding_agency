# Agency Toolkit: Production Hardening Roadmap (Updated)

**Status as of 2025-11-08:**
- ✅ Epic 1 (load_config refactor) COMPLETE
- ✅ Epic 2 (Task handler plugins) COMPLETE
- ✅ Story 1.1.1 (Typer/Reporter fix) COMPLETE
- 📋 Ready to merge to main

---

## PHASE 1: STABILIZE (Week 1) 🚨

### Epic 1.2: Security Vulnerabilities 🔒 **P0 - DO TODAY**
**Why**: 4 critical CVEs are portfolio blockers.

#### Story 1.2.1: Update Vulnerable Packages
**Status**: ⏳ READY TO START (1 hour)

**Tasks**:
```bash
# Update packages
pip install --upgrade \
  brotli>=1.2.0 \
  pdfminer-six>=20251107 \
  starlette>=0.49.1 \
  torch>=2.6.0

# Verify
pip-audit  # Should show 0 vulnerabilities
pytest     # Ensure no regressions

# Update pyproject.toml
# Update dependencies to new minimum versions
```

**Exit Criteria:**
- [ ] `pip-audit` shows 0 vulnerabilities
- [ ] All 264 tests pass
- [ ] `pyproject.toml` updated

**CLI Agent Prompt:**
```
Update dependencies in pyproject.toml to fix CVEs: brotli>=1.2.0, pdfminer-six>=20251107, starlette>=0.49.1, torch>=2.6.0. Run pip install, then pip-audit and pytest to verify. Report results.
```

---

### Epic 1.3: Critical Error Handling 🛡️ **P1**
**Why**: Users are getting cryptic errors.

#### Story 1.3.1: Image Generation Error Handling
**Location**: `agency_toolkit/image_gen.py`
**Time**: 2 hours

**Tasks**:
- [ ] Wrap `provider_instance.generate()` in try/except
- [ ] Catch: `ProviderError`, `httpx.HTTPError`, `httpx.ConnectError`
- [ ] Add retry logic (already exists in decorator, verify it works)
- [ ] Log full error, show user-friendly message
- [ ] Write unit test: mock provider failure

**Exit Criteria:**
- [ ] No unhandled exceptions possible
- [ ] Test `test_image_gen_provider_failure` passes
- [ ] Error message: "Image generation failed: {clear reason}"

**CLI Agent Prompt:**
```
Add error handling to image_gen.py::generate_image(). Catch ProviderError, httpx.HTTPError, and httpx.ConnectError. Provide user-friendly error messages. Write a unit test that mocks provider failure and verifies graceful handling.
```

---

#### Story 1.3.2: AI Command Error Handling
**Location**: `agency_toolkit/commands/ai.py`
**Time**: 2 hours

**Tasks**:
- [ ] Replace `except Exception as e` with specific types
- [ ] Handle: `ProviderError`, `ValidationError`, `FileNotFoundError`, `httpx.HTTPError`
- [ ] Specific user messages for each error type
- [ ] Log full traceback only in debug mode
- [ ] Write unit tests for each error path

**Exit Criteria:**
- [ ] 5 new tests for error paths
- [ ] No generic exceptions
- [ ] All error messages are actionable

**CLI Agent Prompt:**
```
Refactor error handling in commands/ai.py. Replace generic 'except Exception' with specific types: ProviderError, ValidationError, FileNotFoundError, httpx.HTTPError. Add tailored user messages. Write unit tests for all error paths.
```

---

## PHASE 2: ORGANIZE (Week 2) 📁

### Epic 2.1: Centralize AI Prompts 🤖
**Why**: Prompts are hardcoded in config.py (Audit confirms this).

#### Story 2.1.1: Create Prompts System
**Time**: 3 hours

**Tasks**:
- [ ] Create `agency_toolkit/prompts/` directory
- [ ] Create `prompts/profiles/` subdirectory
- [ ] Move all `MISTRAL_PROFILES.system_prompt` to `.txt` files:
  ```
  prompts/profiles/default.txt
  prompts/profiles/code.txt
  prompts/profiles/creative.txt
  prompts/profiles/strategy.txt
  prompts/profiles/client.txt
  prompts/profiles/technical.txt
  ```
- [ ] Create `prompts/loader.py`:
  ```python
  def load_prompt(name: str) -> str:
      """Load prompt from prompts/profiles/{name}.txt"""
      pass
  ```
- [ ] Update `config.py` to use `load_prompt()`
- [ ] Add versioning support: `.latest` symlink

**Exit Criteria:**
- [ ] All prompts externalized
- [ ] config.py has no hardcoded prompt strings
- [ ] Tests pass

**CLI Agent Prompt:**
```
Create a prompts system. Create prompts/profiles/ directory and move all MISTRAL_PROFILES system_prompt strings from config.py into individual .txt files. Create prompts/loader.py with load_prompt() function. Update config.py to load prompts dynamically.
```

---

#### Story 2.1.2: Extract Template Prompts
**Time**: 4 hours

**Tasks**:
- [ ] Audit `core/social/background.py` for AI prompts
- [ ] Create `prompts/templates/` directory
- [ ] Extract prompts to Jinja2 templates:
  ```
  prompts/templates/social_background.jinja2
  ```
- [ ] Template variables: `{{ post_text }}`, `{{ style }}`
- [ ] Document in `prompts/README.md`

**Exit Criteria:**
- [ ] No multi-line prompt strings in source code
- [ ] Templates use Jinja2 variables
- [ ] Documentation exists

**CLI Agent Prompt:**
```
Extract AI prompts from core/social/background.py into Jinja2 templates. Create prompts/templates/ directory. Use template variables like {{ post_text }}. Create prompts/README.md documenting all templates and variables.
```

---

### Epic 2.3: Template Registry 📋
**Time**: 4 hours (defer to v0.3 if needed)

**Tasks**:
- [ ] Create `templates/registry.json` with metadata
- [ ] Create JSON schemas: `schemas/briefing.schema.json`, etc.
- [ ] Add `agency-toolkit templates list` command
- [ ] Validate templates on load

**CLI Agent Prompt:**
```
Create template registry. Add templates/registry.json with metadata for all templates. Create JSON schemas for validation. Add 'templates list' command. Validate templates against schemas on load.
```

---

## PHASE 3: PRODUCTIONIZE (Week 3) 🚀

### Epic 3.1: UX Improvements ✨

#### Story 3.1.1: Progress Indicators
**Time**: 4 hours

**Tasks**:
- [ ] Install `rich` library
- [ ] Add progress bars to:
  - `social batch` (per-image progress)
  - `briefing` (multi-step generation)
  - API calls (spinner during wait)
- [ ] Add ETA calculations
- [ ] Replace `typer.secho` with `rich.console`

**Exit Criteria:**
- [ ] No long-running command is silent
- [ ] Progress bars show ETA
- [ ] User testing confirms improved experience

**CLI Agent Prompt:**
```
Add progress indicators using 'rich' library. Show progress bars for social batch, briefing, and API calls. Include ETAs. Replace typer.secho with rich.console for better formatting.
```

---

### Epic 3.3: Documentation & Examples 📚

#### Story 3.3.2: Cookbook Examples
**Time**: 6 hours

**Tasks**:
- [ ] Create `examples/` directory
- [ ] Create 5 scenarios:
  1. `01_restaurant_campaign/` (briefing + 50 social posts)
  2. `02_product_launch/` (structure + AI content)
  3. `03_client_report/` (briefing + images)
  4. `04_social_media_batch/` (CSV → 100 posts)
  5. `05_grand_agency_workflow/` (full OS workflow)
- [ ] Each has: README.md, input files, expected output, run.sh
- [ ] Add "Examples" section to main README

**Exit Criteria:**
- [ ] All examples run successfully
- [ ] README links to examples
- [ ] Each example is self-contained

**CLI Agent Prompt:**
```
Create examples/ directory with 5 real-world scenario tutorials. Each example needs README, input files, expected output, and run.sh script. Focus on end-to-end workflows demonstrating multiple features.
```

---

### Epic 3.4: Distribution 📦

#### Story 3.4.1: Publish to PyPI
**Time**: 2 hours

**Tasks**:
- [ ] Test build: `python -m build`
- [ ] Create PyPI account + API token
- [ ] Publish to Test PyPI first
- [ ] Verify: `pip install -i https://test.pypi.org/simple/ agency-toolkit`
- [ ] Publish to real PyPI
- [ ] Add badge to README

**Exit Criteria:**
- [ ] `pip install agency-toolkit` works
- [ ] Package on PyPI
- [ ] README has PyPI badge

---

## DELIVERY SCHEDULE (Updated)

| Week | Focus | Deliverable | Hours |
|------|-------|-------------|-------|
| **Week 1** | Security + Error Handling | v0.2.0 (stable + secure) | 5h |
| **Week 2** | Prompts + Organization | v0.2.5 (clean arch) | 7h |
| **Week 3** | UX + Examples + PyPI | v0.3.0 (showcase) | 12h |

**Total Time**: ~24 hours over 3 weeks

---

## WHAT CHANGED FROM ORIGINAL ROADMAP

### ✅ Already Done (Remove from roadmap)
- Story 1.1.1: Typer/Reporter fix
- Epic 1 (entire): load_config refactor
- Epic 2 (entire): Task handler plugin system

### 🔄 Reprioritized
- **Security (1.2.1)**: Now P0 (was "next")
- **Test Coverage (1.4.1)**: Deferred (68% is acceptable)
- **Config Consolidation (2.2)**: Mostly obsolete (Epic 1 covered it)

### 📋 Kept As-Is
- Error handling (1.3)
- Prompts externalization (2.1)
- Template registry (2.3)
- Progress bars (3.1)
- Examples (3.3.2)
- PyPI publish (3.4)

---

## IMMEDIATE ACTION

**Right now:**
```bash
# 1. Merge Epic 1 & 2
git checkout main
git merge epic-1 epic-2
git tag v0.2.0-foundation
git push origin main --tags

# 2. Fix security (Story 1.2.1)
pip install --upgrade brotli>=1.2.0 pdfminer-six>=20251107 starlette>=0.49.1 torch>=2.6.0
pip-audit
pytest
```

**Then:** Start Epic 1.3 (Error Handling)
