# KDAF-Fix Test Suite

This directory contains test files and validation scripts for the `kdaf-fix` tool.

## Files

### Test Targets (Vulnerable Code)
- `core/phoenix_config/loaders.py` - Command injection vulnerability (SEC-001)
- `core/prompt_profiles.py` - Exception handling issue (SEC-002)
- `utils/api_client.py` - Hardcoded secrets (SEC-003)

### Test Data
- `test_issues.json` - Issue definitions that point to the test targets

### Test Scripts
- `validate_fix.py` - Pre-flight validation (checks that issues can be found)
- `integration_test.py` - Full integration test (applies fixes, verifies, restores)
- `test_edge_cases.py` - Edge case validation (8 error handling scenarios)

## Running Tests

```bash
# Pre-flight validation
python3 examples/test_files/validate_fix.py

# Integration test (applies & verifies fixes)
python3 examples/test_files/integration_test.py

# Edge case tests
python3 examples/test_files/test_edge_cases.py
```

## Test Results

### Integration Test
✅ All 3 security issues successfully fixed:
- SEC-001: Command injection → shell=False
- SEC-002: Exception handling → specific exceptions
- SEC-003: Hardcoded secrets → environment variables

### Edge Case Tests
✅ 8/8 tests passed:
- Missing file detection
- Line number out of range (high/zero/negative)
- Code mismatch detection
- Missing field validation
- Valid fix acceptance

## Validation Logic

The `apply_fix()` function implements these safety checks:

1. **Input validation**: All required fields present
2. **File existence**: Target file exists
3. **Line number validation**: Within file bounds (1 to len(lines))
4. **Code matching**: Exact snippet match on target line
5. **Safe replacement**: Only replaces matched code
6. **Git-first**: Suggests `git diff` after changes

This ensures fixes are only applied when:
- The file hasn't changed since analysis
- The line number is still valid
- The vulnerable code is exactly where expected
