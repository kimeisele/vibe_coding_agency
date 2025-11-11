# Test Suite Best Practices Guide

This document defines the standards and best practices for our test suite. Following these guidelines ensures maintainable, reliable, and fast tests that give us confidence in our code.

## Table of Contents
1. [The Testing Pyramid](#the-testing-pyramid)
2. [Core Principles](#core-principles)
3. [Test Organization](#test-organization)
4. [Writing Good Tests](#writing-good-tests)
5. [Mocking & Dependencies](#mocking--dependencies)
6. [Common Patterns](#common-patterns)
7. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
8. [Running Tests](#running-tests)

---

## The Testing Pyramid

Our test architecture follows the testing pyramid principle:

```
        /\
       /  \  E2E Tests (few, slow, expensive)
      /----\
     /      \ Integration Tests (some, moderate speed)
    /--------\
   /          \ Unit Tests (many, fast, cheap)
  /------------\
```

### Unit Tests (`/tests/unit/`)
- **Quantity:** 70-80% of all tests
- **Speed:** < 100ms per test
- **Scope:** Single function, method, or class
- **Dependencies:** All external dependencies mocked
- **Purpose:** Verify business logic in isolation

### Integration Tests (`/tests/integration/`)
- **Quantity:** 15-25% of all tests
- **Speed:** < 1s per test
- **Scope:** Multiple components working together
- **Dependencies:** External services mocked, internal integrations real
- **Purpose:** Verify component interactions

### E2E Tests (`/tests/e2e/`)
- **Quantity:** 5-10% of all tests
- **Speed:** Can be slow (seconds to minutes)
- **Scope:** Complete user workflows
- **Dependencies:** Full system with minimal mocking
- **Purpose:** Verify critical user journeys

---

## Core Principles

### 1. Test Isolation
Every test must be completely independent.

✅ **Good:**
```python
def test_user_creation(tmp_path):
    db = Database(tmp_path / "test.db")
    user = db.create_user("alice")
    assert user.name == "alice"
```

❌ **Bad:**
```python
# Depends on state from previous test
def test_user_login():
    user = db.get_user("alice")  # Assumes alice exists!
    assert user.login()
```

### 2. Fast Feedback
Unit tests should run in milliseconds, full suite in seconds.

- No network calls
- No file I/O (except in integration tests with `tmp_path`)
- No sleep/wait statements
- No database queries (use in-memory or mocks)

### 3. Deterministic Results
Tests must produce the same result every time.

✅ **Good:**
```python
def test_parse_date():
    result = parse_date("2024-01-15")
    assert result == datetime(2024, 1, 15)
```

❌ **Bad:**
```python
def test_parse_date():
    result = parse_date("today")  # Non-deterministic!
    assert result.day == datetime.now().day
```

### 4. One Assertion Focus
Each test should verify one specific behavior.

✅ **Good:**
```python
def test_calculate_discount_applies_percentage():
    assert calculate_discount(100, 0.1) == 90

def test_calculate_discount_handles_zero():
    assert calculate_discount(100, 0) == 100
```

❌ **Bad:**
```python
def test_calculate_discount():
    assert calculate_discount(100, 0.1) == 90
    assert calculate_discount(100, 0) == 100
    assert calculate_discount(0, 0.5) == 0
    # Too many concerns in one test!
```

---

## Test Organization

### File Structure
```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_database.py
│   └── test_validators.py
├── integration/
│   ├── test_api_database.py
│   └── test_cli_workflow.py
├── e2e/
│   └── test_user_journey.py
├── fixtures/
│   ├── __init__.py
│   └── common.py
└── conftest.py
```

### Naming Conventions

**Test Files:** `test_<module_name>.py`
```python
# For src/auth/login.py
# Create tests/unit/test_login.py
```

**Test Functions:** `test_<function>_<scenario>_<expected_result>`
```python
def test_login_with_valid_credentials_returns_token()
def test_login_with_invalid_password_raises_error()
def test_login_with_missing_username_returns_400()
```

**Test Classes:** `Test<ClassName>`
```python
class TestUserAuthentication:
    def test_validates_password_length(self):
        pass

    def test_hashes_password_before_storage(self):
        pass
```

---

## Writing Good Tests

### The AAA Pattern
Structure tests with Arrange, Act, Assert:

```python
def test_shopping_cart_calculates_total():
    # Arrange
    cart = ShoppingCart()
    cart.add_item(Item("Book", 10.00))
    cart.add_item(Item("Pen", 1.50))

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 11.50
```

### Use Descriptive Assertions
```python
# ✅ Good: Clear what went wrong
assert user.age >= 18, f"User {user.name} must be 18+, got {user.age}"

# ❌ Bad: Unclear what failed
assert user.age >= 18
```

### Parametrized Tests
Use `pytest.mark.parametrize` for similar test cases:

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("123", "123"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert to_uppercase(input) == expected
```

### Fixtures for Common Setup
```python
# conftest.py
@pytest.fixture
def sample_user():
    return User(name="Alice", email="alice@example.com")

# test_user.py
def test_user_email_validation(sample_user):
    assert sample_user.is_valid_email()
```

---

## Mocking & Dependencies

### When to Mock
Mock external dependencies that are:
- Slow (network, database, file system)
- Non-deterministic (time, random, external APIs)
- Difficult to set up (third-party services)
- Outside your control

### Mock Strategies

**1. Dependency Injection (Preferred)**
```python
# ✅ Code that's easy to test
class EmailService:
    def __init__(self, smtp_client):
        self.smtp_client = smtp_client

    def send(self, to, message):
        return self.smtp_client.send(to, message)

# Test
def test_email_service_sends_message():
    mock_smtp = Mock()
    service = EmailService(mock_smtp)

    service.send("user@example.com", "Hello")

    mock_smtp.send.assert_called_once_with("user@example.com", "Hello")
```

**2. Patch for Legacy Code**
```python
from unittest.mock import patch, Mock

# Use patch.object for specific targeting
def test_user_saves_to_database():
    with patch.object(Database, 'save') as mock_save:
        user = User("Alice")
        user.save()

        mock_save.assert_called_once()

# Use patch for module-level functions
@patch('myapp.utils.send_email')
def test_registration_sends_welcome_email(mock_send):
    register_user("alice@example.com")
    assert mock_send.called
```

**3. Mock Return Values**
```python
def test_fetch_user_data():
    mock_api = Mock()
    mock_api.get_user.return_value = {"name": "Alice", "id": 123}

    service = UserService(api=mock_api)
    user = service.fetch_user(123)

    assert user.name == "Alice"
```

**4. Mock Side Effects**
```python
def test_retry_on_failure():
    mock_api = Mock()
    mock_api.call.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"status": "success"}
    ]

    result = retry_api_call(mock_api)
    assert result["status"] == "success"
    assert mock_api.call.call_count == 3
```

### Patching Best Practices

```python
# ✅ Good: Patch where it's used
# myapp/service.py imports datetime
@patch('myapp.service.datetime')
def test_timestamp(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1)
    # ...

# ❌ Bad: Patch at source
@patch('datetime.datetime')  # Too broad!
def test_timestamp(mock_datetime):
    # ...
```

---

## Common Patterns

### Testing Exceptions
```python
import pytest

def test_division_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_email_raises_with_message():
    with pytest.raises(ValueError, match="Invalid email format"):
        validate_email("not-an-email")
```

### Testing Async Code
```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data()
    assert result is not None
```

### Testing File Operations
```python
def test_save_config(tmp_path):
    config_file = tmp_path / "config.json"

    save_config(config_file, {"setting": "value"})

    assert config_file.exists()
    content = json.loads(config_file.read_text())
    assert content["setting"] == "value"
```

### Testing Time-Dependent Code
```python
from freezegun import freeze_time

@freeze_time("2024-01-15 10:00:00")
def test_expiry_check():
    token = Token(expires_at="2024-01-15 09:00:00")
    assert token.is_expired()
```

---

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details
```python
# Bad: Tests internal structure
def test_user_storage():
    user = User("Alice")
    assert user._password_hash is not None  # Private attribute!

# Good: Tests behavior
def test_user_authenticates_with_correct_password():
    user = User("Alice", password="secret123")
    assert user.verify_password("secret123")
```

### ❌ Over-Mocking
```python
# Bad: Mocking everything
def test_calculate_total():
    mock_cart = Mock()
    mock_cart.items = Mock()
    mock_cart.items.return_value = Mock()
    # Too much mocking, test is meaningless!

# Good: Only mock external dependencies
def test_calculate_total():
    cart = ShoppingCart()  # Real object
    cart.add_item(Item("Book", 10))
    assert cart.total() == 10
```

### ❌ Brittle Tests
```python
# Bad: Breaks on small changes
def test_format_user():
    user = User("Alice", "alice@example.com")
    # If order changes, test breaks!
    assert str(user) == "Alice (alice@example.com)"

# Good: Tests essential behavior
def test_format_user():
    user = User("Alice", "alice@example.com")
    result = str(user)
    assert "Alice" in result
    assert "alice@example.com" in result
```

### ❌ Shared State Between Tests
```python
# Bad: Shared mutable state
shared_list = []

def test_add_item():
    shared_list.append(1)
    assert len(shared_list) == 1

def test_list_empty():
    assert len(shared_list) == 0  # Fails if test_add_item ran first!

# Good: Fresh state per test
def test_add_item():
    my_list = []
    my_list.append(1)
    assert len(my_list) == 1
```

### ❌ Sleep in Tests
```python
# Bad: Slow and flaky
def test_async_operation():
    start_background_task()
    time.sleep(5)  # Hope it's done by now?
    assert task_completed()

# Good: Mock or use proper async
@patch('myapp.background.time')
def test_async_operation(mock_time):
    start_background_task()
    # Test synchronously or use async/await
```

---

## Running Tests

### Basic Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test
pytest tests/unit/test_auth.py::test_login_success

# Run tests matching pattern
pytest -k "login"

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel
pytest -n auto
```

### Test Markers
```python
# Mark slow tests
@pytest.mark.slow
def test_large_dataset():
    pass

# Skip conditionally
@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_feature():
    pass

# Run only marked tests
# pytest -m slow
```

### Coverage Goals
- **Unit tests:** Aim for 80%+ coverage
- **Integration tests:** Cover critical paths
- **E2E tests:** Cover essential user journeys

Coverage is a metric, not a goal. Focus on meaningful tests over hitting numbers.

---

## Quick Checklist

Before committing tests, ensure:

- [ ] Tests run in < 1s for unit tests
- [ ] No external dependencies (network, database)
- [ ] Tests pass when run in isolation and in full suite
- [ ] Descriptive test names explain what's being tested
- [ ] One clear assertion per test
- [ ] All mocks are necessary and targeted
- [ ] No hardcoded paths or environment assumptions
- [ ] Test data is created within test or fixture
- [ ] Exceptions are tested with `pytest.raises`
- [ ] No `print()` statements or debug code

---

## Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [Test Driven Development by Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [The Art of Unit Testing](https://www.manning.com/books/the-art-of-unit-testing-third-edition)
- [Python Testing with pytest by Brian Okken](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)

---

**Remember:** Good tests give you confidence to refactor. If you're afraid to change code because tests might break, your tests need improvement, not your code.
