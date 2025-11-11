# PROJECT CONTEXT HUB

> **Purpose:** This document provides essential project context to AI assistants. Load this at the beginning of development sessions to ensure consistent, informed responses.
>
> **Last Updated:** 2025-11-08
> **Project Version:** 0.4.0

---

## 📑 INDEX - IMPORTANT FILES

### Core Documentation
- `docs/BLUEPRINT.yaml` - System architecture and design decisions
- `docs/IMPLEMENTATION.yaml` - Detailed module implementation guide
- `docs/agency_toolkit_roadmap.md` - High-level development and refactoring roadmap
- `ARCHITECTURAL_OVERVIEW.md` - Auto-generated analysis of the current architecture

### Code References
- `agency_toolkit/cli_app.py` - Application entry point
- `agency_toolkit/core/orchestrator.py` - Core business logic for the workflow engine
- `agency_toolkit/config.py` & `config.toml.example` - Configuration files
- `registry/seeds/solutions.json` - Data source for all executable workflows

### Development Guides
- `DEVELOPMENT.md` - Development workflow and standards
- `tests/README.md` - Testing strategy and test suite location
- `CONTRIBUTING.md` - Contribution guidelines (Standard)

---

## 🎯 PROJECT OVERVIEW

### Project Name
**agency-toolkit**

### Mission Statement
An AI-driven CLI platform for creative agencies that orchestrates and automates repetitive workflows like asset generation, content creation, and project setup.

### Current Phase
- [ ] Prototype / MVP
- [X] Active Development (Refactoring & Hardening)
- [ ] Production / Maintenance
- [ ] Legacy / Sunset

### Key Stakeholders
- **Product Owner:** You (the user)
- **Tech Lead:** You (the user)
- **Primary Maintainers:** You and me (Project Steward AI)

---

## 🛠️ TECHNOLOGY STACK

### Core Technologies
| Category | Technology | Version | Notes |
|----------|-----------|---------|-------|
| Language | Python | 3.10+ | As defined in `pyproject.toml` |
| Framework | Typer | 0.9.0+ | For building the CLI application |
| Database | N/A | - | The project is file-based; no database is used. |
| Cache | N/A | - | Caching is planned but not yet implemented. |

### Frontend (if applicable)
| Technology | Version | Notes |
|-----------|---------|-------|
| N/A | - | This is a command-line interface (CLI) application. |

### Infrastructure
| Component | Technology | Notes |
|-----------|-----------|-------|
| Cloud Provider | N/A | The tool is platform-agnostic and runs locally. |
| CI/CD | GitHub Actions | Defined in `.github/workflows/ci.yml`. |
| Monitoring | N/A | - |
| Logging | Python `logging` | Configured in `agency_toolkit/logger.py`. |

### Development Tools
- **Package Manager:** `pip`
- **Linter:** `Ruff`
- **Formatter:** `Black`
- **Type Checker:** `mypy` (in strict mode)
- **Test Framework:** `pytest`

### Prohibited Technologies
> **DO NOT USE** the following without explicit team approval:
- **New external libraries:** The goal is to keep the dependency footprint small. Any new library must be justified and approved.
- **Direct file system access outside of `core` modules:** All file I/O should be handled by core logic, not in the command layer.

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Architecture
```mermaid
graph TD
    subgraph User
        A[CLI User]
    end

    subgraph CLI Layer
        B[commands/os.py]
    end

    subgraph Orchestration
        C[core/orchestrator.py]
        D[core/workflow_loader.py]
        E[tasks/registry.py]
    end

    subgraph Task Handlers
        F[tasks/ai_handler.py]
        G[tasks/social_handler.py]
    end

    subgraph Core Logic
        H[core/social/generator.py]
        I[core/briefing/generator.py]
    end

    subgraph Providers
        J[providers/provider_loader.py]
        K[providers/mistral_provider.py]
        L[providers/pollinations.py]
    end

    A --> B;
    B --> C;
    B --> D;
    C --> E;
    E --> F;
    E --> G;
    F --> J;
    G --> H;
    J --> K;
    J --> L;
```

### Design Patterns
- **Strategy Pattern:** Used extensively for `Task Handlers` (`tasks/`) and `Providers` (`providers/`). The orchestrator and core logic depend on an abstract interface, and the concrete implementation is chosen at runtime. This makes the system highly extensible.
- **Singleton Pattern:** Used in `core/reporter.py` via `get_reporter()` to ensure a single, consistent output formatter is used throughout a command's lifecycle.
- **Layered Architecture:** The project is clearly separated into distinct layers: `Commands` (UI), `Core` (Business Logic), `Tasks` (Workflow Steps), and `Providers` (External Services).

### Key Architectural Decisions
1. **Orchestrator with Task Handlers**
   - **Context:** The initial design had business logic mixed in the command layer.
   - **Decision:** A central orchestrator (`core/orchestrator.py`) was introduced, which dispatches work to registered "Task Handlers" in the `tasks/` directory.
   - **Consequences:** Massively improved separation of concerns and extensibility. Adding new "tools" to a workflow only requires creating a new handler, not modifying the orchestrator.

2. **Provider Abstraction Layer**
   - **Context:** The tool needed to support multiple external AI and image services.
   - **Decision:** An adapter layer was created in `providers/` using Abstract Base Classes (`TextProvider`, `ImageProvider`).
   - **Consequences:** The core logic is completely decoupled from the specific implementation of any external API (e.g., Mistral vs. Google vs. Ollama).

3. **Circular Dependency Refactoring**
   - **Context:** A circular import was discovered between `commands/os.py` and `core/os_interactive.py`.
   - **Decision:** The shared utility (`interactive_utils.py`) was moved down into the `core/` layer, breaking the cycle and restoring a clean, unidirectional dependency flow.
   - **Consequences:** Improved architectural integrity and enabled proper unit testing of the `os_interactive` module.

---

## 📁 PROJECT STRUCTURE

### Directory Layout
```
agency_toolkit/
├── cli_app.py           # Main CLI entry point
├── commands/            # User-facing CLI command definitions
├── config.py            # Default application constants
├── core/                # Core business logic, decoupled from UI
├── exceptions.py        # Custom exception classes
├── models.py            # Pydantic data models
├── providers/           # Plugin system for external APIs
├── tasks/               # Task handlers for the orchestrator
└── utils.py             # Shared utility functions
tests/
├── unit/
├── integration/
└── quality/
docs/
└── ...
registry/
└── seeds/               # Data files for workflows (solutions.json)
```

### Module Responsibilities
- **`commands/`** - Handles user input parsing and high-level command flow. Delegates all real work.
- **`core/`** - Contains the pure, reusable business logic for generating artifacts (images, PDFs, etc.) and orchestrating workflows.
- **`tasks/`** - Acts as the "glue" between the orchestrator and the core logic. Each handler implements the logic for a single "tool" in a workflow.
- **`providers/`** - Manages all communication with external APIs (Mistral, Google, Pollinations, etc.).

### Critical Files
- **`core/orchestrator.py`** - The engine that runs workflows. Modify with extreme care.
- **`tasks/base.py`** - Defines the `TaskHandler` interface. Changes here affect all tasks.
- **`registry/seeds/solutions.json`** - Defines all available workflows. Changes here directly impact the `os init` command.

---

## 📋 CODE CONVENTIONS

### Naming Conventions
```python
# Files
module_name.py          # Snake case for modules

# Variables & Functions
user_count = 0          # Snake case for variables
def calculate_total()   # Snake case for functions

# Classes
class UserService:      # PascalCase for classes

# Constants
MAX_RETRY_COUNT = 3     # UPPER_CASE for constants
```

### Code Style Rules
- **Indentation:** 4 spaces
- **Line Length:** 88 characters max (enforced by Black)
- **Imports:** Grouped by stdlib/third-party/local (enforced by Ruff)
- **Docstrings:** Google style is preferred.
- **Type Hints:** Required for all function signatures.

### Error Handling
```python
# Specific exceptions should be caught. Avoid broad `except Exception:`.
try:
    # Business logic that can fail
    result = some_provider_call()
except AIProviderError as e:
    logger.error(f"AI call failed: {e}")
    raise CustomException("Could not get AI completion.") from e
```

### Logging Standards
```python
# Use the standard Python logging module.
logger.debug("Detailed diagnostic info for developers.")
logger.info("Confirmation that things are working as expected.")
logger.warning("An unexpected event occurred, but the software will continue running.")
logger.error("A serious problem, the software may be unable to perform some function.")
```

---

## 🔒 SECURITY GUIDELINES

### Authentication & Authorization
- **Auth Method:** N/A. The tool is a local CLI and does not have its own user authentication system.
- **Session Management:** N/A.
- **Permission Model:** Relies on the user's file system permissions.

### Sensitive Data Handling
- **API Keys:** Must be loaded from environment variables (e.g., `MISTRAL_API_KEY`, `GOOGLE_API_KEY`).
- **Secrets Management:** The tool does not manage secrets; it reads them from the environment.
- **PII Data:** The tool processes user-provided text, which could contain PII. It does not store this data persistently beyond creating output artifacts.

### Security Requirements
- ✅ All external inputs (from files like CSV/JSON) must be validated.
- ✅ API keys must be loaded from environment variables.
- ❌ **Never** log sensitive data (API keys, user content).
- ❌ **Never** commit secrets to version control.

---

## 🧪 TESTING STRATEGY

### Test Coverage Requirements
- **Unit Tests:** Target coverage for new/refactored code is 80%+.
- **Integration Tests:** Key user flows (e.g., `os init`, `social generate --from-csv`) must be covered.
- **E2E Tests:** N/A at this stage.

### Test Structure
```
tests/
├── unit/           # Fast, isolated tests for core logic and tasks
├── integration/    # Tests CLI commands and multi-module workflows
└── quality/        # Semantic and architectural tests
```

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=agency_toolkit
```

### Test Data
- **Fixtures:** Located in `tests/conftest.py` and `tests/fixtures/`.
- **Mocking:** `unittest.mock` is used to mock external API calls and file system operations.
- **Test Database:** N/A.

---

## 🚀 DEPLOYMENT

### Environments
| Environment | Purpose | URL | Deploy Method |
|------------|---------|-----|---------------|
| Development | Local dev | localhost | Manual (`pip install -e .`) |
| Staging | N/A | - | - |
| Production | PyPI | pypi.org | CI/CD on Git tag |

### Deployment Process
1. Create PR with changes.
2. Pass all CI checks (lint, types, tests).
3. Code review approval.
4. Merge to `main`.
5. Create a new Git tag (e.g., `v0.5.0`).
6. Push the tag to trigger the automated release workflow on GitHub Actions, which publishes to PyPI.

### Environment Variables
```bash
# Required for AI features
MISTRAL_API_KEY=[Your Mistral API key]
GOOGLE_API_KEY=[Your Google API key]

# Optional for image generation
REPLICATE_API_TOKEN=[Your Replicate API token]
```

---

## 🗄️ DATA MODELS

### Core Entities
#### `Task` (from `solutions.json`)
```json
{
    "tool": "string",         // Name of the handler to execute (e.g., "ai", "social")
    "params": "dict",         // Parameters for the task, may contain placeholders
    "output_key": "string"    // Optional key to store the result in the context
}
```

#### `SocialTemplate` (from `models.py`)
```python
class SocialTemplate(BaseModel):
    font_face: str
    font_size_ratio: float | None  # e.g., 0.06 = 6% of image height
    padding_ratio: float         # e.g., 0.1 = 10% margin
    # ... and other responsive layout fields
```

---

## 🔗 EXTERNAL DEPENDENCIES

### Third-Party APIs
| Service | Purpose | Auth Method | Rate Limits | Docs |
|---------|---------|-------------|-------------|------|
| Mistral AI | Text Generation | API Key | Yes (handled by resilience module) | [URL] |
| Google GenAI | Text Generation | API Key | Yes (handled by resilience module) | [URL] |
| Replicate | Image Generation | API Token | Yes (handled by resilience module) | [URL] |
| Pollinations | Image Generation | None | Yes (informal) | [URL] |

---

## 🐛 KNOWN ISSUES & TECHNICAL DEBT

### Active Issues
1. **`torch` Security Vulnerability**
   - **Impact:** A CVE remains in the `torch` dependency.
   - **Workaround:** None.
   - **Planned Fix:** Blocked until PyTorch 2.6.0+ is available for macOS x86_64.

2. **Broken `pre-commit` Hooks**
   - **Impact:** Code quality checks are not being automatically enforced before commits.
   - **Workaround:** Manually running `ruff` and `black`.
   - **Planned Fix:** `P2` priority in the current roadmap.

### Technical Debt
1. **Configuration System**
   - **Location:** `agency_toolkit/config.py`, `agency_toolkit/utils.py`
   - **Reason:** The current system is a mix of a single Pydantic model and a custom TOML loader. It lacks environment awareness and structure.
   - **Priority:** High (scheduled for `Epic 2.2`, to be replaced by `phoenix_config`).

2. **Prompt Management**
   - **Location:** `agency_toolkit/config.py`, `registry/seeds/solutions.json`
   - **Reason:** Prompts are hardcoded as strings in various places.
   - **Priority:** High (scheduled for `Epic 2.1`, to be replaced by `prompt_registry`).

---

## 📊 PERFORMANCE CONSIDERATIONS

### Performance Targets
- **API Response Time:** Not applicable (CLI tool).
- **CLI Command Execution:** Should feel responsive (<2s for non-API tasks).
- **Batch Processing:** Should be significantly faster than running commands individually.

### Known Bottlenecks
- **AI/Image API Calls:** These are network-bound and can be slow. Mitigation is planned via async processing (`Epic 3.2`).
- **Font Loading:** Can be slow on some systems. Mitigated with a font fallback mechanism.

---

## 📞 SUPPORT & ESCALATION

### Getting Help
- **Documentation:** `docs/`, `README.md`, `ARCHITECTURAL_OVERVIEW.md`
- **Team Chat:** This CLI session.
- **Issue Tracker:** N/A.

---

## 🔄 REPO MAP

> **Note:** This section contains the output of a code indexing tool. It provides the AI with a high-level view of the entire codebase structure.

### Generation Command
```bash
# glob agency_toolkit/**/*.py | read_many_files | parse
```

### Map Content
```
[The full content of CODEBASE_INTELLIGENCE_REPORT.md is pasted here]
```

---

## ✅ CONTEXT HUB CHECKLIST

Before loading this Context Hub, ensure:
- [X] All placeholder values `[LIKE_THIS]` are replaced with actual values
- [X] Index section points to existing, current files
- [X] Technology stack versions are up to date
- [X] Repo Map is freshly generated
- [X] Known issues section reflects current state
- [X] Contact information is accurate

---

*This Context Hub should be reviewed and updated quarterly or after major architectural changes.*
