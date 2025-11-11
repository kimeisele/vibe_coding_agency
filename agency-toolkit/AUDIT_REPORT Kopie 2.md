# Agency Toolkit - Audit Report (2025-11-08)

This report provides a comprehensive analysis of the Agency Toolkit Python project, highlighting areas for improvement in code quality, structure, and maintainability.

## 1. CODE QUALITY METRICS

### Summary

| Metric | Result | Notes |
| --- | --- | --- |
| **Avg. Cyclomatic Complexity** | B (8.79) | Generally good, but some functions are overly complex. |
| **Maintainability Index** | A (All files) | Excellent. All files are rated as highly maintainable. |
| **Test Coverage** | 68% | **CRITICAL**: 35 tests are failing, blocking a true coverage assessment. |
| **Lines of Code** | ~8700 LOC | Moderate project size. |

### Test Failures Analysis

A significant number of tests (35) are failing with a `RuntimeError: Type not yet supported: <class 'agency_toolkit.core.reporter.Reporter'>` originating from within the `typer` library. This suggests a fundamental issue with how a custom class (`Reporter`) is being used as a type hint in a Typer command function, which is not supported. This is a **critical bug** that prevents proper testing and validation of a large part of the application.

### Modules of Concern (High Complexity / Lines of Code)

The following modules warrant review due to high cyclomatic complexity (>10) or being over 200 lines of code. This can indicate they have too many responsibilities and might be difficult to test and maintain.

| File Path | Lines of Code | Avg. Complexity | What it does (Brief) |
| --- | --- | --- | --- |
| `agency_toolkit/commands/info.py` | 485 | B (8.79) | Provides CLI commands to display information about the toolkit. |
| `agency_toolkit/commands/validate.py` | 395 | C (11.0) | Handles validation of project snapshots and configurations. |
| `agency_toolkit/core/briefing/pdf_sections.py` | 379 | B (8.79) | Generates different sections of the PDF briefing document. |
| `agency_toolkit/commands/os.py` | 379 | B (8.79) | Orchestrates OS-level commands and file system operations. |
| `agency_toolkit/core/os_interactive.py` | 321 | B (8.79) | Manages interactive prompts for the OS commands. |
| `agency_toolkit/utils.py` | 319 | B (8.79) | Contains various utility functions used across the application. |
| `agency_toolkit/models.py` | 300 | N/A | Defines the Pydantic data models for the application. |
| `agency_toolkit/core/reporter.py` | 254 | B (8.79) | Handles reporting of progress and results to the console. |
| `agency_toolkit/core/orchestrator.py` | 253 | C (11.0) | Coordinates the execution of tasks and workflows. |
| `agency_toolkit/commands/social.py` | 252 | B (8.79) | Command to generate social media posts. |
| `agency_toolkit/core/os_executor.py` | 251 | B (8.79) | Executes the OS-level operations defined by the orchestrator. |
| `agency_toolkit/providers/mistral_provider.py` | 250 | B (8.79) | Provider for interacting with the Mistral AI API. |
| `agency_toolkit/core/resilience.py` | 240 | B (8.79) | Implements retry logic and error handling for network requests. |
| `agency_toolkit/core/social/batch.py` | 233 | B (8.79) | Processes batch generation of social media posts from CSV/JSON. |

### Test Coverage Gaps (Top 10)

Total coverage is **68%**. The following files have the most significant number of missed lines, indicating they are undertested.

| File | Stmts | Miss | Cover | Missing lines |
| --- | --- | --- | --- | --- |
| `agency_toolkit/core/os_interactive.py` | 101 | 84 | 17% | 31-46, 61-81, 96-115, 133-155, 167-170, 179-195, 224-272, 289-321 |
| `agency_toolkit/commands/ai.py` | 70 | 57 | 19% | 30-39, 61-79, 137-210 |
| `agency_toolkit/core/reporter.py` | 99 | 78 | 21% | 23-24, 33-39, 51-58, 67-73, 82-88, 96-97, 105-108, 117-125, 135-152, 164-177, 186-190, 198-199, 211-216, 224-225, 242-244, 254 |
| `agency_toolkit/core/os_executor.py` | 54 | 43 | 20% | 29-36, 52-65, 81-89, 111-126, 142-154, 178-181, 228-244 |
| `agency_toolkit/commands/briefing.py` | 42 | 32 | 24% | 52-109 |
| `agency_toolkit/core/social/batch.py` | 76 | 66 | 13% | 43-80, 105-152, 179-228 |
| `agency_toolkit/core/briefing/interactive.py` | 36 | 33 | 8% | 17-64 |
| `agency_toolkit/providers/ollama_provider.py` | 36 | 25 | 31% | 30, 56-111, 123, 131 |
| `agency_toolkit/logger.py` | 18 | 13 | 28% | 20-44 |
| `agency_toolkit/cli_app.py` | 45 | 23 | 49% | 29-31, 51-79, 93, 98 |

## 2. PROJECT STRUCTURE

```
__init__.py     config.py       image_gen.py    tasks
__pycache__     constants.py    logger.py       utils.py
cli_app.py      core            models.py
commands        exceptions.py   providers

agency_toolkit//__pycache__:
__init__.cpython-311.pyc        image_gen.cpython-313.pyc
__init__.cpython-313.pyc        logger.cpython-311.pyc
briefing.cpython-311.pyc        logger.cpython-313.pyc
briefing.cpython-313.pyc        mistral.cpython-311.pyc
cli_app.cpython-311.pyc         mistral.cpython-313.pyc
cli_app.cpython-313.pyc         models.cpython-311.pyc
config.cpython-311.pyc          models.cpython-313.pyc
config.cpython-313.pyc          social.cpython-311.pyc
constants.cpython-311.pyc       social.cpython-313.pyc
constants.cpython-313.pyc       structure.cpython-311.pyc
exceptions.cpython-311.pyc      structure.cpython-313.pyc
exceptions.cpython-313.pyc      utils.cpython-311.pyc
image_gen.cpython-311.pyc       utils.cpython-313.pyc

agency_toolkit//commands:
__init__.py             interactive_utils.py
__pycache__             os.py
ai.py                   social.py
briefing.py             structure.py
image.py                validate.py
info.py

agency_toolkit//commands/__pycache__:
__init__.cpython-311.pyc
__init__.cpython-313.pyc
ai.cpython-311.pyc
ai.cpython-313.pyc
briefing.cpython-311.pyc
briefing.cpython-313.pyc
image.cpython-311.pyc
image.cpython-313.pyc
info.cpython-311.pyc
info.cpython-313.pyc
interactive_utils.cpython-311.pyc
interactive_utils.cpython-313.pyc
mistral.cpython-311.pyc
mistral.cpython-313.pyc
os.cpython-311.pyc
os.cpython-313.pyc
social.cpython-311.pyc
social.cpython-313.pyc
structure.cpython-311.pyc
structure.cpython-313.pyc
validate.cpython-311.pyc

agency_toolkit//core:
__init__.py             os_executor.py
__pycache__             os_interactive.py
briefing                reporter.py
dependency_resolver.py  resilience.py
discovery.py            social
mistral                 structure
orchestrator.py         workflow_loader.py

agency_toolkit//core/__pycache__:
__init__.cpython-311.pyc
__init__.cpython-313.pyc
dependency_resolver.cpython-311.pyc
dependency_resolver.cpython-313.pyc
discovery.cpython-311.pyc
grand_agency_registry.cpython-311.pyc
orchestrator.cpython-311.pyc
orchestrator.cpython-313.pyc
os_executor.cpython-311.pyc
os_executor.cpython-313.pyc
os_interactive.cpython-311.pyc
os_interactive.cpython-313.pyc
reporter.cpython-311.pyc
resilience.cpython-311.pyc
resilience.cpython-313.pyc
task_handlers.cpython-311.pyc
workflow_loader.cpython-311.pyc
workflow_loader.cpython-313.pyc

agency_toolkit//core/briefing:
__init__.py     generator.py    models.py       templates.py
__pycache__     interactive.py  pdf_sections.py
constants.py    io.py           pdf_writer.py

agency_toolkit//core/briefing/__pycache__:
__init__.cpython-311.pyc        io.cpython-313.pyc
__init__.cpython-313.pyc        models.cpython-311.pyc
constants.cpython-311.pyc       models.cpython-313.pyc
constants.cpython-313.pyc       pdf_sections.cpython-311.pyc
generator.cpython-311.pyc       pdf_sections.cpython-313.pyc
generator.cpython-313.pyc       pdf_writer.cpython-311.pyc
interactive.cpython-311.pyc     pdf_writer.cpython-313.pyc
interactive.cpython-313.pyc     templates.cpython-311.pyc
io.cpython-311.pyc              templates.cpython-313.pyc

agency_toolkit//core/mistral:
__init__.py

agency_toolkit//core/social:
__init__.py     batch.py        layout.py       validators.py
__pycache__     constants.py    rendering.py
background.py   generator.py    templates.py

agency_toolkit//core/social/__pycache__:
__init__.cpython-311.pyc        generator.cpython-313.pyc
__init__.cpython-313.pyc        layout.cpython-311.pyc
background.cpython-311.pyc      layout.cpython-313.pyc
background.cpython-313.pyc      rendering.cpython-311.pyc
batch.cpython-311.pyc           rendering.cpython-313.pyc
batch.cpython-313.pyc           templates.cpython-311.pyc
constants.cpython-311.pyc       templates.cpython-313.pyc
constants.cpython-313.pyc       validators.cpython-311.pyc
generator.cpython-311.pyc       validators.cpython-313.pyc

agency_toolkit//core/structure:
__init__.py     generator.py    validators.py
__pycache__     templates.py    writer.py

agency_toolkit//core/structure/__pycache__:
__init__.cpython-311.pyc        templates.cpython-313.pyc
__init__.cpython-313.pyc        validators.cpython-311.pyc
generator.cpython-311.pyc       validators.cpython-313.pyc
generator.cpython-313.pyc       writer.cpython-311.pyc
templates.cpython-311.pyc       writer.cpython-313.pyc

agency_toolkit//providers:
__init__.py             ollama_provider.py
__pycache__             pollinations.py
base.py                 provider_loader.py
google_provider.py      replicate.py
mistral_provider.py

agency_toolkit//providers/__pycache__:
__init__.cpython-311.pyc
__init__.cpython-313.pyc
base.cpython-311.pyc
base.cpython-313.pyc
google_provider.cpython-311.pyc
google_provider.cpython-313.pyc
mistral_provider.cpython-311.pyc
mistral_provider.cpython-313.pyc
ollama_provider.cpython-311.pyc
ollama_provider.cpython-313.pyc
pollinations.cpython-311.pyc
pollinations.cpython-313.pyc
provider_loader.cpython-311.pyc
provider_loader.cpython-313.pyc
registry.cpython-311.pyc
registry.cpython-313.pyc
replicate.cpython-311.pyc
replicate.cpython-313.pyc

agency_toolkit//tasks:
__init__.py             briefing_handler.py
__pycache__             registry.py
ai_handler.py           social_handler.py
base.py                 structure_handler.py

agency_toolkit//tasks/__pycache__:
__init__.cpython-311.pyc
__init__.cpython-313.pyc
ai_handler.cpython-311.pyc
ai_handler.cpython-313.pyc
base.cpython-311.pyc
base.cpython-313.pyc
briefing_handler.cpython-311.pyc
briefing_handler.cpython-313.pyc
registry.cpython-311.pyc
registry.cpython-313.pyc
social_handler.cpython-311.pyc
social_handler.cpython-313.pyc
structure_handler.cpython-311.pyc
structure_handler.cpython-313.pyc
```
