# Development Guide

This guide explains how to set up your development environment and contribute to the agency_toolkit project.

## 📋 Table of Contents

1. [Setup](#setup)
2. [Local Development](#local-development)
3. [Code Quality](#code-quality)
4. [Testing](#testing)
5. [Pre-commit Hooks](#pre-commit-hooks)
6. [Architecture Guide](#architecture-guide)
7. [Common Tasks](#common-tasks)

---

## Setup

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- git

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/agency_toolkit.git
   cd agency_toolkit
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .  # Installs in development mode
   pip install -e ".[dev]"  # Also installs dev dependencies
   ```

4. **Install pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Verify Installation

```bash
python -m pytest tests/ -q
# Should show: ✅ 166 passed, 5 skipped
```

---

## Local Development

### Running the CLI

```bash
# Image generation (uses free Pollinations.ai by default)
python -m agency_toolkit.cli_app image generate "A beautiful sunset"

# Social media post
python -m agency_toolkit.cli_app social generate "Check this out!" --dry-run

# Folder structure
python -m agency_toolkit.cli_app structure create "ClientName" "ProjectName" --dry-run

# Briefing generation
python -m agency_toolkit.cli_app briefing create --help
```

### Code Structure

```
agency_toolkit/
├── core/                          # Business logic
│   ├── social/                   # Social media generation
│   │   ├── generator.py         # Main orchestrator
│   │   ├── layout.py            # Position/dimension calculations
│   │   ├── rendering.py         # Image drawing logic
│   │   ├── validators.py        # Input validation
│   │   └── constants.py         # Magic numbers
│   ├── structure/                # Folder structure generation
│   ├── briefing/                 # PDF generation
│   └── mistral/                  # LLM integration
│
├── providers/                     # Plugin architecture for image generation
│   ├── base.py                   # Abstract ImageProvider class
│   ├── registry.py               # Provider discovery system
│   ├── replicate.py              # Replicate API provider
│   └── pollinations.py           # Pollinations.ai provider (FREE)
│
├── commands/                      # CLI command handlers
│   ├── image.py
│   ├── social.py
│   ├── structure.py
│   └── briefing.py
│
├── models.py                      # Pydantic validation models
├── config.py                      # Configuration loading
├── constants.py                   # Global constants
├── exceptions.py                  # Custom exceptions
└── utils.py                       # Utility functions
```

### Architecture Principles

1. **Thin CLI Wrappers**: Commands in `commands/` are minimal handlers that call core logic
2. **Plugin Architecture**: Image providers implement `ImageProvider` abstract base
3. **Backward Compatibility**: Old function locations still work via wrappers
4. **Custom Exceptions**: Use exceptions from `exceptions.py`, never generic `Exception`
5. **Constants Extraction**: All magic numbers in `constants.py` files

---

## Code Quality

### Type Checking

```bash
# Check types with mypy
mypy agency_toolkit/

# Fix common type errors
mypy agency_toolkit/ --show-error-codes | head -20
```

### Linting

```bash
# Check code style with Ruff
ruff check agency_toolkit/

# Automatically fix issues
ruff check agency_toolkit/ --fix
```

### Code Formatting

```bash
# Format code with Black
black agency_toolkit/

# Check formatting without changes
black --check agency_toolkit/
```

### Quality Audit

```bash
# Run comprehensive quality audit
python scripts/full_audit.py agency_toolkit/

# Output includes:
# - God functions (functions >50 lines)
# - Magic numbers (hardcoded values)
# - Missing error handling
# - Code duplication
```

---

## Testing

### Run All Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=agency_toolkit --cov-report=html
# View coverage report: open htmlcov/index.html
```

### Run Specific Test Suites

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# Provider tests only
python -m pytest tests/unit/providers/ -v

# Specific test file
python -m pytest tests/unit/test_social_unit.py -v

# Specific test class
python -m pytest tests/unit/test_social_unit.py::TestValidateColor -v

# Specific test
python -m pytest tests/unit/test_social_unit.py::TestValidateColor::test_validate_color_with_valid_named_color_returns_hex -v
```

### Writing Tests

1. **Unit Tests** (test isolated functions)
   - Location: `tests/unit/`
   - Mock external dependencies
   - Test edge cases and error paths
   - Aim for >80% code coverage

2. **Integration Tests** (test CLI behavior)
   - Location: `tests/integration/`
   - Run actual CLI commands
   - Verify file outputs
   - Test error messages

Example unit test:
```python
def test_validate_color_accepts_valid_colors(self) -> None:
    """Should accept valid color names and hex values."""
    assert validate_color("blue") == "#2E5EAA"
    assert validate_color("#FFFFFF") == "#FFFFFF"
```

Example integration test:
```python
def test_social_generate_creates_png(self, cli_runner, output_dir) -> None:
    """Test that social generate command creates PNG."""
    result = cli_runner.run("social", "generate", "Test post")
    assert result.returncode == 0
    assert (output_dir / "social").exists()
```

---

## Pre-commit Hooks

### Installation

```bash
pip install pre-commit
pre-commit install
```

### What Runs Automatically

Before each commit, pre-commit will:

1. **Black** - Auto-format code to PEP 8 style
2. **Ruff** - Lint and auto-fix issues
3. **mypy** - Type check code (can be slow)
4. **Trailing Whitespace** - Remove trailing spaces
5. **File Endings** - Ensure files end with newline
6. **YAML/TOML** - Validate configuration files

### Skip Hooks (if needed)

```bash
# Commit without pre-commit hooks
git commit --no-verify

# Not recommended - hooks catch issues!
```

### Run Manually

```bash
# Run all hooks on changed files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run mypy --all-files
```

---

## Architecture Guide

### Adding a New Command

1. Create handler in `commands/new_command.py`
2. Create core logic in `core/new_command/`
3. Import and register in `cli_app.py`

Example:
```python
# commands/new_command.py
@new_command.command("action")
def new_action(ctx: typer.Context, arg: str) -> None:
    from agency_toolkit.core.new_command import generate
    result = generate(arg)
    # Output result
```

### Adding a New Image Provider

1. Create provider class in `providers/new_provider.py`
2. Implement `ImageProvider` interface
3. Register in `image_gen.py`

Example:
```python
# providers/new_provider.py
from agency_toolkit.providers.base import ImageProvider

class NewProvider(ImageProvider):
    def generate(self, prompt, seed, width, height, config):
        # API call logic
        return {
            "path": str(image_path),
            "cost": cost,
            "seed": seed,
            "model": model_name,
            "provider": "new_provider",
        }

    def estimate_cost(self) -> float:
        return 0.05

    def supports_seed(self) -> bool:
        return True

    def max_dimensions(self) -> tuple[int, int]:
        return (2048, 2048)

# Register in image_gen.py
register_provider("new_provider", NewProvider)
```

### Adding a New Feature to core/social/

1. Add function to appropriate module (layout.py, rendering.py, etc.)
2. Import in generator.py
3. Add unit tests in `tests/unit/core/social/`
4. Verify no new god functions (>50 lines)

---

## Common Tasks

### Add a New Constant

```python
# agency_toolkit/constants.py (global) or
# agency_toolkit/core/social/constants.py (module-specific)

# Define constant
MAGIC_VALUE = 42

# Use in code
if result == MAGIC_VALUE:
    # ...
```

### Add Custom Error Handling

```python
# Define in exceptions.py if new
from agency_toolkit.exceptions import ConfigurationError

# Raise with context
try:
    validate_input()
except ValueError as e:
    raise ConfigurationError(f"Invalid config: {e}") from e
```

### Update Documentation

- User docs: Update README.md
- API docs: Add docstrings (Google style)
- Dev docs: Update this file

### Bump Version

```bash
# Update version in pyproject.toml
# version = "0.1.0" -> "0.2.0"

# Create git tag
git tag v0.2.0
git push --tags
```

---

## Troubleshooting

### Import Errors

```bash
# Reinstall package in development mode
pip install -e .
```

### Test Failures

```bash
# Run with full traceback
python -m pytest tests/unit/test_file.py -vv --tb=long

# Run single failing test
python -m pytest tests/unit/test_file.py::test_function -vv
```

### Pre-commit Issues

```bash
# Clear pre-commit cache
rm -rf .pre-commit .git/hooks/pre-commit

# Reinstall hooks
pre-commit install
```

### Type Checking Too Strict

```bash
# Run mypy in non-strict mode for development
mypy agency_toolkit/ --ignore-missing-imports

# Add type ignore comment for specific lines
x = some_untyped_function()  # type: ignore
```

---

## CI/CD Pipeline

The project uses GitHub Actions for automated testing and quality checks.

**Workflows run on:**
- Every push to main/master/develop
- Every pull request

**Jobs:**
1. **Lint** - Ruff, Black formatting checks
2. **Type Check** - mypy static type analysis
3. **Test** - pytest (Python 3.10, 3.11, 3.12)
4. **Quality Audit** - Code quality metrics
5. **Build** - Package building verification

**PR Requirements:**
- All tests must pass
- Linting must pass
- Build must succeed

---

## Performance Considerations

1. **Slow Imports**: Avoid importing heavy modules at module level
2. **Slow Tests**: Integration tests timeout at 30 seconds
3. **Type Checking**: mypy is slow, skipped in CI
4. **Font Loading**: Known issue with social command font hang

---

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Code Style](https://black.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)

---

**Last Updated**: November 7, 2025
**Maintained By**: Claude Code
