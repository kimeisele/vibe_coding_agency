# Epic 8: Production Hardening & Launch Readiness - Refined Scope

**Based on**: Reality Check findings from November 7, 2025
**Status**: Planning Phase (Ready for Implementation)
**Total Estimated Effort**: 7-11 Days
**Critical Success Factor**: WU 8.4 (Documentation) is NON-OPTIONAL

---

## Overview

Epic 8 transforms the toolkit from "functionally complete" to "production-ready" by adding:
1. **Output Quality Validation** (Golden Master snapshots)
2. **Resilience & Error Recovery** (graceful degradation)
3. **Production Observability** (anonymous metrics)
4. **Complete Documentation** (SSOT updates)

---

## WU 8.1: Output Quality Guardian (3-4 Days)

### Goal
Establish automated quality validation for all generated artifacts (PDFs, images, JSON) to prevent regressions and ensure consistent quality.

### Why This Matters (from Reality Check)
- ✅ Code is tested (248 tests passing)
- ❓ But actual artifacts (images, PDFs) quality is not validated
- 🎯 Need "Snapshot Testing" to verify outputs don't degrade

### Part A: Semantic Validation Tests (New: `tests/quality/`)

#### A1: Prompt Quality Validation
**File**: `tests/quality/test_prompt_quality.py`

```python
def test_negative_prompts_present():
    """Ensure all seed templates have negative prompts."""
    # Prevents: Low-quality outputs with unwanted artifacts
    # Example: "blurry", "low res", "ugly" in negative prompt

def test_quality_tags_enforced():
    """Ensure prompts contain professional quality tags."""
    # Required tags: "8k", "high resolution", "masterpiece", "sharp focus"
    # Prevents: Generic, low-quality outputs

def test_no_generic_lazy_descriptors():
    """Ban lazy adjectives without context."""
    # Fails on: "vibrant", "stunning", "amazing" without specifics
    # Allows: "vibrant playful energetic" (specific context)

def test_color_palette_coverage():
    """Ensure seed templates have 3+ distinct colors."""
    # Prevents: Monochromatic, boring color palettes

def test_prompt_length_sufficient():
    """Ensure prompts are detailed enough (min 50 chars)."""
    # Prevents: Lazy short prompts like "nice image"
```

#### A2: Output Structure Validation
**File**: `tests/quality/test_output_contracts.py`

```python
def test_pdf_structure_briefing():
    """Validate PDF has all required sections."""
    # Uses pdfplumber to extract text
    # Ensures: Title, Executive Summary, Sections, Footer present

def test_social_image_dimensions():
    """Validate social post images have correct dimensions."""
    # Checks: Width/height match format (square=1:1, etc.)
    # Uses PIL to verify actual image properties

def test_json_schema_compliance():
    """Validate JSON outputs match expected schema."""
    # Ensures: Keys, types, required fields present
    # Uses: jsonschema library

def test_text_rendering_non_empty():
    """Verify text is actually rendered on images."""
    # Checks: Image has content, not blank
    # Uses: PIL pixel analysis
```

#### A3: Registry Seed Quality (Hardened)
**File**: `tests/quality/test_registry_hardening.py`

```python
def test_seed_templates_have_all_fields():
    """Ensure each seed template has required fields."""
    # Required: name, description, prompt_prefix, mood, color_palette,
    #          best_for, default_seed, negative_prompt (NEW)

def test_negative_prompts_present():
    """Each seed must define what NOT to generate."""
    # Example: "blurry, low res, distorted, ugly, deformed"

def test_mood_consistency():
    """Ensure mood matches prompt and colors."""
    # Moody → dark colors ✓
    # Playful → vibrant colors ✓
    # Corporate → professional colors ✓

def test_no_contradictory_prompts():
    """Ensure prompt and negative_prompt don't contradict."""
    # Example: If prompt says "sharp", negative shouldn't say "sharp focus required"
```

### Part B: Snapshot/Golden Master Workflow

#### Setup
1. **Create directories**:
   ```
   snapshots/
   ├── approved/        # Master (verified good outputs)
   │   ├── social_modern.png
   │   ├── briefing_web.pdf
   │   ├── structure_web.json
   │   └── image_test.jpg
   └── current/         # Latest test run
       ├── (auto-populated by tests)
   ```

2. **Reference Artifacts** (manually created once):
   - `snapshots/approved/social_modern.png` - A "good" modern social post
   - `snapshots/approved/briefing_web.pdf` - A "good" web briefing
   - `snapshots/approved/structure_web.json` - A "good" web structure
   - `snapshots/approved/image_test.jpg` - A "good" generated image

#### New CLI Command: `toolkit validate`

**Feature 1: Snapshot Generation**
```bash
toolkit validate --snapshot
# Generates fresh artifacts in snapshots/current/
# Compares hashes with snapshots/approved/
# Reports: ✓ (unchanged), ⚠️ (changed), ✗ (missing)
```

**Feature 2: Approval/Promotion**
```bash
toolkit validate --approve
# After manual review of snapshots/current/
# Promotes current/ → approved/ (becomes new golden master)
```

**Feature 3: Detailed Report**
```bash
toolkit validate --report
# Shows:
#  - Which files changed
#  - Byte diff for text files
#  - Visual diffs for images (if tooling available)
#  - Git-like format (old vs new)
```

#### Implementation (`agency_toolkit/commands/validate.py`)
```python
@validate_command.command()
def snapshot(ctx):
    """Generate snapshot and compare with approved master."""
    config = ctx.obj

    # 1. Run generators with fixed seeds
    social_result = generate_social_post(..., seed=42)
    briefing_result = generate_briefing(..., seed=42)
    # ...etc

    # 2. Save to snapshots/current/
    shutil.copy(social_result['path'], 'snapshots/current/social_modern.png')
    # ...etc

    # 3. Compare with snapshots/approved/
    # For images: Compare file hashes
    # For PDFs: Extract text and compare
    # For JSON: Compare structure (not formatting)

    # 4. Report differences

@validate_command.command()
def approve(ctx):
    """Promote snapshots/current/ to snapshots/approved/."""
    # After user verifies quality, promote them
```

### Success Criteria for WU 8.1
- ✅ 15+ semantic validation tests in `tests/quality/`
- ✅ `toolkit validate --snapshot` creates artifacts in `snapshots/current/`
- ✅ `toolkit validate --approve` promotes to `snapshots/approved/`
- ✅ `toolkit validate --report` shows diffs
- ✅ CI/CD can run snapshot tests and fail on regressions
- ✅ Documentation in IMPLEMENTATION.yaml updated

---

## WU 8.2: Resilience & Error Recovery (2-3 Days)

### Goal
Handle real-world failures gracefully (API downtime, network errors, missing files) instead of crashing.

### Why This Matters (from Reality Check)
- ✅ Code works in happy path (tests pass)
- ❌ But what if Mistral API is down? Pollinations API is rate-limited? Font is missing?
- 🎯 Need graceful degradation to keep toolkit usable offline

### Part A: Graceful Degradation

#### A1: Provider Fallback
**File**: `agency_toolkit/core/resilience.py` (new)

```python
class ProviderFallback:
    """Implement fallback chain for image generation."""

    @staticmethod
    def generate_with_fallback(prompt, seed, **kwargs):
        """Try providers in order: pollinations → replicate → placeholder"""
        providers = [
            ('pollinations', generate_pollinations),
            ('replicate', generate_replicate),
            ('placeholder', generate_placeholder_image),
        ]

        for provider_name, provider_func in providers:
            try:
                result = provider_func(prompt, seed, **kwargs)
                logger.info(f"Generated image using {provider_name}")
                return result
            except ProviderError as e:
                logger.warning(f"{provider_name} failed: {e}, trying next...")
                continue

        # Last resort: return placeholder
        logger.warning("All providers failed, using placeholder")
        return generate_placeholder_image()

def generate_placeholder_image(width=1024, height=1024):
    """Create a simple placeholder image (never fails)."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text((width//2, height//2), "Image generation unavailable",
              fill=(100, 100, 100), anchor="mm")
    return img
```

#### A2: Font Fallback (Enhancement)
**File**: `agency_toolkit/core/social/rendering.py` (update)

```python
def get_font_with_fallback(font_name, size):
    """Get font with cascading fallback."""
    font_chain = [
        f"agency_toolkit/assets/fonts/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        None,  # PIL default
    ]

    for font_path in font_chain:
        try:
            if font_path is None:
                return ImageFont.load_default()
            return ImageFont.truetype(font_path, size)
        except (FileNotFoundError, OSError):
            continue

    # Absolute fallback
    return ImageFont.load_default()
```

#### A3: Offline Mode
**File**: `agency_toolkit/cli_app.py` (add global flag)

```python
@app.callback()
def main(
    ctx: typer.Context,
    # ... existing options ...
    offline: bool = typer.Option(
        False,
        "--offline",
        help="Disable all network calls, use local-only features"
    ),
):
    """Agency Toolkit with offline mode support."""
    config = load_config()
    config.offline = offline

    if offline:
        logger.warning("⚠️  OFFLINE MODE: Network features disabled")

    ctx.obj = config
```

**Behavior when `--offline` is set**:
- `toolkit structure` ✅ Works (local only)
- `toolkit briefing` ✅ Works (local only)
- `toolkit social` ⚠️ Works (no background image)
- `toolkit image` ❌ Fails gracefully ("Image generation requires network")
- `toolkit ask` ❌ Fails gracefully ("Ask feature requires network")

### Part B: Retry Logic & Exponential Backoff

**File**: `agency_toolkit/core/resilience.py` (add)

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
)
def api_call_with_retry(api_func, *args, **kwargs):
    """Call API with exponential backoff: 2s, 4s, 8s."""
    return api_func(*args, **kwargs)
```

**Usage in Mistral**:
```python
def query_mistral_resilient(prompt, **kwargs):
    """Query Mistral with retry logic."""
    return api_call_with_retry(
        _mistral_client.messages.create,
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
    )
```

### Part C: State Recovery (Bonus)

**File**: `agency_toolkit/core/recovery.py` (new, optional)

```python
def save_state(command: str, args: dict, status: str):
    """Save command state for potential resume."""
    state_file = Path.home() / ".toolkit" / "state.json"
    state_file.parent.mkdir(exist_ok=True)

    state = {
        "command": command,
        "args": args,
        "status": status,  # running, failed, completed
        "timestamp": datetime.now().isoformat(),
    }
    state_file.write_text(json.dumps(state, indent=2))

@app.command()
def resume():
    """Resume a failed command."""
    state_file = Path.home() / ".toolkit" / "state.json"
    if not state_file.exists():
        typer.secho("No incomplete command to resume", fg="yellow")
        return

    state = json.loads(state_file.read_text())
    typer.echo(f"Resuming: {state['command']} {state['args']}")
    # Re-run with same args...
```

### Success Criteria for WU 8.2
- ✅ Provider fallback works (tests with mock failures)
- ✅ Font fallback cascade tested
- ✅ `--offline` flag works correctly
- ✅ Retry logic implemented for API calls
- ✅ Graceful error messages instead of stack traces
- ✅ 10+ resilience tests added
- ✅ IMPLEMENTATION.yaml updated

---

## WU 8.3: Production Observability (1-2 Days)

### Goal
Understand what users use and where failures occur (privacy-first) to guide future development.

### Why This Matters (from Reality Check)
- ✅ Code is tested (248 tests passing)
- ❓ But we don't know: Which commands are most used? Where do users hit errors?
- 🎯 Need metrics to prioritize future work

### Implementation (`agency_toolkit/core/telemetry.py`)

```python
import json
from pathlib import Path
from datetime import datetime

class AnonymousTelemetry:
    """Track only aggregate stats, no user data or prompts."""

    def __init__(self):
        self.metrics_file = Path.home() / ".toolkit" / "metrics.json"
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> dict:
        """Load existing metrics or create new."""
        if self.metrics_file.exists():
            return json.loads(self.metrics_file.read_text())
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "commands": {},
            "errors": {},
        }

    def track_command(self, cmd: str, duration: float, success: bool):
        """Track command execution."""
        if cmd not in self.metrics["commands"]:
            self.metrics["commands"][cmd] = {
                "count": 0,
                "success_count": 0,
                "total_time": 0.0,
            }

        self.metrics["commands"][cmd]["count"] += 1
        self.metrics["commands"][cmd]["total_time"] += duration
        if success:
            self.metrics["commands"][cmd]["success_count"] += 1

        self._save_metrics()

    def track_error(self, error_type: str):
        """Track error occurrences."""
        if error_type not in self.metrics["errors"]:
            self.metrics["errors"][error_type] = 0

        self.metrics["errors"][error_type] += 1
        self._save_metrics()

    def _save_metrics(self):
        """Save metrics to disk."""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.write_text(json.dumps(self.metrics, indent=2))

# Global telemetry instance
_telemetry = AnonymousTelemetry()

def get_telemetry():
    """Get global telemetry instance."""
    return _telemetry
```

### New CLI Commands

#### `toolkit stats`
```bash
$ toolkit stats

📊 Your Toolkit Usage (Local)

Commands Used:
  social:     42 runs (avg 2.3s), 40 successful
  briefing:   15 runs (avg 5.1s), 14 successful
  structure:   8 runs (avg 1.2s), 8 successful
  image:      23 runs (avg 3.4s), 18 successful

Errors Encountered:
  PDFTimeoutError:  3
  APIRateLimited:   2
  MissingFontError: 1

To share anonymous stats with developers: toolkit stats --share
```

#### `toolkit stats --share` (Opt-In)
```bash
$ toolkit stats --share

📤 Sharing anonymous stats with agency-toolkit development...

Data shared:
  ✓ Command usage counts (no details)
  ✓ Error type counts (no stack traces)
  ✓ Your toolkit version
  ✓ Your OS type (Linux/macOS/Windows)

No user data, no prompts, no private information shared.

To review what we collect: https://docs.agency-toolkit.dev/privacy
To disable: toolkit config --no-telemetry
```

### Success Criteria for WU 8.3
- ✅ Telemetry module created with track_command() and track_error()
- ✅ `toolkit stats` displays local metrics
- ✅ `toolkit stats --share` sends with explicit consent
- ✅ Metrics saved to `~/.toolkit/metrics.json`
- ✅ No sensitive data collected (no prompts, no user input)
- ✅ 8+ telemetry tests added
- ✅ Privacy policy documented in README.md

---

## WU 8.4: SSOT Documentation Update (1-2 Days) - **CRITICAL**

### Goal
Align all architectural and user-facing documentation with Epic 8 features to ensure the project is 100% documented for launch.

### Why This is Critical (not Optional)
- ❌ Without this, Epic 8 is a "half-shipped product"
- 🎯 SSOT documents are the contract with future developers
- 📋 New concepts (snapshots, resilience, telemetry) MUST be in BLUEPRINT and IMPLEMENTATION

### Part A: Update `docs/BLUEPRINT.yaml`

**Add New Section**: "Quality Assurance & Validation"
```yaml
qa_and_validation:
  approach: "Spec-Driven Testing + Snapshot Regression Testing"
  components:
    - name: "Semantic Validation Tests"
      purpose: "Ensure generated artifacts meet quality standards"
      location: "tests/quality/"
    - name: "Snapshot/Golden Master Testing"
      purpose: "Detect regressions in generated artifacts"
      tools: ["toolkit validate", "snapshots/ directory"]
    - name: "Resilience Testing"
      purpose: "Verify graceful degradation under failures"
      location: "tests/resilience/"
```

**Add New Section**: "Resilience & Error Recovery"
```yaml
resilience:
  approach: "Graceful degradation with fallback chains"
  components:
    - name: "Provider Fallback"
      description: "If Pollinations fails, try Replicate, then placeholder"
      implementation: "agency_toolkit/core/resilience.py"
    - name: "Font Fallback Cascade"
      description: "Try custom fonts, system fonts, then default"
      implementation: "agency_toolkit/core/social/rendering.py"
    - name: "Offline Mode"
      description: "Disable network calls with --offline flag"
      location: "agency_toolkit/cli_app.py"
```

**Add New Section**: "Production Observability"
```yaml
observability:
  approach: "Privacy-first anonymous telemetry"
  data_collected:
    - "Command usage counts (not details)"
    - "Error type counts (not stack traces)"
    - "Toolkit version"
    - "OS type"
  data_not_collected:
    - "User prompts or input"
    - "Generated artifact contents"
    - "Personal information"
  implementation: "agency_toolkit/core/telemetry.py"
  user_controls:
    - "toolkit stats (view local metrics)"
    - "toolkit stats --share (opt-in sharing)"
    - "toolkit config --no-telemetry (disable)"
```

### Part B: Update `docs/IMPLEMENTATION.yaml`

**Add New Modules**:
```yaml
core:
  resilience:
    file: "agency_toolkit/core/resilience.py"
    purpose: "Graceful degradation and error recovery"
    classes:
      - name: "ProviderFallback"
        methods:
          - "generate_with_fallback(prompt, seed)"
          - "generate_placeholder_image()"

  telemetry:
    file: "agency_toolkit/core/telemetry.py"
    purpose: "Privacy-first anonymous metrics collection"
    classes:
      - name: "AnonymousTelemetry"
        methods:
          - "track_command(cmd, duration, success)"
          - "track_error(error_type)"

commands:
  validate:
    file: "agency_toolkit/commands/validate.py"
    subcommands:
      - "validate --snapshot (generate and compare)"
      - "validate --approve (promote to master)"
      - "validate --report (show diffs)"
```

**Add New Testing Section**:
```yaml
testing:
  quality_tests:
    location: "tests/quality/"
    purpose: "Semantic validation and snapshot regression testing"
    test_files:
      - "test_prompt_quality.py (15+ tests)"
      - "test_output_contracts.py (10+ tests)"
      - "test_registry_hardening.py (5+ tests)"

  resilience_tests:
    location: "tests/resilience/"
    purpose: "Verify graceful degradation under failures"
    test_files:
      - "test_provider_fallback.py (5+ tests)"
      - "test_offline_mode.py (3+ tests)"
      - "test_retry_logic.py (4+ tests)"

  observability_tests:
    location: "tests/observability/"
    purpose: "Verify telemetry collection without privacy issues"
    test_files:
      - "test_telemetry.py (8+ tests)"

snapshots:
  location: "snapshots/"
  subdirs:
    - "approved/ (master golden artifacts)"
    - "current/ (latest test run)"
  purpose: "Regression detection for generated outputs"
```

### Part C: Update `README.md` (User-Facing)

**Add Section**: "Complete Command Reference"
```markdown
## Command Reference

### Information & Discovery
- `toolkit info` - Show all available commands and features
- `toolkit ask "<question>"` - Ask Mistral about toolkit capabilities

### Generation Commands
- `toolkit social "text" [options]` - Generate social media posts
- `toolkit briefing [options]` - Create project briefings
- `toolkit structure "client" "project" [options]` - Create folder structures
- `toolkit image "prompt" [options]` - Generate AI images

### Quality & Validation
- `toolkit validate --snapshot` - Check output quality
- `toolkit validate --approve` - Approve snapshots as new master
- `toolkit validate --report` - Show quality diffs

### Metrics & Usage
- `toolkit stats` - View your local usage metrics
- `toolkit stats --share` - Share anonymous stats (opt-in)

### Configuration
- `toolkit config --offline` - Disable network features
- `toolkit config --no-telemetry` - Disable metrics collection
```

**Add Section**: "New in Epic 8: Production Hardening"
```markdown
## What's New: Production Hardening

### Reliability
- **Provider Fallback**: If image generation fails, toolkit uses placeholder
- **Font Fallback**: Missing fonts automatically fallback to system fonts
- **Retry Logic**: API calls retry with exponential backoff
- **Offline Mode**: Run locally-only features with `--offline` flag

### Quality Assurance
- **Snapshot Testing**: `toolkit validate` detects output regressions
- **Semantic Validation**: Seed templates checked for quality
- **Test Coverage**: 250+ automated tests

### Observability
- **Usage Metrics**: `toolkit stats` shows what you use
- **Error Tracking**: Errors are logged locally for debugging
- **Privacy First**: No prompts, no personal data collected
```

**Add Section**: "Privacy Policy"
```markdown
## Privacy & Data

The toolkit collects **only** anonymous aggregate statistics:
- ✓ Count of commands used
- ✓ Count of errors by type
- ✓ Your toolkit version and OS

The toolkit **never** collects:
- ✗ Your prompts or generated content
- ✗ Personal information
- ✗ Prompts or image descriptions
- ✗ Any user input

All metrics are stored locally in `~/.toolkit/metrics.json`. You can:
- View them anytime with `toolkit stats`
- Opt-in to share them with `toolkit stats --share`
- Disable collection with `toolkit config --no-telemetry`

For details: See [PRIVACY.md](docs/PRIVACY.md)
```

### Part D: Update `docs/TRANSITION.md` (Release Notes)

**Add Section**: "v0.2 → v1.0: Production Hardening"
```markdown
## v1.0: Production Ready (Epic 8)

### New Features
- **Output Quality Guardian**: Snapshot testing for regressions
- **Graceful Degradation**: Works offline, handles API failures
- **Production Observability**: Anonymous metrics collection
- **Validated Quality**: All seed templates meet quality standards

### Reliability Improvements
- API calls now retry with exponential backoff (max 3 attempts)
- Missing fonts automatically fallback to system fonts
- Image generation failures use placeholder instead of crashing
- All commands have `--offline` support where applicable

### New CLI Commands
```bash
toolkit validate --snapshot    # Check output quality
toolkit validate --approve     # Update quality baseline
toolkit validate --report      # Show quality diffs
toolkit stats                  # View usage metrics
toolkit stats --share          # Share anonymous data (opt-in)
```

### Breaking Changes
None! All v0.2 commands work exactly as before.

### Migration Guide
No migration needed. Just update your version:
```bash
pip install --upgrade agency-toolkit
```

The new resilience features activate automatically.
```

### Part E: Create `docs/ARCHITECTURE_EPIC8.md` (New)

Document the new architecture:
- Resilience patterns (provider fallback, retry logic)
- Observability design (anonymous telemetry)
- Quality validation approach (snapshots)
- Privacy guarantees

### Success Criteria for WU 8.4
- ✅ BLUEPRINT.yaml updated with Resilience + Observability sections
- ✅ IMPLEMENTATION.yaml updated with new modules and testing strategy
- ✅ README.md updated with new commands and privacy policy
- ✅ TRANSITION.md documents v0.2 → v1.0 changes
- ✅ ARCHITECTURE_EPIC8.md created with detailed design docs
- ✅ All SSOT documents reviewed for consistency
- ✅ Zero ambiguity about what Epic 8 delivers

---

## Summary: Epic 8 Work Breakdown

| WU | Title | Days | Focus | Critical? |
|----|-------|------|-------|-----------|
| 8.1 | Output Quality Guardian | 3-4 | Semantic validation + snapshots | 🟡 High |
| 8.2 | Resilience & Error Recovery | 2-3 | Graceful degradation + fallbacks | 🟡 High |
| 8.3 | Production Observability | 1-2 | Anonymous telemetry + metrics | 🟢 Medium |
| 8.4 | SSOT Documentation Update | 1-2 | **BLUEPRINT + IMPLEMENTATION + README** | 🔴 **CRITICAL** |
| **TOTAL** | | **7-11 days** | **Production Launch Ready** | **YES** |

---

## Critical Note on WU 8.4

**This is not optional cleanup.** WU 8.4 is a core work unit because:

1. **SSOT as Contract**: BLUEPRINT.yaml and IMPLEMENTATION.yaml are the contract between "what exists" and "what developers/users believe exists". If they're out of sync after Epic 8, the next person will make wrong decisions.

2. **Onboarding**: New team members, future maintainers, and API consumers all rely on SSOT docs. Without updates, they won't know about:
   - Provider fallback mechanism
   - Offline mode
   - Snapshot validation
   - Telemetry opt-in
   - New CLI commands

3. **Launch Readiness**: A "production-ready" toolkit MUST be fully documented. Users need to know:
   - How to use new features
   - Privacy guarantees
   - Reliability characteristics
   - Migration path (if any)

**Without WU 8.4, Epic 8 is incomplete.**

---

## Next Steps

1. **Review this plan** - Confirm all WUs align with your vision
2. **Start WU 8.1** - Output Quality Guardian (highest priority)
3. **Run in parallel**:
   - WU 8.2 (Resilience) can start after WU 8.1 base infrastructure
   - WU 8.3 (Observability) is independent
4. **WU 8.4 last** - Update all SSOT docs after code is complete
5. **Launch v1.0** - Production-ready with full documentation

---

*Plan created: November 7, 2025*
*Based on Reality Check findings*
*Ready for implementation*
