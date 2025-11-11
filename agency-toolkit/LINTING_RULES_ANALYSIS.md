# Linting Rules Analysis & Decision Log

**Date:** 11 Nov 2025
**Status:** Completed Analysis - See Decisions Below

Currently, `pyproject.toml` ignores 9 linting rules. Below is the analysis and decision for each.

---

## Rules Currently Ignored

### 1. E501 - Line too long
```
Rule: E501
Current Ignore: YES
Status: DECISION - KEEP IGNORED (with conditions)
```

**Reasoning:**
- Agency-toolkit uses 88 character line limit (Black default)
- Some lines legitimately exceed this (long string messages, complex type hints)
- **Decision:** Keep ignored but:
  - [ ] Do NOT use as excuse for sloppy code
  - [ ] NEW RULE: If a line exceeds 120 chars, must be justified with comment
  - [ ] Review after next refactor

---

### 2. E722 - Bare except (naked except)
```
Rule: E722
Current Ignore: YES
Status: DECISION - FIX NOW
```

**Reasoning:**
- Bare `except:` masks all exceptions including KeyboardInterrupt, SystemExit
- This is a **REAL BUG**, not a style issue
- Bad pattern: `except: pass` silently swallows everything

**Decision:** ENABLE THIS RULE
```bash
# Remove "E722" from pyproject.toml
# Run: ruff check agency_toolkit/ --fix
# Review changes manually
```

**Action:** Remove E722 from ignore list ✅ (Must do)

---

### 3. F401 - Unused imports
```
Rule: F401
Current Ignore: YES
Status: DECISION - FIX NOW (systematic)
```

**Reasoning:**
- Unused imports bloat code and confuse maintainers
- Usually indicates dead code or refactoring leftovers
- Legitimate cases (type-only imports, conditional imports) can be marked with `# noqa: F401`

**Decision:** ENABLE THIS RULE - but with exceptions
```bash
# Step 1: Find all unused imports
ruff check agency_toolkit/ --select F401 --no-fix

# Step 2: For each, decide:
#   - Is it type-only? Add # noqa: F401
#   - Is it unused? Delete it
#   - Is it needed for side effects? Add comment

# Step 3: Add F401 back to select, remove from ignore
```

**Action:** Fix unused imports ✅ (Must do)

---

### 4. F601 - Duplicate dict keys
```
Rule: F601
Current Ignore: YES
Status: DECISION - FIX NOW (critical)
```

**Reasoning:**
- Duplicate keys in dict literals = BUG (last value wins, rest silently lost)
- This is a **DATA LOSS BUG**, not a style issue
- Example:
  ```python
  config = {
    "setting": "value1",
    "setting": "value2"  # ← First value is LOST
  }
  ```

**Decision:** ENABLE THIS RULE IMMEDIATELY
```bash
# Find and fix all duplicate dict keys
ruff check agency_toolkit/ --select F601 --fix
```

**Action:** Fix duplicate dict keys ✅ (Critical - must do)

---

### 5. F841 - Unused variables
```
Rule: F841
Current Ignore: YES
Status: DECISION - FIX NOW
```

**Reasoning:**
- Unused variables indicate dead code or refactoring mistakes
- Can mask actual bugs (e.g., forgot to use result of expensive operation)

**Decision:** ENABLE THIS RULE
```bash
# Find unused variables
ruff check agency_toolkit/ --select F841

# For each, decide:
#   - Is it intentional (e.g., unpacking)? Rename to _var
#   - Is it dead code? Delete it
```

**Action:** Fix unused variables ✅ (Must do)

---

### 6. E402 - Module imports not at top
```
Rule: E402
Current Ignore: YES
Status: DECISION - KEEP IGNORED (but document)
```

**Reasoning:**
- Some imports MUST come after code (e.g., after setting env variables)
- Agency-toolkit uses this pattern in CLI for lazy loading

**Decision:** KEEP IGNORED but:
- [ ] Mark each E402 violation with comment `# noqa: E402 - lazy loading for <reason>`
- [ ] Document pattern in CONTRIBUTING.md

**Example:**
```python
import os
os.environ['ENV_VAR'] = 'value'
from expensive_module import something  # noqa: E402 - env vars must be set first
```

**Action:** Add comments to E402 violations ⏳ (Can do later)

---

### 7. UP038 - Use X | Y instead of Union[X, Y]
```
Rule: UP038
Current Ignore: YES
Status: DECISION - KEEP IGNORED (for now)
```

**Reasoning:**
- UP038 wants you to use `str | int` instead of `Union[str, int]`
- This requires Python 3.10+
- Agency-toolkit supports Python 3.10, 3.11, 3.12
- But mixing styles is inconsistent

**Decision:** KEEP IGNORED FOR NOW
- Once codebase fully converted to 3.10+ syntax, remove this

**Action:** Revisit after Python 3.9 support ends

---

### 8. W293 - Blank line whitespace
```
Rule: W293
Current Ignore: YES
Status: DECISION - KEEP IGNORED
```

**Reasoning:**
- This warns about whitespace on blank lines
- Minor style issue, not a bug
- Black handles this automatically

**Decision:** KEEP IGNORED
- Not worth the noise

**Action:** No change needed

---

### 9. N802 - Function name should be lowercase
```
Rule: N802
Current Ignore: YES
Status: DECISION - KEEP IGNORED
```

**Reasoning:**
- AST visitors use camelCase by convention (visitClassName, etc.)
- This is a known legitimate exception
- Only affects specific types of functions

**Decision:** KEEP IGNORED
- But add comment: "# AST visitors use camelCase by convention"

**Action:** Add comment to pyproject.toml ✅

---

## ACTION PLAN - NEXT 1 HOUR

### HIGH PRIORITY (Do immediately):
1. ❌ Remove E722 (bare except) from ignore list
2. ❌ Remove F401 (unused imports) from ignore list
3. ❌ Remove F601 (duplicate dict keys) from ignore list
4. ❌ Remove F841 (unused variables) from ignore list

### MEDIUM PRIORITY (Do next session):
5. ⏳ Add `# noqa: E402` comments to lazy imports

### LOW PRIORITY (Do after refactor):
6. ⏳ Remove UP038 after full Python 3.10+ conversion
7. ⏳ Document E402 pattern in CONTRIBUTING.md

---

## Current Decision Summary

| Rule | Ignore? | Why | Action |
|------|---------|-----|--------|
| E501 | ✅ YES | Legitimate line length variance | Keep, review after refactor |
| E722 | ❌ NO | Bare except is a BUG | **REMOVE NOW** |
| F401 | ❌ NO | Unused imports indicate dead code | **REMOVE NOW** |
| F601 | ❌ NO | Duplicate keys = data loss BUG | **REMOVE NOW** |
| F841 | ❌ NO | Unused vars indicate dead code | **REMOVE NOW** |
| E402 | ✅ YES | Lazy imports are intentional | Keep, add comments |
| UP038 | ✅ YES | Mixed Python 3.9-3.12 support | Revisit later |
| W293 | ✅ YES | Minor style issue | Keep |
| N802 | ✅ YES | AST visitor convention | Keep, add comment |

---

## Strict Rules (must be fixed):

```yaml
MUST_REMOVE_FROM_IGNORE:
  - E722  # Bare except - this masks bugs
  - F401  # Unused imports - indicates dead code
  - F601  # Duplicate dict keys - data loss!
  - F841  # Unused variables - indicates dead code

SHOULD_KEEP_IGNORED:
  - E501  # Line length (88 char is reasonable limit)
  - E402  # Module imports (lazy loading is intentional)
  - UP038 # Union syntax (Python 3.10+ conversion in progress)
  - W293  # Blank line whitespace (cosmetic)
  - N802  # Function names (AST visitors use camelCase)
```

---

## Next Steps

1. Review this analysis
2. Decide: Ready to fix immediately or schedule for later?
3. If fixing now: Apply changes from ACTION PLAN above
4. If scheduling: Add to backlog with timeline
