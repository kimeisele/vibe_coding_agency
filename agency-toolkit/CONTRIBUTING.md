# Contributing to Agency Toolkit

## Testing Standards & Best Practices

This document outlines testing standards for the Agency Toolkit project, established through the 2-Week Regression Prevention Initiative.

---

## Core Testing Philosophy

**Goal:** Tests should catch real bugs, not just mock behavior.

**Problem We Solve:**
```
❌ BEFORE: Tests passed, but real code was broken
   - Tests tested Mocks
   - Reality was never tested
   - Regressions appeared in production

✅ AFTER: Tests catch real issues immediately
   - Tests use real implementations
   - Mocks used only where necessary
   - Regressions caught in CI
```

---

## Test Categories

### 1. Smoke Tests (Integration)
**Purpose:** Verify CLI and basic functionality works end-to-end

**Pattern:**
```python
def test_cli_runs_without_crashing():
    """NO MOCKS - real execution"""
    result = subprocess.run(["toolkit", "--help"], capture_output=True)
    assert result.returncode == 0
```

**Guidelines:**
- ✅ Use real subprocess execution
- ✅ Test actual CLI commands
- ✅ Verify output structure
- ❌ Don't mock the CLI framework

---

### 2. Integration Tests (Real Data)
**Purpose:** Test workflows and component interactions

**Pattern:**
```python
def test_workflow_executes():
    """Use real implementations with test data"""
    module = {
        "id": "test_m1",
        "tasks": [{"tool": "info", "params": {}}]
    }
    context = {}  # Real context

    # Use REAL orchestrator, no mocks
    report = execute_module(module, context)

    assert report.successful > 0
```

**Guidelines:**
- ✅ Use `load_test_config()` or fixtures
- ✅ Pass real config objects, not `MagicMock()`
- ✅ Test real workflows end-to-end
- ✅ Verify real output structure
- ❌ Don't mock the orchestrator
- ❌ Don't mock config loading

---

### 3. Contract Tests (API Guarantees)
**Purpose:** Define and enforce API contracts

**Pattern:**
```python
def test_orchestrator_statistics_consistent():
    """Verify API contract: total == successful + failed + skipped"""
    report = execute_module(module, context)

    # Contract verification
    assert (
        report.total_tasks ==
        report.successful + report.failed + report.skipped
    )
```

**Guidelines:**
- ✅ Test real objects with real data
- ✅ Verify all expected fields exist
- ✅ Check type consistency
- ✅ Verify math/invariants
- ❌ Don't mock the object being tested

---

### 4. Unit Tests (Pure Functions)
**Purpose:** Test isolated logic with no dependencies

**Pattern:**
```python
def test_generate_seed_is_deterministic():
    """NO MOCKS - pure function"""
    seed1 = image_gen._generate_seed("prompt")
    seed2 = image_gen._generate_seed("prompt")
    assert seed1 == seed2
```

**Guidelines:**
- ✅ Test pure functions (no side effects)
- ✅ Test utility functions
- ✅ Test pure calculations
- ✅ Use mocks ONLY for unavoidable dependencies
- ❌ Don't test business logic with only mocks
- ❌ Don't mock the function you're testing

---

## When to Use Mocks (And When NOT To)

### ✅ DO Mock These Things

1. **External APIs** (if not testing resilience)
   ```python
   @responses.activate
   def test_api_call():
       responses.add(responses.GET, "https://api.example.com/...", json={...})
       result = fetch_from_api()  # REAL function, mocked HTTP
   ```

2. **Third-party Libraries** (when testing error handling)
   ```python
   @patch("requests.get")
   def test_handles_network_error(mock_get):
       mock_get.side_effect = ConnectionError()
       # Test your error handling with real exception
   ```

3. **System Dependencies** (file system, time)
   ```python
   @patch("pathlib.Path.exists")
   def test_handles_missing_file(mock_exists):
       mock_exists.return_value = False
       # Test behavior when file doesn't exist
   ```

### ❌ DON'T Mock These Things

1. **Your Own Functions** (you're testing them!)
   ```python
   # ❌ WRONG - this tests the mock, not your code
   @patch("agency_toolkit.core.orchestrator.execute_module")
   def test_workflow(mock_execute):
       result = mock_execute()
   ```

2. **Config Loading**
   ```python
   # ❌ WRONG
   mock_config = MagicMock()

   # ✅ RIGHT
   config = load_test_config()  # Use real config
   ```

3. **Business Logic Classes**
   ```python
   # ❌ WRONG - mocking the thing you're testing
   @patch("agency_toolkit.providers.Pollinations")
   def test_image_generation(mock_provider):
       pass

   # ✅ RIGHT - use a real stub
   class TestProviderStub:
       def generate(self, *args):
           return {"image": "test.png"}

   stub = TestProviderStub()
   result = generate_image(..., provider=stub)
   ```

---

## Test Fixtures & Stubs

### Use Test Fixtures
```python
# tests/fixtures/config.py
def load_test_config():
    """Load a real Config object with test data"""
    return Config(
        output_dir=Path("/tmp/test"),
        social_style="modern",
        # ... other fields
    )
```

### Create Stub Classes
```python
# Instead of @patch and MagicMock
class TestProviderStub:
    """A REAL class that acts like a provider"""
    def __init__(self, error=None, result=None):
        self.error = error
        self.result = result or {}

    def generate(self, *args):
        if self.error:
            raise self.error
        return self.result

# Use in test
stub = TestProviderStub(error=HTTPError("..."))
# Pass to code - it's a real object
```

---

## Test File Organization

```
tests/
├── smoke/                    # CLI smoke tests (no mocks)
│   └── test_cli_smoke.py
├── regression/               # Golden master snapshot tests
│   ├── test_output_regression.py
│   └── golden_masters/
├── integration/              # Real integration tests
│   ├── test_config_priority.py
│   ├── test_orchestrator_contract.py
│   ├── test_critical_workflows.py
│   └── fixtures/
├── unit/                     # Pure function unit tests
│   └── test_*.py
└── conftest.py               # Shared fixtures
```

---

## Golden Master Tests (Snapshot Testing)

Purpose: Catch unintended output changes

```python
def test_info_output_stable():
    """Output regression test using golden master"""
    result = subprocess.run(["toolkit", "info", "info"], capture_output=True)

    golden_file = Path("tests/regression/golden_masters/info_output.txt")

    if not golden_file.exists():
        # First run: save baseline
        golden_file.write_text(result.stdout)
    else:
        # Compare: if output changed, test fails
        assert result.stdout == golden_file.read_text()
```

---

## Code Review Checklist for Tests

When reviewing test PRs, check:

- [ ] **No unnecessary mocks** - Is every `@patch` justified?
- [ ] **Real data** - Uses real Config, real fixtures, not `MagicMock()`?
- [ ] **Tests the code, not mocks** - Would the test fail if code behavior changed?
- [ ] **Consistent with patterns** - Follows one of the 4 categories above?
- [ ] **Clear purpose** - Docstring explains what's being tested and why?
- [ ] **Integration tested** - Real workflows tested end-to-end (smoke tests)?

---

## Common Patterns to Avoid

### ❌ Pattern 1: Mocking Everything
```python
@patch("module.func1")
@patch("module.func2")
@patch("module.func3")
def test_something(mock1, mock2, mock3):
    # If 3+ mocks, usually testing with mocks instead of real code
    # Better: Write integration test with real code
```

### ❌ Pattern 2: Deep Mock Chain
```python
mock_provider.method.return_value.another_method.return_value = ...
# This complexity indicates: test real code instead
```

### ❌ Pattern 3: Config Mocks
```python
mock_config = MagicMock()
mock_config.output_dir = "/tmp"
# Better: use real Config object
config = Config(output_dir=Path("/tmp"))
```

---

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Category
```bash
pytest tests/smoke/          # Smoke tests
pytest tests/integration/    # Integration tests
pytest tests/unit/           # Unit tests
pytest tests/regression/     # Golden master tests
```

### With Coverage
```bash
pytest tests/ --cov=agency_toolkit --cov-report=html
```

---

## Test Statistics Goals

| Metric | Target | Current |
|--------|--------|---------|
| Total Tests | 800+ | 838 |
| Integration Tests | 100+ | 41+ |
| Mock Usage | <200 | 376 → 200 |
| Coverage | >80% | ~75% |

---

## Questions?

If you have questions about testing patterns:
1. Check `MOCK_REFACTORING_STRATEGY.md` for detailed analysis
2. Look at recent tests in `tests/integration/` for examples
3. Review `REGRESSION_PREVENTION_PLAN.md` for the philosophy

---

**Last Updated:** 11 Nov 2025
**Initiative:** 2-Week Regression Prevention
**Status:** Active
