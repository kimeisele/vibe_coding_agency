# 🎯 IMMEDIATE ACTION ITEMS - Next Session

## 🔴 CRITICAL (Blocking Production Readiness)

### 1️⃣ Fix Pre-Commit Hooks Configuration
**Priority**: 🔴 CRITICAL
**Time**: 2-3 hours
**Impact**: All commits currently bypass hooks with `--no-verify`

**Diagnosis Steps**:
```bash
cd /Users/ss/projects/agency_toolkit
pre-commit run --all-files
```

**Expected Issues**:
- Likely hook configurations are outdated or tools missing
- Possible: black, ruff, mypy version mismatches
- May need `.pre-commit-config.yaml` update

**Resolution**:
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Try running again
pre-commit run --all-files

# If still failing: debug specific hooks
pre-commit run black --all-files -v
pre-commit run ruff --all-files -v
pre-commit run mypy --all-files -v
```

---

### 2️⃣ Install Questionary Dependency
**Priority**: 🔴 CRITICAL
**Time**: 10 minutes
**Impact**: Blocks 4 test files from running

**Current Status**:
- 264 tests passing with questionary excluded
- 4 tests skipped (import errors)
- These tests block Full CI pipeline

**Action**:
```bash
pip install "agency-toolkit[interactive]"
# OR
pip install questionary

# Verify
python3 -m pytest tests/unit/test_info_command_unit.py -v
```

---

### 3️⃣ Epic 1.2: Update Vulnerable Dependencies
**Priority**: ✅ COMPLETE (2025-11-08)
**Time**: 45 minutes (actual)
**Status**: 3/4 CVEs resolved

**Results**:
```
✅ brotli: 1.1.0 → 1.2.0
✅ pdfminer-six: 20250506 → 20251107
✅ starlette: 0.47.2 → 0.49.3
✅ fastapi: 0.116.1 → 0.121.0 (dependency fix)
⚠️ torch: 2.2.2 (latest available - 2.6.0 N/A on macOS)
```

**Test Results**: 350 passed, 5 skipped
**Commit**: `70a76ca`

**Note**: 1 CVE remains in torch due to PyTorch 2.6.0 not being available for macOS x86_64. Not blocking for portfolio showcase.

---

## 🟡 MEDIUM PRIORITY (Roadmap Phase 1)

### 4️⃣ Epic 1.3.1: Image Generation Error Handling
**Priority**: 🟡 MEDIUM
**Time**: 2 hours
**Estimated Effort**: 80 lines of code + 3 unit tests

**Location**: `agency_toolkit/image_gen.py`

**Deliverables**:
- Try/except wrapper around `provider_instance.generate()`
- Handle: `ProviderError`, `httpx.HTTPError`, `httpx.ConnectError`
- Retry logic: 3 attempts with exponential backoff
- User-friendly error messages
- Unit tests mocking failures

---

### 5️⃣ Epic 1.3.2: Refactor Exception Handling in ai.py
**Priority**: 🟡 MEDIUM
**Time**: 3 hours
**Estimated Effort**: 150 lines + 5 unit tests

**Location**: `agency_toolkit/commands/ai.py`

**Deliverables**:
- Replace generic `except Exception` with specific types
- Custom messages for each error type
- Debug logging in debug mode only
- 5 new unit tests covering all error paths

---

### 6️⃣ Epic 1.3.3: Input Validation Framework
**Priority**: 🟡 MEDIUM
**Time**: 4 hours
**Estimated Effort**: 200 lines + 8-10 tests

**New File**: `agency_toolkit/commands/validators.py`

**Deliverables**:
- Reusable validation functions for:
  - File paths (exist, readable, extension checks)
  - Enum choices validation
  - Numerical ranges
- Apply to all CLI commands
- Property-based tests (optional but recommended)

---

## 🟢 LOWER PRIORITY (Epics 3.3-3.4, Phase 2)

### 7️⃣ Epic 3.3: Refactor `info.py::providers_status`
**Status**: ⏳ PENDING
**Current CC**: 15
**Target CC**: <8 (47% reduction)
**Time**: 2 hours

**Pattern**: Similar to Epic 3.1-3.2 (lookup + extraction)

---

### 8️⃣ Epic 3.4: Refactor `social.py::social` Main Logic
**Status**: ⏳ PENDING
**Current CC**: 13
**Target CC**: <8 (38% reduction)
**Time**: 3 hours

**Pattern**: Extract batch handling helpers

---

## 📊 CURRENT STATE SUMMARY

```
✅ Master Branch: Stable
✅ Core Tests: 350 passing / 0 failing
✅ Epics 1.1, 1.2, 3.1-3.2: Complete
✅ CVEs: 3/4 fixed (torch pending platform support)
✅ Typer/Reporter: Fixed
❌ Pre-Commit: Broken (using --no-verify)
❌ Questionary: Dependency missing for 4 tests
```

---

## 🚀 SUCCESS CRITERIA (Next Session)

Session can be considered successful when:
1. ✅ Pre-commit hooks passing on all files
2. ✅ All 354 tests passing (350 current + 4 questionary)
3. ⏳ pip-audit shows minimal vulnerabilities (torch CVE acknowledged)
4. ✅ No `--no-verify` commits needed
5. ✅ CI pipeline green

---

**Created**: 2025-11-08
**For**: Next session AI agent
**Priority Order**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
