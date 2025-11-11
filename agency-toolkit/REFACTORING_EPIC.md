# 🏗️ AGENCY TOOLKIT - COMPLETE REFACTORING EPIC

**Status:** PLANNING
**Created:** 2025-11-07
**Priority:** CRITICAL
**Estimated Duration:** 4-6 weeks

---

## 📋 EXECUTIVE SUMMARY

This epic addresses the complete overhaul of the `agency_toolkit` codebase to eliminate "AI slop" and establish a maintainable, production-ready architecture. The codebase audit revealed **118 quality issues** including god functions, magic numbers, and inadequate test coverage.

### Key Goals:
1. ✅ **Refactor Core Modules** - Eliminate god functions, extract constants
2. ✅ **Plugin Architecture** - Support multiple image generation providers (Replicate, Pollinations.ai, future: DALL-E, Stability)
3. ✅ **Test Suite Migration** - Replace unreliable tests with CLI-based integration tests
4. ✅ **Code Quality Standards** - Enforce standards via CI/CD

---

## 🎯 SUCCESS CRITERIA

- [ ] All god functions (>50 lines) refactored into single-responsibility functions
- [ ] Zero magic numbers - all hardcoded values moved to constants/config
- [ ] Plugin architecture for image providers (minimum 2 working: Replicate + Pollinations)
- [ ] CLI integration tests with >80% coverage of user workflows
- [ ] CI pipeline enforces quality gates (linting, type checking, tests)
- [ ] All existing features work identically (no breaking changes)
- [ ] **All modules use custom exceptions from `exceptions.py` (no generic Exception throwing)**

---

## 📊 CURRENT STATE AUDIT SUMMARY

**Total Issues:** 118
- **HIGH (9):** God functions >50 lines
- **MEDIUM (95):** Magic numbers, duplication, missing error handling
- **LOW (14):** Unclear variable names

**Worst Offenders:**
1. `social.py::generate_social_post()` - 129 lines, 20+ magic numbers
2. `structure.py::create_folder_structure()` - 114 lines
3. `briefing.py::_write_pdf()` - 94 lines, 31 magic numbers
4. `mistral.py::call_mistral_api()` - 67 lines, 9 parameters

---

## 🏗️ ARCHITECTURE BLUEPRINT

### Current Architecture (BROKEN)
```
agency_toolkit/
├── cli_app.py          # Entry point (recently fixed)
├── commands/           # CLI command handlers
│   ├── social.py       # Direct coupling to social.py
│   ├── image.py        # Direct coupling to image_gen.py
│   └── ...
├── social.py           # 129-line god function
├── image_gen.py        # Hardcoded to Replicate only
├── mistral.py          # God functions, 9 params
└── models.py           # Hardcoded model names
```

### Target Architecture (CLEAN)
```
agency_toolkit/
├── cli_app.py
├── commands/           # Thin CLI handlers
├── core/               # NEW: Business logic layer
│   ├── social/
│   │   ├── generator.py    # Orchestrator
│   │   ├── layout.py       # Layout calculations
│   │   ├── rendering.py    # Image rendering
│   │   └── constants.py    # All magic numbers
│   ├── briefing/
│   │   ├── generator.py
│   │   ├── pdf_writer.py
│   │   └── constants.py
│   └── structure/
│       ├── generator.py
│       └── templates.py
├── providers/          # NEW: Plugin architecture
│   ├── base.py         # Abstract base class
│   ├── replicate.py    # Replicate implementation
│   ├── pollinations.py # Pollinations.ai implementation
│   └── registry.py     # Provider discovery/selection
├── models.py           # Pydantic models (config only)
├── config.py           # Configuration management
└── constants.py        # Global constants
```

---

## 📦 WORK UNITS (EPICS → STORIES → TASKS)

---

## **EPIC 1: FOUNDATION & SETUP**
**Priority:** P0 (BLOCKER)
**Estimated:** 3 days
**Dependencies:** None

### WU-1.1: Create New Architecture Structure
**Story:** As a developer, I need a clean folder structure to organize refactored code

**Tasks:**
- [ ] Create `agency_toolkit/core/` directory
- [ ] Create `agency_toolkit/providers/` directory
- [ ] Create `agency_toolkit/core/social/` subdirectory
- [ ] Create `agency_toolkit/core/briefing/` subdirectory
- [ ] Create `agency_toolkit/core/structure/` subdirectory
- [ ] Create placeholder `__init__.py` files
- [ ] Update `.gitignore` if needed

**Acceptance Criteria:**
- Directory structure matches target architecture
- All imports work (no broken references)

**Agent Execution Plan:**
```bash
# Safe - no code changes, just structure
mkdir -p agency_toolkit/core/{social,briefing,structure}
mkdir -p agency_toolkit/providers
touch agency_toolkit/core/__init__.py
touch agency_toolkit/core/social/__init__.py
touch agency_toolkit/core/briefing/__init__.py
touch agency_toolkit/core/structure/__init__.py
touch agency_toolkit/providers/__init__.py
```

---

### WU-1.2: Extract Constants (Low-Risk Quick Win)
**Story:** As a developer, I need all magic numbers in one place for easy maintenance

**Tasks:**
- [ ] Create `agency_toolkit/constants.py`
- [ ] Create `agency_toolkit/core/social/constants.py`
- [ ] Create `agency_toolkit/core/briefing/constants.py`
- [ ] Extract magic numbers from `social.py` (74 instances)
- [ ] Extract magic numbers from `briefing.py` (31 instances)
- [ ] Extract magic numbers from `config.py` (dimension defaults)
- [ ] Review/expand `exceptions.py` for missing error types
- [ ] Run tests to verify no breakage

**Acceptance Criteria:**
- Zero magic numbers in audit report
- All tests pass
- CLI manual smoke test passes

**Agent Execution Plan:**
```python
# Example for social/constants.py
"""Social media generation constants."""

# Twitter character limits
TWITTER_MAX_CHARS = 280

# Layout dimensions
CORNER_RADIUS = 25
GRADIENT_ANGLE = 90
GRADIENT_SIZE = (540, 540)

# Font sizes (relative to image height)
TITLE_FONT_SIZE_RATIO = 0.16
SUBTITLE_FONT_SIZE_RATIO = 0.04

# ... etc
```

**Validation:**
```bash
python scripts/full_audit.py agency_toolkit | grep "magic_number"
# Should return 0 results
```

---

### WU-1.3: Setup Test Baseline
**Story:** As a developer, I need to know which tests are reliable before refactoring

**Tasks:**
- [ ] Run existing test suite, document results
- [ ] Create `tests/integration/test_cli_baseline.py` with manual verification
- [ ] Test `social generate` command (local rendering)
- [ ] Test `structure` command
- [ ] Test `briefing` command
- [ ] Document which features are currently broken
- [ ] Create test fixtures directory structure

**Acceptance Criteria:**
- Baseline test results documented
- Integration test scaffolding in place
- Know exactly which tests are unreliable

**Agent Execution Plan:**
```bash
# Run and capture baseline
pytest -v > test_baseline_before.txt 2>&1

# Manual CLI tests
python -m agency_toolkit.cli_app social generate "Test" --dry-run
python -m agency_toolkit.cli_app structure "Test Project"
```

---

## **EPIC 2: IMAGE PROVIDER PLUGIN ARCHITECTURE**
**Priority:** P0 (BLOCKER for pollinations.ai)
**Estimated:** 5 days
**Dependencies:** WU-1.1 complete

### WU-2.1: Research Pollinations.ai API
**Story:** As a developer, I need to understand the Pollinations.ai API to implement a provider

**Tasks:**
- [ ] Clone/read https://github.com/pollinations/pollinations docs
- [ ] Identify API endpoints for text-to-image
- [ ] Document request/response format
- [ ] Test API with curl (no auth required per docs)
- [ ] Document rate limits, cost (free tier?)
- [ ] Compare capabilities to Replicate (seed support, dimensions, etc.)
- [ ] Create `docs/pollinations_api_research.md`

**Acceptance Criteria:**
- Can successfully generate image via curl
- API request/response documented
- Know limitations vs Replicate

**Agent Execution Plan:**
```bash
# Test Pollinations API
curl "https://image.pollinations.ai/prompt/A%20beautiful%20sunset" -o test_pollinations.jpg

# Document findings in markdown
```

---

### WU-2.2: Create Provider Base Class
**Story:** As a developer, I need an abstract interface for image providers

**Tasks:**
- [ ] Create `agency_toolkit/providers/base.py`
- [ ] Define `ImageProvider` abstract base class with:
  - `generate(prompt, seed, width, height) -> dict`
  - `estimate_cost() -> float`
  - `supports_seed() -> bool`
  - `max_dimensions() -> tuple`
- [ ] Add type hints and docstrings
- [ ] Create `ProviderRegistry` for dynamic provider loading
- [ ] Add unit tests for registry

**Acceptance Criteria:**
- Abstract class enforces interface
- Registry can register/discover providers
- Type checking passes (mypy)

**Agent Execution Plan:**
```python
# agency_toolkit/providers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Tuple

class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        seed: int | None,
        width: int,
        height: int,
        config
    ) -> Dict[str, Any]:
        """Generate image and return metadata."""
        pass

    @abstractmethod
    def estimate_cost(self) -> float:
        """Return estimated cost in USD."""
        pass

    # ... etc
```

---

### WU-2.3: Refactor Replicate to Plugin
**Story:** As a developer, I need Replicate as a plugin to prove the architecture

**Tasks:**
- [ ] Create `agency_toolkit/providers/replicate.py`
- [ ] Move `_generate_replicate()` logic from `image_gen.py`
- [ ] Implement `ImageProvider` interface
- [ ] Extract Replicate-specific constants
- [ ] Update `image_gen.py` to use plugin registry
- [ ] Add unit tests for Replicate provider
- [ ] Verify existing Replicate functionality works

**Acceptance Criteria:**
- `image generate` command works identically
- No code duplication
- Tests pass

**Agent Execution Plan:**
```python
# agency_toolkit/providers/replicate.py
from .base import ImageProvider

class ReplicateProvider(ImageProvider):
    def generate(self, prompt, seed, width, height, config):
        # Moved from image_gen.py
        ...

# Update image_gen.py
from .providers.registry import get_provider

def generate_image(prompt, provider="replicate", ...):
    provider_instance = get_provider(provider)
    return provider_instance.generate(...)
```

**Validation:**
```bash
python -m agency_toolkit.cli_app image generate "Test" --seed 42
# Should work identically to before
```

---

### WU-2.4: Implement Pollinations.ai Provider
**Story:** As a user, I want to use Pollinations.ai as a free image generation alternative

**Tasks:**
- [ ] Create `agency_toolkit/providers/pollinations.py`
- [ ] Implement `ImageProvider` interface
- [ ] Handle API request/response (likely simple GET/POST)
- [ ] Add seed support if available (or document limitation)
- [ ] Add error handling for rate limits
- [ ] Add unit tests
- [ ] Add integration test
- [ ] Update CLI to support `--provider pollinations`

**Acceptance Criteria:**
- Can generate images via Pollinations
- Error messages are clear
- CLI `--provider` flag works

**Agent Execution Plan:**
```python
# agency_toolkit/providers/pollinations.py
import requests
from .base import ImageProvider

class PollinationsProvider(ImageProvider):
    API_BASE = "https://image.pollinations.ai"

    def generate(self, prompt, seed, width, height, config):
        # Implementation based on research
        url = f"{self.API_BASE}/prompt/{quote(prompt)}"
        params = {"width": width, "height": height}
        if seed and self.supports_seed():
            params["seed"] = seed

        response = requests.get(url, params=params, timeout=30)
        # ... save and return
```

**Validation:**
```bash
python -m agency_toolkit.cli_app image generate "A cat" --provider pollinations
# Should create image in output/images/
```

---

### WU-2.5: Update Configuration Models
**Story:** As a user, I need to configure my preferred image provider

**Tasks:**
- [ ] Update `models.py::ImageGenerationConfig` to support multiple providers
- [ ] Add `provider_configs` dict for provider-specific settings
- [ ] Update `config.toml.example` with provider examples
- [ ] Add validation for provider-specific required fields
- [ ] Update CLI help text to document providers

**Acceptance Criteria:**
- Config validates provider settings
- Example config includes both Replicate and Pollinations
- CLI `--help` shows available providers

---

## **EPIC 3: REFACTOR GOD FUNCTIONS**
**Priority:** P1 (HIGH)
**Estimated:** 7 days
**Dependencies:** WU-1.1, WU-1.2 complete

### WU-3.1: Refactor social.generate_social_post (129 lines)
**Story:** As a maintainer, I need `generate_social_post` broken into testable units

**Current Issues:**
- 129 lines (>50 threshold)
- 7 parameters
- 20+ magic numbers
- Mixed responsibilities: validation, layout, rendering, file I/O

**Target Structure:**
```
core/social/
├── constants.py        # All magic numbers
├── generator.py        # Orchestrator (calls other modules)
├── layout.py           # calculate_layout(), position_text()
├── rendering.py        # draw_gradient(), draw_text(), draw_logo()
├── validators.py       # validate_prompt_length() - raises ConfigurationError
├── exceptions.py       # Module-specific exceptions (or use top-level)
└── __init__.py
```

**Tasks:**
- [ ] Create `core/social/constants.py` (WU-1.2 might do this)
- [ ] Create `core/social/layout.py` with:
  - `calculate_dimensions(format: str) -> tuple`
  - `calculate_text_position(text, font, image_dims) -> tuple`
  - `calculate_gradient_position() -> tuple`
- [ ] Create `core/social/rendering.py` with:
  - `draw_gradient_background(draw, dims, color) -> None`
  - `draw_text_with_shadow(draw, text, position, font) -> None`
  - `draw_logo(image, logo_path, position) -> None`
- [ ] Create `core/social/validators.py` with:
  - `validate_prompt(prompt: str, max_length: int) -> str`
- [ ] Create `core/social/generator.py` (orchestrator):
  - `generate(prompt, style, color, format, ...) -> Path`
  - Calls layout/rendering functions
  - Max 50 lines
- [ ] Update `agency_toolkit/social.py` to import from `core/social/generator`
- [ ] Update `commands/social.py` if needed
- [ ] Add unit tests for each new module
- [ ] Run integration tests

**Acceptance Criteria:**
- No function >50 lines
- Each function has single responsibility
- All tests pass
- CLI works identically
- **All error cases use custom exceptions from `exceptions.py` (no bare Exception)**

**Agent Execution Plan:**
```python
# Example: core/social/layout.py
from .constants import FORMAT_DIMENSIONS

def calculate_dimensions(format: str) -> tuple[int, int]:
    """Calculate image dimensions based on format."""
    return FORMAT_DIMENSIONS.get(format, (1080, 1080))

def calculate_text_position(
    text: str,
    font,
    image_width: int,
    image_height: int
) -> tuple[int, int]:
    """Calculate centered text position."""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (image_width - text_width) // 2
    y = (image_height - text_height) // 2

    return (x, y)
```

**Validation:**
```bash
# Run audit - should show social.py god function resolved
python scripts/full_audit.py agency_toolkit/core/social/

# Manual test
python -m agency_toolkit.cli_app social generate "Test refactor" --style modern
# Should produce identical output to before
```

---

### WU-3.2: Refactor structure.create_folder_structure (114 lines)
**Story:** As a maintainer, I need `create_folder_structure` broken into testable units

**Target Structure:**
```
core/structure/
├── constants.py        # Folder templates
├── generator.py        # Orchestrator
├── templates.py        # get_template_structure()
├── validators.py       # validate_project_name()
└── writer.py           # create_directories(), write_readme()
```

**Tasks:**
- [ ] Create `core/structure/constants.py` with folder template definitions
- [ ] Create `core/structure/templates.py`
- [ ] Create `core/structure/writer.py` for file I/O
- [ ] Create `core/structure/generator.py` (orchestrator, <50 lines)
- [ ] Update `agency_toolkit/structure.py` to delegate
- [ ] Add unit tests
- [ ] Integration test

**Acceptance Criteria:**
- No function >50 lines
- CLI works identically
- Tests pass
- **Error handling uses custom exceptions (OutputPathError, ConfigurationError, etc.)**

---

### WU-3.3: Refactor briefing._write_pdf (94 lines)
**Story:** As a maintainer, I need PDF generation broken into logical units

**Target Structure:**
```
core/briefing/
├── constants.py        # PDF styling constants (31 magic numbers!)
├── generator.py        # Orchestrator
├── pdf_writer.py       # ReportLabWriter class
├── sections.py         # write_header(), write_section(), etc.
└── formatters.py       # format_date(), format_content()
```

**Tasks:**
- [ ] Extract 31 magic numbers to `constants.py`
- [ ] Create `pdf_writer.py` with PDF-specific logic
- [ ] Create `sections.py` for section rendering
- [ ] Refactor `briefing.py` to use new modules
- [ ] Unit tests for each module
- [ ] Integration test

**Acceptance Criteria:**
- Zero magic numbers
- No function >50 lines
- PDF output identical
- **Error handling uses OutputPathError, ConfigurationError from exceptions.py**

---

### WU-3.4: Refactor mistral.py God Functions
**Story:** As a maintainer, I need Mistral API calls refactored

**Issues:**
- `call_mistral_api()` - 67 lines, 6 params
- `query_mistral()` - 64 lines, 8 params

**Target Structure:**
```
core/mistral/
├── constants.py
├── client.py           # MistralClient class
├── validators.py       # validate_model(), validate_params()
└── formatters.py       # format_response()
```

**Tasks:**
- [ ] Create `MistralClient` class to encapsulate API logic
- [ ] Reduce parameter count by using config objects
- [ ] Extract constants
- [ ] Refactor functions to <50 lines
- [ ] Unit tests with mocked API
- [ ] Integration test

**Acceptance Criteria:**
- Functions <50 lines
- <5 parameters per function
- Tests pass
- **API errors raise custom exceptions (create MistralAPIError if needed)**

---

## **EPIC 4: TEST SUITE OVERHAUL**
**Priority:** P1 (HIGH)
**Estimated:** 5 days
**Dependencies:** WU-3.x complete (refactored code in place)

### WU-4.1: Analyze Existing Test Coverage
**Story:** As a QA engineer, I need to know which tests are valuable

**Tasks:**
- [ ] Run `pytest --cov=agency_toolkit --cov-report=html`
- [ ] Document coverage gaps
- [ ] Identify which tests are unit vs integration
- [ ] Identify tests that pass when features are broken (false positives)
- [ ] Create `docs/test_analysis.md`

**Acceptance Criteria:**
- Coverage report generated
- False positive tests identified
- Gaps documented

---

### WU-4.2: Create CLI Integration Test Framework
**Story:** As a developer, I need integration tests that catch real CLI breakage

**Tasks:**
- [ ] Create `tests/integration/conftest.py` with:
  - Temp directory fixture
  - CLI runner fixture (subprocess wrapper)
  - Output verification helpers
- [ ] Create `tests/integration/test_social_cli.py`
  - Test `social generate` creates PNG
  - Test `--dry-run` flag
  - Test error cases (invalid style, etc.)
- [ ] Create `tests/integration/test_image_cli.py`
  - Test with mocked Replicate
  - Test with mocked Pollinations
  - Test provider switching
- [ ] Create `tests/integration/test_structure_cli.py`
  - Test folder creation
  - Test README generation
- [ ] Create `tests/integration/test_briefing_cli.py`
  - Test PDF generation

**Acceptance Criteria:**
- Integration tests run actual CLI commands
- Tests verify file outputs exist and are valid
- Tests catch the bugs that manual testing found

**Agent Execution Plan:**
```python
# tests/integration/conftest.py
import pytest
import subprocess
from pathlib import Path

@pytest.fixture
def cli_runner(tmp_path):
    """Fixture to run CLI commands in temp directory."""
    def run_cli(*args):
        result = subprocess.run(
            ["python", "-m", "agency_toolkit.cli_app", *args],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )
        return result
    return run_cli

@pytest.fixture
def output_dir(tmp_path):
    """Fixture providing clean output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output
```

```python
# tests/integration/test_social_cli.py
def test_social_generate_creates_png(cli_runner, output_dir):
    """Test that social generate creates a PNG file."""
    result = cli_runner(
        "social", "generate", "Test Post",
        "--style", "modern",
        "--format", "square"
    )

    assert result.returncode == 0
    assert (output_dir / "social").exists()

    # Find generated PNG
    pngs = list((output_dir / "social").glob("*.png"))
    assert len(pngs) == 1
    assert pngs[0].stat().st_size > 0  # Not empty
```

---

### WU-4.3: Add Unit Tests for Refactored Modules
**Story:** As a developer, I need unit tests for all new `core/` modules

**Tasks:**
- [ ] `tests/unit/core/social/test_layout.py`
- [ ] `tests/unit/core/social/test_rendering.py`
- [ ] `tests/unit/core/social/test_validators.py`
- [ ] `tests/unit/core/briefing/test_pdf_writer.py`
- [ ] `tests/unit/core/structure/test_templates.py`
- [ ] `tests/unit/providers/test_replicate.py`
- [ ] `tests/unit/providers/test_pollinations.py`
- [ ] `tests/unit/providers/test_registry.py`

**Acceptance Criteria:**
- >80% coverage of new modules
- Tests are fast (<1s total)
- All tests pass

---

### WU-4.4: Remove/Fix Unreliable Tests
**Story:** As a developer, I need to remove tests that provide false confidence

**Tasks:**
- [ ] Review tests identified in WU-4.1
- [ ] Delete or fix tests that pass when features are broken
- [ ] Update `tests/README.md` with testing philosophy
- [ ] Document which scenarios require manual testing

**Acceptance Criteria:**
- Zero false positive tests
- Test suite accurately reflects code health

---

## **EPIC 5: CI/CD & QUALITY GATES**
**Priority:** P2 (MEDIUM)
**Estimated:** 3 days
**Dependencies:** WU-4.x complete

### WU-5.1: Setup Pre-commit Hooks
**Story:** As a developer, I need quality checks before committing

**Tasks:**
- [ ] Install `pre-commit` framework
- [ ] Configure `.pre-commit-config.yaml`:
  - `ruff` (linting)
  - `mypy` (type checking)
  - `black` (formatting)
  - Trailing whitespace check
  - YAML/TOML validation
- [ ] Run on existing code, fix issues
- [ ] Document in `README.md`

**Acceptance Criteria:**
- Pre-commit hooks installed
- All checks pass on current code
- Team can run `pre-commit install`

---

### WU-5.2: Create GitHub Actions Workflow (if using GitHub)
**Story:** As a team, we need automated CI on every PR

**Tasks:**
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add job: lint (ruff, mypy)
- [ ] Add job: test (pytest with coverage)
- [ ] Add job: quality audit (scripts/full_audit.py)
- [ ] Require CI pass before merge
- [ ] Add status badge to README

**Acceptance Criteria:**
- CI runs on every push/PR
- Failed CI blocks merge
- Badge shows build status

---

### WU-5.3: Quality Metrics Dashboard
**Story:** As a maintainer, I want to track code quality over time

**Tasks:**
- [ ] Extend `scripts/full_audit.py` to output JSON
- [ ] Create `scripts/track_quality.py` to log metrics
- [ ] Add to CI to track trends
- [ ] Optional: Setup SonarQube or CodeClimate

**Acceptance Criteria:**
- Can track quality metrics over time
- Regression is visible

---

## **EPIC 6: DOCUMENTATION & POLISH**
**Priority:** P2 (MEDIUM)
**Estimated:** 3 days
**Dependencies:** All above complete

### WU-6.1: Update User Documentation
**Story:** As a user, I need docs that match the refactored code

**Tasks:**
- [ ] Update `README.md` with new architecture
- [ ] Update `CONFIG_REFERENCE.md` for new provider configs
- [ ] Create `docs/PROVIDERS.md` documenting image providers
- [ ] Create `docs/DEVELOPMENT.md` for contributors
- [ ] Add architecture diagram

**Acceptance Criteria:**
- Docs are accurate
- New contributors can understand architecture

---

### WU-6.2: Migration Guide
**Story:** As an existing user, I need to know what changed

**Tasks:**
- [ ] Create `MIGRATION_GUIDE.md`
- [ ] Document config changes
- [ ] Document any CLI flag changes
- [ ] Provide upgrade path

**Acceptance Criteria:**
- Users can upgrade without breaking existing workflows

---

### WU-6.3: Code Comments & Docstrings
**Story:** As a developer, I need inline documentation for complex logic

**Tasks:**
- [ ] Add docstrings to all public functions (Google style)
- [ ] Add comments only where logic is non-obvious
- [ ] Remove redundant comments

**Acceptance Criteria:**
- All public APIs have docstrings
- Comments explain "why" not "what"

---

## 📅 EXECUTION TIMELINE

### **Phase 1: Foundation (Week 1)**
- WU-1.1: Directory structure (Day 1)
- WU-1.2: Extract constants (Day 2-3)
- WU-1.3: Test baseline (Day 4)
- WU-2.1: Pollinations research (Day 5)

### **Phase 2: Plugin Architecture (Week 2)**
- WU-2.2: Base class (Day 1-2)
- WU-2.3: Replicate plugin (Day 2-3)
- WU-2.4: Pollinations plugin (Day 4-5)
- WU-2.5: Config updates (Day 5)

### **Phase 3: God Function Refactoring (Week 3-4)**
- WU-3.1: Refactor social.py (Week 3, Day 1-3)
- WU-3.2: Refactor structure.py (Week 3, Day 4-5)
- WU-3.3: Refactor briefing.py (Week 4, Day 1-2)
- WU-3.4: Refactor mistral.py (Week 4, Day 3-4)

### **Phase 4: Testing (Week 5)**
- WU-4.1: Analyze coverage (Day 1)
- WU-4.2: CLI integration tests (Day 2-3)
- WU-4.3: Unit tests (Day 4-5)
- WU-4.4: Remove bad tests (Day 5)

### **Phase 5: CI & Docs (Week 6)**
- WU-5.1: Pre-commit hooks (Day 1)
- WU-5.2: GitHub Actions (Day 2)
- WU-5.3: Quality dashboard (Day 3)
- WU-6.1: Update docs (Day 4)
- WU-6.2: Migration guide (Day 5)
- WU-6.3: Comments/docstrings (Day 5)

---

## 🚨 RISK MANAGEMENT

### High-Risk Work Units:
- **WU-3.1 (social refactor):** Most complex, highest breakage risk
  - **Mitigation:** Do last in Epic 3, ensure integration tests first
- **WU-2.3 (Replicate plugin):** Breaking existing image generation
  - **Mitigation:** Feature flag to toggle old/new implementation
- **WU-4.4 (remove tests):** Risk of deleting useful tests
  - **Mitigation:** Review with team before deletion

### Rollback Plan:
- Each WU is atomic and can be reverted via git
- Keep `main` branch stable, use feature branches
- Merge only when all tests pass

---

## 🔧 AGENT EXECUTION GUIDELINES

### For Each Work Unit:
1. **Read Context:** Review Epic description and acceptance criteria
2. **Run Baseline:** Test current functionality before changes
3. **Make Changes:** Implement per task list
4. **Validate:** Run audit, tests, manual CLI verification
5. **Document:** Update inline comments if complex logic
6. **Commit:** Small, atomic commits with descriptive messages

### Safe Execution Patterns:
- **Constants extraction:** Low risk, high value
- **New file creation:** Safe (doesn't break existing code)
- **Refactoring with tests:** Medium risk, validate thoroughly
- **Test deletion:** High risk, require human review

### When to Stop and Ask:
- Acceptance criteria unclear
- Tests fail after changes
- Audit shows new issues introduced
- Unclear how to validate changes

---

## ✅ DEFINITION OF DONE (Per Work Unit)

- [ ] All tasks complete
- [ ] Acceptance criteria met
- [ ] Code quality audit passes (no new issues)
- [ ] All tests pass (unit + integration)
- [ ] Manual CLI smoke test passes
- [ ] Code reviewed (if multi-person team)
- [ ] Documentation updated (if user-facing change)
- [ ] Committed to feature branch

---

## 📊 METRICS TO TRACK

- **Code Quality Score:** Track over time via audit script
- **Test Coverage:** Should increase to >80%
- **God Functions:** Should reach zero
- **Magic Numbers:** Should reach zero
- **Build Time:** CI should run in <5 minutes
- **False Positive Tests:** Should reach zero

---

## 🎓 LESSONS LEARNED (Post-Epic Retrospective)

_To be filled after completion_

- What went well?
- What was harder than expected?
- What would we do differently?
- What tools/processes helped most?

---

## 📚 REFERENCES

- [AI Code Quality Standards (YAML)](linked in handover)
- [Pollinations.ai GitHub](https://github.com/pollinations/pollinations)
- [Replicate API Docs](https://replicate.com/docs)
- [Typer CLI Framework](https://typer.tiangolo.com/)
- Project audit report: `scripts/full_audit.py`
- Custom exceptions: `agency_toolkit/exceptions.py`

---

## 🚨 CRITICAL: ERROR HANDLING MANDATE

**All refactored modules MUST use custom exceptions from `exceptions.py`:**

```python
# ✅ CORRECT - Use custom exceptions
from agency_toolkit.exceptions import ConfigurationError, OutputPathError

def validate_format(format: str):
    if format not in VALID_FORMATS:
        raise ConfigurationError(f"Invalid format: {format}")

def create_output_dir(path: Path):
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OutputPathError(f"Cannot create {path}") from e
```

```python
# ❌ WRONG - Generic exceptions
def validate_format(format: str):
    if format not in VALID_FORMATS:
        raise ValueError(f"Invalid format: {format}")  # Too generic!
```

**Existing Custom Exceptions:**
- `TemplateNotFoundError` - Template files missing
- `TemplateValidationError` - JSON Schema validation fails
- `ConfigurationError` - Invalid config values
- `OutputPathError` - Directory creation fails

**New Exceptions Needed (to be added in WU-1.2):**
- `ImageProviderError` - Image generation API failures
- `MistralAPIError` - Mistral API failures
- `RenderingError` - Image rendering failures

---

**END OF EPIC**
