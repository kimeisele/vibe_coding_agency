# Mock Refactoring Strategy - Technical Debt Analysis

**Date:** 11 Nov 2025
**Status:** Documented - Not yet implemented (Planned for Phase 3)

---

## Current State: Mock Overuse Problem

### Statistics
- **376 mock/patch usages** across test suite
- **376 instances** in ~48 test files
- **Coverage:** ~62% of tests use mocks

### Examples of Problematic Patterns

#### Bad Pattern 1: Mocking External Dependencies
```python
# tests/test_image_gen_unit.py - Line 62-81
@patch("agency_toolkit.image_gen.get_provider")
def test_generate_image_handles_http_error(self, mock_get_provider):
    """Problem: Tests the error handler, not the provider logic"""
    mock_provider_instance = MagicMock()
    mock_provider_instance.generate.side_effect = httpx.HTTPError(...)
    # ^ This is a FAKE error, not what real code would see
```

**What's Wrong:**
- Real `get_provider()` might fail differently
- Test passes but real code could fail
- Error handling logic is tested in isolation

**Better Approach:**
```python
# Instead: Create real (stubbed) provider for this test
class TestProviderStub:
    def generate(self, prompt):
        raise httpx.HTTPError("Connection failed")

def test_generate_image_handles_http_error(self):
    config = load_test_config()
    provider = TestProviderStub()

    with pytest.raises(ImageProviderError):
        generate_image(prompt="test", config=config, provider=provider)
```

#### Bad Pattern 2: Mocking Configuration Loading
```python
# Many tests do:
mock_config = MagicMock()
# ^ This is FAKE config, not real structure

# Better:
config = load_test_config()  # Real config with test data
```

#### Bad Pattern 3: Mocking the Thing You're Testing
```python
# DON'T do this:
@patch("agency_toolkit.image_gen.generate_image")
def test_generate_image():
    # ^ Testing the mock, not the real function
```

---

## The Fix Strategy (3-Phase Approach)

### Phase 1: Identification ✅ DONE
- [x] Count total mocks (376)
- [x] Identify problematic patterns
- [x] Document specific examples
- [x] Categorize by type

### Phase 2: Prioritization (Next)
**Priority 1 - High Impact Refactors:**
1. Config loading mocks → Use test fixtures
2. Provider mocks → Create stub providers
3. Orchestrator mocks → Use test modules

**Priority 2 - Medium Impact:**
4. File I/O mocks → Use tempfile
5. API response mocks → Store test fixtures

**Priority 3 - Low Impact (Keep Mocked):**
6. External APIs (Twitter, etc) → OK to mock
7. Network calls (unless testing resilience)
8. Third-party library internals

### Phase 3: Refactoring (After Stabilization)
- Remove mocks for high-priority items
- Replace with test fixtures
- Verify test behavior doesn't change
- Measure coverage improvement

---

## Action Items for Next Phase

### Immediate (This Week):
- [ ] Identify the 5 worst mock patterns
- [ ] Create test fixtures to replace them
- [ ] Document new patterns in CONTRIBUTING.md

### Short-term (Next 2 Weeks):
- [ ] Replace config mocks with test fixtures
- [ ] Replace provider mocks with stub providers
- [ ] Run integration tests to verify behavior

### Long-term (After Release):
- [ ] Remove all unnecessary mocks
- [ ] Document best practices
- [ ] Create reusable test fixtures library

---

## The 5 Worst Offenders

### 1. **test_image_gen_unit.py**
- **Lines:** 62-81, 83-100, etc.
- **Issue:** Mocks `get_provider()` and error handling
- **Fix:** Create TestProvider stub, use real error paths
- **Effort:** 2-3 hours

### 2. **test_social_refactored_unit.py**
- **Issue:** Mocks social API providers
- **Fix:** Create test fixtures with sample posts
- **Effort:** 2-3 hours

### 3. **test_os_interactive_unit.py**
- **Issue:** Mocks config and file I/O
- **Fix:** Use tempfile and test fixtures
- **Effort:** 3-4 hours

### 4. **test_validate_refactored_unit.py**
- **Issue:** Mocks validation logic
- **Fix:** Create test data, run real validation
- **Effort:** 2 hours

### 5. **test_pollinations.py**
- **Issue:** Mocks HTTP client
- **Fix:** Use responses library for real HTTP mocking
- **Effort:** 1-2 hours

---

## Test Impact Matrix

| Test File | Mocks | Effort | Priority | Impact |
|-----------|-------|--------|----------|--------|
| test_image_gen_unit.py | 15 | 3h | P1 | High |
| test_social_refactored_unit.py | 12 | 3h | P1 | High |
| test_os_interactive_unit.py | 18 | 4h | P1 | High |
| test_validate_refactored_unit.py | 8 | 2h | P2 | Med |
| test_pollinations.py | 10 | 2h | P2 | Med |

**Total Effort Estimate:** ~14 hours to refactor top 5 files

---

## Rules for New Tests

Going forward, follow these patterns:

### ✅ DO:
```python
# Use real implementations with test data
def test_something():
    config = load_test_config()  # Real Config object
    result = process(config)
    assert result.success
```

### ❌ DON'T:
```python
# Don't mock the core logic
@patch("module.function_you_are_testing")
def test_something(mock_func):
    # ^ This tests the mock, not the code
```

### ✅ DO (for external APIs):
```python
# Use responses library for HTTP
@responses.activate
def test_api_call():
    responses.add(responses.GET, "https://api.example.com/data", ...)
    # Test real code path with stubbed HTTP
```

### ❌ DON'T (for internal functions):
```python
# Don't mock orchestrator internals
@patch("orchestrator.execute_task")
def test_workflow():
    # ^ Use real orchestrator, test the integration
```

---

## Success Criteria (for Phase 3)

- [ ] Reduce mocks from 376 → 150 (max)
- [ ] All new tests use real implementations
- [ ] Integration tests all pass
- [ ] Coverage reports show better quality
- [ ] CONTRIBUTING.md documents mock policies

---

## Technical Debt Ticket

```
Title: Refactor Test Mocks to Use Real Implementations
Priority: Medium
Effort: ~14 hours
Phase: Post-Stabilization
Blockers: None
Dependencies: Existing test infrastructure
```

This will be tracked as a separate initiative after the regression prevention phase is complete.
