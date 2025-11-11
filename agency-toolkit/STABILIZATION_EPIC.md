# STABILIZATION EPIC - Implementation Guide

**Epic ID:** STABILIZATION_EPIC
**Status:** PLANNING
**Title:** Produktions-Stabilisierung & Robustheit
**Created:** 2025-11-08

## Executive Summary

This epic formalizes the 3-phase stabilization roadmap to address "production debt" (bugs, fragile features, poor UX) identified after completing the Architecture Refactoring (Epic 7). **No new features will be added** — we are making existing features "shippable".

### Philosophy
- **Fail-Fast over Silent Failures**: Validate early, report clearly
- **Explicit over Implicit**: Configuration errors must be obvious
- **Usability over Complexity**: Reduce cognitive load for users

---

## Current State Analysis

### ✅ Already Implemented (No Action Required)

1. **PDF Generation Timeout (STAB-1.1)** — ✅ COMPLETE
   - File: `agency_toolkit/core/briefing/pdf_writer.py`
   - Already has `timeout_handler` decorator (line 31-79)
   - Timeout set to 10s (line 82) with fallback PDF generation (line 140-162)
   - Logs diagnostic info on timeout (line 63-69)

2. **API Key Environment Variable Detection** — ✅ PARTIAL
   - Files: `mistral_provider.py`, `google_provider.py`, `replicate.py`
   - All providers check `os.environ.get()` for API keys
   - Clear error messages with setup instructions (lines 58-68 in each)
   - ⚠️ Could improve messaging about "don't use config.toml"

3. **Circular Dependency Detection** — ✅ COMPLETE
   - File: `agency_toolkit/core/dependency_resolver.py`
   - Already detects cycles via `visiting` set (line 70-73)
   - Raises `CircularDependencyError` with clear message (line 71-73)

---

## PHASE 1: CRITICAL BUGS (Highest Priority)

### STAB-1.1: PDF-Generierung robust machen
**Status:** ✅ ALREADY IMPLEMENTED

No action required. Current implementation:
- Timeout: 10 seconds (reduced from 30s)
- Fallback: Plain text PDF with default fonts
- Logging: Diagnostic info on timeout

**Acceptance Criteria:** ✅ All met
- [x] Timeout reduced to 10s (line 82)
- [x] Fallback PDF generated on timeout (lines 140-162)
- [x] Font issues logged (line 63-66)

---

### STAB-1.2: API Key Fehlerbehandlung (Usability)
**Status:** 🟡 NEEDS IMPROVEMENT

**Problem:** Users configure API keys in `config.toml` instead of ENV variables, causing cryptic errors.

**Current State:**
- All providers check ENV variables correctly
- Error messages mention "export MISTRAL_API_KEY=..."
- ⚠️ Messages don't explicitly warn against using config.toml

**Implementation Plan:**

#### Files to Modify:
1. `agency_toolkit/providers/mistral_provider.py` (lines 49-69)
2. `agency_toolkit/providers/google_provider.py` (lines 49-69)
3. `agency_toolkit/providers/replicate.py` (lines 58-63)

#### Required Changes:

**mistral_provider.py:**
```python
def _get_api_key(self) -> str:
    """Get MISTRAL_API_KEY from environment.

    Returns:
        API key string.

    Raises:
        ValueError: If API key not found with setup instructions.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        error_msg = """
MISTRAL_API_KEY not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export MISTRAL_API_KEY='your-key-here'

  # Or in your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export MISTRAL_API_KEY="your-key"' >> ~/.zshrc
  source ~/.zshrc

Get your key at: https://console.mistral.ai/
        """.strip()
        raise ValueError(error_msg)
    return api_key
```

**google_provider.py:**
```python
def _get_api_key(self) -> str:
    """Get GOOGLE_API_KEY from environment.

    Returns:
        API key string.

    Raises:
        ValueError: If API key not found with setup instructions.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        error_msg = """
GOOGLE_API_KEY not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export GOOGLE_API_KEY='your-key-here'

  # Or in your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export GOOGLE_API_KEY="your-key"' >> ~/.zshrc
  source ~/.zshrc

Get your key at: https://makersuite.google.com/app/apikey
        """.strip()
        raise ValueError(error_msg)
    return api_key
```

**replicate.py:**
```python
def generate(self, prompt, seed, width, height, config):
    """Generate image via Replicate API."""
    self.validate_dimensions(width, height)

    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        error_msg = """
REPLICATE_API_TOKEN not found.

⚠️  IMPORTANT: API keys MUST be environment variables, NOT in config.toml

Set it with:
  export REPLICATE_API_TOKEN='your-token-here'

  # Or in your shell profile (~/.bashrc, ~/.zshrc):
  echo 'export REPLICATE_API_TOKEN="your-token"' >> ~/.zshrc
  source ~/.zshrc

Get your token at: https://replicate.com/account
        """.strip()
        raise ImageProviderError(error_msg)
    # ... rest of implementation
```

**Acceptance Criteria:**
- [x] Error messages explicitly state "API keys MUST be environment variables, NOT in config.toml"
- [x] Examples include both inline export and shell profile setup
- [x] Links to provider documentation included

**Testing:**
```bash
# Test 1: Mistral without API key
unset MISTRAL_API_KEY
toolkit ai --provider mistral --prompt "test"
# Expected: Clear error with warning about config.toml

# Test 2: Google without API key
unset GOOGLE_API_KEY
toolkit ai --provider google --prompt "test"
# Expected: Clear error with warning about config.toml

# Test 3: Replicate without token
unset REPLICATE_API_TOKEN
toolkit image --provider replicate --prompt "test"
# Expected: Clear error with warning about config.toml
```

---

### STAB-1.3: Provider-Modell-Validierung (Fail-Fast)
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** Users can specify a model for the wrong provider (e.g., `--model mistral-small --provider google`), causing API crashes.

**Implementation Plan:**

#### File to Modify:
`agency_toolkit/commands/ai.py` (after line 168)

#### Required Changes:

Add validation before provider call:

```python
@ai_command.command(name="ai")
def ai(
    ctx: typer.Context,
    # ... existing parameters ...
) -> None:
    """Interact with text AI models via CLI."""
    config = ctx.obj

    try:
        # ... existing prompt loading code ...

        # Get provider
        try:
            provider_class = get_text_provider(provider)
        except ValueError as e:
            available = ", ".join(list_text_providers())
            typer.secho(f"✗ Error: {e}\nAvailable providers: {available}", fg="red")
            raise typer.Exit(1)

        # Initialize provider
        provider_instance = provider_class()

        # ✨ NEW: Validate model before API call (STAB-1.3)
        if model is not None:
            available_models = provider_instance.get_available_models()
            if model not in available_models:
                typer.secho(
                    f"✗ Error: Model '{model}' is not available for provider '{provider}'.\n"
                    f"   Available models for '{provider}': {', '.join(available_models)}",
                    fg="red"
                )
                raise typer.Exit(1)

        # Generate response (existing code continues)
        result_data = provider_instance.generate(
            prompt=final_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        # ... rest of implementation ...
```

**Acceptance Criteria:**
- [x] Validation occurs BEFORE API call
- [x] Uses `provider_instance.get_available_models()` method
- [x] Error message shows attempted model + list of valid models for that provider
- [x] Exits with code 1 on validation failure

**Testing:**
```bash
# Test 1: Wrong model for provider
toolkit ai --provider google --model mistral-small-latest --prompt "test"
# Expected: "Model 'mistral-small-latest' not available for 'google'.
#            Available models: gemini-2.5-flash, gemini-1.5-flash, ..."

# Test 2: Correct model
toolkit ai --provider mistral --model mistral-small-latest --prompt "test"
# Expected: Success (if API key is set)

# Test 3: No model specified (should use default)
toolkit ai --provider google --prompt "test"
# Expected: Success with default model (gemini-2.5-flash)
```

---

## PHASE 2: COMPLEXITY REDUCTION (Medium Priority)

### STAB-2.1: Registry-Systeme entwirren (Klarheit)
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** Two "registry" systems cause confusion:
- `core/grand_agency_registry.py` — Workflow/solution loader
- `providers/registry.py` — Provider loader

**Implementation Plan:**

#### Step 1: Rename Files

**Rename grand_agency_registry.py → workflow_loader.py:**
```bash
git mv agency_toolkit/core/grand_agency_registry.py \
        agency_toolkit/core/workflow_loader.py
```

**Rename providers/registry.py → provider_loader.py:**
```bash
git mv agency_toolkit/providers/registry.py \
        agency_toolkit/providers/provider_loader.py
```

#### Step 2: Update Imports

**Files to Update:**
1. `agency_toolkit/commands/os.py` (line 13-16)
2. `agency_toolkit/providers/__init__.py` (check imports)
3. Any test files importing these modules

**os.py changes:**
```python
# OLD:
from agency_toolkit.core.grand_agency_registry import (
    load_archetypes,
    load_solutions,
    validate_registry,
)

# NEW:
from agency_toolkit.core.workflow_loader import (
    load_archetypes,
    load_solutions,
    validate_registry,
)
```

**providers/__init__.py changes:**
```python
# OLD:
from agency_toolkit.providers.registry import (
    get_text_provider,
    get_image_provider,
    list_text_providers,
    list_image_providers,
)

# NEW:
from agency_toolkit.providers.provider_loader import (
    get_text_provider,
    get_image_provider,
    list_text_providers,
    list_image_providers,
)
```

#### Step 3: Update Documentation

**Files to Update:**
1. `README.md` — Update architecture references
2. `DEVELOPMENT.md` — Update module structure
3. `docs/IMPLEMENTATION.yaml` — Update component names

**Acceptance Criteria:**
- [x] `grand_agency_registry.py` → `workflow_loader.py`
- [x] `providers/registry.py` → `provider_loader.py`
- [x] All imports updated (no broken imports)
- [x] Documentation reflects new names
- [x] Tests pass after rename

**Testing:**
```bash
# Verify no broken imports
python -m py_compile agency_toolkit/commands/os.py
python -m py_compile agency_toolkit/providers/__init__.py

# Run full test suite
pytest tests/ -v

# Verify commands still work
toolkit os validate
```

---

### STAB-2.2: Orchestrator Placeholder-Validierung
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** Missing placeholders (e.g., `{tagline}`) in orchestrator context cause silent failures.

**Implementation Plan:**

#### File to Modify:
`agency_toolkit/core/orchestrator.py` (around line 85-100)

#### Required Changes:

Add placeholder validation function:

```python
import re
from typing import Any

def _validate_placeholders(text: str, context: dict[str, Any], task_name: str) -> None:
    """Validate that all {placeholder} variables exist in context.

    Args:
        text: String that may contain {placeholder} variables
        context: Context dictionary with available variables
        task_name: Name of task for error reporting

    Raises:
        ValueError: If any placeholder is missing from context
    """
    # Find all {placeholder} patterns in text
    placeholders = re.findall(r'\{(\w+)\}', text)

    if not placeholders:
        return  # No placeholders to validate

    missing = [p for p in placeholders if p not in context]

    if missing:
        available = sorted(context.keys())
        raise ValueError(
            f"Task '{task_name}': Missing placeholder(s) in context: {', '.join(missing)}\n"
            f"Available context keys: {', '.join(available)}"
        )


def _format_task_params(
    task: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Format task parameters by replacing {placeholder} variables.

    Args:
        task: Task definition with params
        context: Context dictionary with variables

    Returns:
        Formatted parameters dict

    Raises:
        ValueError: If any placeholder is missing from context
    """
    params = task.get("params", {})
    formatted = {}
    task_name = task.get("tool", "unknown")

    for key, value in params.items():
        if isinstance(value, str):
            # Validate before formatting
            _validate_placeholders(value, context, task_name)
            # Format string with context variables
            formatted[key] = value.format(**context)
        else:
            formatted[key] = value

    return formatted


def _execute_task(tool_name: str, task: dict, context: dict) -> Any:
    """Execute a single task using the appropriate handler.

    Args:
        tool_name: Name of tool/command to execute
        task: Task definition dict
        context: Execution context with variables

    Returns:
        Task output (type depends on tool)

    Raises:
        ValueError: If tool not found in registry or placeholders missing
    """
    if tool_name not in TASK_REGISTRY:
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            f"Available tools: {', '.join(TASK_REGISTRY.keys())}"
        )

    handler = TASK_REGISTRY[tool_name]

    # Format task parameters with placeholder validation (STAB-2.2)
    formatted_params = _format_task_params(task, context)

    # Execute handler with formatted params
    return handler(formatted_params, context)
```

**Update execute_module function (line 83-100):**
```python
for idx, task in enumerate(tasks):
    tool_name = task.get("tool", "unknown")
    output_key = task.get("output_key")

    try:
        # Merge step_context into context for this task
        enriched_context = {**context, **step_context}

        # Execute task (now with placeholder validation)
        output = _execute_task(tool_name, task, enriched_context)

        result = TaskResult(
            tool=tool_name,
            success=True,
            output=output,
            error="",
        )
        results.append(result)

        # Store output in step_context if output_key is specified
        if output_key:
            step_context[output_key] = output
            logger.debug(f"Stored output: {output_key} = {output}")

    except ValueError as e:
        # Placeholder validation or tool not found
        logger.error(f"Task validation failed: {e}")
        result = TaskResult(
            tool=tool_name,
            success=False,
            output=None,
            error=str(e),
        )
        results.append(result)

        if stop_on_error:
            logger.warning(f"Stopping execution due to error in task {idx + 1}")
            break

    except Exception as e:
        # Other execution errors
        logger.error(f"Task {idx + 1} ({tool_name}) failed: {e}", exc_info=True)
        result = TaskResult(
            tool=tool_name,
            success=False,
            output=None,
            error=str(e),
        )
        results.append(result)

        if stop_on_error:
            logger.warning(f"Stopping execution due to error in task {idx + 1}")
            break
```

**Acceptance Criteria:**
- [x] `_validate_placeholders()` function checks for missing variables
- [x] `_format_task_params()` calls validation before formatting
- [x] Error message shows missing + available context keys
- [x] Validation occurs BEFORE string formatting (fail-fast)

**Testing:**
```python
# Test case 1: Valid placeholders
context = {"project_name": "Acme", "tagline": "Innovation"}
task = {"tool": "social", "params": {"text": "Project {project_name}: {tagline}"}}
result = _format_task_params(task, context)
# Expected: {"text": "Project Acme: Innovation"}

# Test case 2: Missing placeholder
context = {"project_name": "Acme"}
task = {"tool": "social", "params": {"text": "{project_name} - {tagline}"}}
# Expected: ValueError("Missing placeholder(s): tagline. Available: project_name")

# Test case 3: No placeholders
context = {"project_name": "Acme"}
task = {"tool": "social", "params": {"text": "Hello World"}}
result = _format_task_params(task, context)
# Expected: {"text": "Hello World"}
```

---

### STAB-2.3: Erkennung von zirkulären Abhängigkeiten
**Status:** ✅ ALREADY IMPLEMENTED

No action required. Current implementation in `dependency_resolver.py`:
- Detects cycles via `visiting` set (line 70)
- Raises `CircularDependencyError` with module ID (line 71-73)
- Tracks visiting vs visited modules correctly (lines 56-57)

**Acceptance Criteria:** ✅ All met
- [x] DFS path tracking via `visiting` set
- [x] Clear error message with cycle information
- [x] No false positives (visited set prevents re-processing)

---

## PHASE 3: USABILITY (Nice-to-Have)

### STAB-3.1: Config-Validierung beim Start
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** Invalid `config.toml` causes crashes during command execution, not at startup.

**Implementation Plan:**

#### File to Modify:
`agency_toolkit/cli_app.py` (around line 50-80)

#### Required Changes:

**Add early config validation:**

```python
@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(None, "--version", help="Show version"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output"),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", help="Override default output directory"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as machine-readable JSON"
    ),
    offline: bool = typer.Option(
        False, "--offline", help="Offline mode - block network calls"
    ),
) -> None:
    """Agency Toolkit main entry point."""

    # Handle version check early
    if version:
        version_callback(True)

    # Setup logging
    setup_logging(verbose=verbose, quiet=quiet)

    # ✨ NEW: Validate config early (STAB-3.1)
    try:
        config = load_config(output_dir=output_dir)

        # Validate config structure using Pydantic (if available)
        # This catches missing required fields, type errors, etc.
        from agency_toolkit.config import Config
        validated_config = Config.model_validate(config.__dict__)

        logger.debug("Configuration validated successfully")

    except FileNotFoundError as e:
        # Config file not found - this is OK, use defaults
        logger.debug(f"No config file found, using defaults: {e}")
        config = load_config(output_dir=output_dir)

    except ValueError as e:
        # Invalid config structure
        typer.secho(
            f"✗ Configuration Error: {e}\n\n"
            f"Please check your config.toml file for syntax errors or missing required fields.\n"
            f"See config.toml.example for reference.",
            fg="red"
        )
        raise typer.Exit(1)

    except Exception as e:
        # Unexpected error during config loading
        typer.secho(
            f"✗ Failed to load configuration: {e}\n\n"
            f"Please check your config.toml file.",
            fg="red"
        )
        logger.debug("Config error details:", exc_info=True)
        raise typer.Exit(1)

    # Add config to context
    config.json_output = json_output
    config.offline_mode = offline
    ctx.obj = config
```

**Acceptance Criteria:**
- [x] Config loaded and validated at CLI startup
- [x] Uses `Config.model_validate()` for Pydantic validation
- [x] Clear error message on validation failure
- [x] Exit code 1 on invalid config
- [x] Reference to `config.toml.example` in error message

**Testing:**
```bash
# Test 1: Valid config
toolkit --help
# Expected: No errors, help shown

# Test 2: Invalid config (syntax error)
echo "[invalid syntax" > config.toml
toolkit info
# Expected: "Configuration Error: ... check config.toml"

# Test 3: Missing required field
echo "[general]\n# missing output_dir" > config.toml
toolkit info
# Expected: "Configuration Error: ... missing required fields"

# Test 4: No config file
rm config.toml
toolkit info
# Expected: Works with defaults
```

---

### STAB-3.2: Neuer Befehl: `info providers`
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** Users don't know which providers are correctly configured or which API keys are missing.

**Implementation Plan:**

#### File to Modify:
`agency_toolkit/commands/info.py` (add new command around line 245)

#### Required Changes:

**Add new command:**

```python
@info_command.command(name="providers")
def providers_info(ctx: typer.Context) -> None:
    """Show status of all AI and image providers.

    Displays:
    - Available text providers (Mistral, Google, Ollama)
    - Available image providers (Pollinations, Replicate)
    - Configuration status (✓ if API key found, ✗ if missing)

    Examples:
        toolkit info providers
        toolkit info providers --json
    """
    import os
    from agency_toolkit.providers import (
        list_text_providers,
        list_image_providers,
    )

    config = ctx.obj

    # Gather text provider info
    text_providers = []
    for provider_name in list_text_providers():
        # Check for API key based on provider
        api_key_env_var = {
            "mistral": "MISTRAL_API_KEY",
            "google": "GOOGLE_API_KEY",
            "ollama": None,  # Ollama is local, no API key needed
        }.get(provider_name)

        if api_key_env_var is None:
            # No API key required (e.g., Ollama)
            status = "✓"
            status_text = "Ready (local)"
        else:
            # Check if API key is set
            has_key = bool(os.environ.get(api_key_env_var))
            status = "✓" if has_key else "✗"
            status_text = "Configured" if has_key else f"Missing: {api_key_env_var}"

        text_providers.append({
            "provider": provider_name,
            "type": "text",
            "status": status,
            "status_text": status_text,
            "api_key_var": api_key_env_var,
        })

    # Gather image provider info
    image_providers = []
    for provider_name in list_image_providers():
        # Check for API key based on provider
        api_key_env_var = {
            "pollinations": None,  # Free, no key needed
            "replicate": "REPLICATE_API_TOKEN",
        }.get(provider_name)

        if api_key_env_var is None:
            status = "✓"
            status_text = "Ready (free)"
        else:
            has_key = bool(os.environ.get(api_key_env_var))
            status = "✓" if has_key else "✗"
            status_text = "Configured" if has_key else f"Missing: {api_key_env_var}"

        image_providers.append({
            "provider": provider_name,
            "type": "image",
            "status": status,
            "status_text": status_text,
            "api_key_var": api_key_env_var,
        })

    # Output
    if config.json_output:
        import json
        output = {
            "text_providers": text_providers,
            "image_providers": image_providers,
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable table
        typer.secho("=" * 60, fg="blue")
        typer.secho("Provider Configuration Status", fg="blue")
        typer.secho("=" * 60, fg="blue")

        typer.secho("\n📝 Text Providers:", fg="green")
        for p in text_providers:
            color = "green" if p["status"] == "✓" else "red"
            typer.secho(
                f"  {p['status']} {p['provider']:<15} {p['status_text']}",
                fg=color
            )

        typer.secho("\n🖼️  Image Providers:", fg="green")
        for p in image_providers:
            color = "green" if p["status"] == "✓" else "red"
            typer.secho(
                f"  {p['status']} {p['provider']:<15} {p['status_text']}",
                fg=color
            )

        typer.secho("\n💡 Tip:", fg="cyan")
        typer.echo("  Set missing API keys with:")
        typer.echo("    export MISTRAL_API_KEY='your-key'")
        typer.echo("    export GOOGLE_API_KEY='your-key'")
        typer.echo("    export REPLICATE_API_TOKEN='your-token'")

        typer.secho("\n" + "=" * 60, fg="blue")
```

**Acceptance Criteria:**
- [x] New command `toolkit info providers` created
- [x] Shows all text providers (mistral, google, ollama)
- [x] Shows all image providers (pollinations, replicate)
- [x] Status symbol (✓/✗) based on ENV variable presence
- [x] JSON output support via `--json` flag
- [x] Helpful tip for setting ENV variables

**Testing:**
```bash
# Test 1: No API keys set
unset MISTRAL_API_KEY GOOGLE_API_KEY REPLICATE_API_TOKEN
toolkit info providers
# Expected: ✗ for mistral, google, replicate
#           ✓ for ollama, pollinations

# Test 2: All keys set
export MISTRAL_API_KEY="test"
export GOOGLE_API_KEY="test"
export REPLICATE_API_TOKEN="test"
toolkit info providers
# Expected: ✓ for all providers

# Test 3: JSON output
toolkit --json info providers
# Expected: Valid JSON with provider status
```

---

### STAB-3.3: Dry-Run Modus für Orchestrator
**Status:** 🔴 NOT IMPLEMENTED

**Problem:** `toolkit os init` executes workflows immediately, which is intimidating for users.

**Implementation Plan:**

#### Files to Modify:
1. `agency_toolkit/commands/os.py` (add `--dry-run` flag)
2. `agency_toolkit/core/orchestrator.py` (add dry-run support)

#### Required Changes:

**os.py changes (around line 24-100):**

```python
def execute_project_workflow(
    project_name: str,
    archetype_id: str,
    solution_id: str,
    module_id: str,
    ai_provider: str | None = None,
    stop_on_error: bool = True,
    dry_run: bool = False,  # ✨ NEW parameter (STAB-3.3)
) -> dict:
    """Execute a complete project workflow (non-interactive).

    Args:
        project_name: Name of the project
        archetype_id: Client archetype ID (e.g., "archetype-i")
        solution_id: Solution template ID (e.g., "solution-a1")
        module_id: Module to execute (e.g., "mod-a1-4-recruiting")
        ai_provider: Optional AI provider override
        stop_on_error: Whether to stop on first error
        dry_run: If True, show execution plan without running tasks

    Returns:
        dict: Execution summary or dry-run plan
    """
    # ... existing validation code ...

    # Resolve dependencies
    modules_to_execute = resolve_module_dependencies(module, solution)

    # Build context
    context = {
        "project_name": project_name,
        "archetype_id": archetype_id,
        "solution_id": solution_id,
        "stop_on_error": stop_on_error,
        "dry_run": dry_run,  # ✨ NEW: Pass dry_run to context
        # ... other context vars ...
    }

    # ✨ NEW: Dry-run mode (STAB-3.3)
    if dry_run:
        execution_plan = []
        for idx, mod in enumerate(modules_to_execute, 1):
            tasks = mod.get("tasks", [])
            task_summaries = []
            for task_idx, task in enumerate(tasks, 1):
                tool_name = task.get("tool", "unknown")
                params = task.get("params", {})
                output_key = task.get("output_key")

                task_summary = {
                    "step": f"{idx}.{task_idx}",
                    "tool": tool_name,
                    "params": params,
                    "output_key": output_key,
                }
                task_summaries.append(task_summary)

            execution_plan.append({
                "module_id": mod["id"],
                "module_title": mod.get("title", "Unknown"),
                "tasks": task_summaries,
            })

        return {
            "dry_run": True,
            "project_name": project_name,
            "solution": solution_id,
            "module": module_id,
            "execution_plan": execution_plan,
        }

    # Execute modules (existing code)
    all_results = []
    for mod in modules_to_execute:
        results = execute_module(mod, context)
        all_results.extend(results)

    return {
        "dry_run": False,
        "results": all_results,
        # ... rest of summary ...
    }
```

**Add --dry-run flag to os init command:**

```python
@app.command(name="init")
def os_init(
    ctx: typer.Context,
    project_name: str | None = typer.Option(None, "--project-name", "-n"),
    archetype: str | None = typer.Option(None, "--archetype", "-a"),
    solution: str | None = typer.Option(None, "--solution", "-s"),
    module: str | None = typer.Option(None, "--module", "-m"),
    ai_provider: str | None = typer.Option(None, "--ai-provider"),
    stop_on_error: bool = typer.Option(True, "--stop-on-error/--continue-on-error"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show execution plan without running"),  # ✨ NEW
) -> None:
    """Initialize and execute GRAND AGENCY OS workflow.

    Examples:
        # Show execution plan
        toolkit os init --dry-run

        # Execute workflow
        toolkit os init --project-name "Acme Corp"
    """
    config = ctx.obj

    # ... existing interactive prompts ...

    # Execute workflow
    try:
        summary = execute_project_workflow(
            project_name=final_project_name,
            archetype_id=final_archetype,
            solution_id=final_solution,
            module_id=final_module,
            ai_provider=ai_provider,
            stop_on_error=stop_on_error,
            dry_run=dry_run,  # ✨ NEW
        )

        # ✨ NEW: Dry-run output (STAB-3.3)
        if dry_run:
            if config.json_output:
                print(json.dumps(summary, indent=2))
            else:
                console.print("\n[bold blue]Execution Plan (Dry-Run)[/bold blue]")
                console.print(f"Project: {summary['project_name']}")
                console.print(f"Solution: {summary['solution']}")
                console.print(f"Module: {summary['module']}\n")

                for module_plan in summary["execution_plan"]:
                    console.print(f"\n[bold green]Module: {module_plan['module_title']}[/bold green]")
                    console.print(f"  ID: {module_plan['module_id']}")

                    for task in module_plan["tasks"]:
                        console.print(f"\n  Step {task['step']}: [cyan]{task['tool']}[/cyan]")
                        if task["params"]:
                            console.print(f"    Params: {task['params']}")
                        if task["output_key"]:
                            console.print(f"    Output saved as: {task['output_key']}")

                console.print("\n[yellow]ℹ️  This was a dry-run. No tasks were executed.[/yellow]")
                console.print("[yellow]   Run without --dry-run to execute the workflow.[/yellow]")
        else:
            # Normal execution output (existing code)
            # ... display results ...

    except Exception as e:
        # ... existing error handling ...
```

**Acceptance Criteria:**
- [x] `--dry-run` flag added to `os init` command
- [x] Dry-run shows execution plan without running tasks
- [x] Plan shows: module sequence, task sequence, tool names, params, output keys
- [x] Clear message: "This was a dry-run. No tasks were executed."
- [x] JSON output support

**Testing:**
```bash
# Test 1: Dry-run (interactive)
toolkit os init --dry-run
# Expected: Interactive prompts, then execution plan shown

# Test 2: Dry-run (non-interactive)
toolkit os init --dry-run \
  --project-name "Test" \
  --archetype archetype-i \
  --solution solution-a1 \
  --module mod-a1-1
# Expected: Execution plan shown, no tasks executed

# Test 3: JSON output
toolkit --json os init --dry-run \
  --project-name "Test" \
  --archetype archetype-i \
  --solution solution-a1 \
  --module mod-a1-1
# Expected: Valid JSON with execution_plan array

# Test 4: Normal execution (verify dry-run doesn't break it)
toolkit os init --project-name "Test" # (no --dry-run)
# Expected: Tasks execute normally
```

---

## Implementation Order (Recommended)

### Sprint 1: Critical Bugs (Phase 1)
**Duration:** 2-3 days

1. ✅ **STAB-1.1** — Already done
2. 🟡 **STAB-1.2** — API Key messaging (1 hour)
3. 🔴 **STAB-1.3** — Model validation (2 hours)

**Testing:** Full regression on AI commands

---

### Sprint 2: Complexity Reduction (Phase 2)
**Duration:** 3-4 days

1. 🔴 **STAB-2.1** — Registry rename (2 hours)
2. 🔴 **STAB-2.2** — Placeholder validation (4 hours)
3. ✅ **STAB-2.3** — Already done

**Testing:** Full regression on orchestrator + AI commands

---

### Sprint 3: Usability (Phase 3)
**Duration:** 3-4 days

1. 🔴 **STAB-3.1** — Config validation (2 hours)
2. 🔴 **STAB-3.2** — `info providers` command (3 hours)
3. 🔴 **STAB-3.3** — Dry-run mode (4 hours)

**Testing:** Full integration test suite

---

## Testing Strategy

### Unit Tests
Create tests for each work unit:

```python
# tests/test_stabilization.py

def test_stab_1_2_api_key_error_message():
    """STAB-1.2: API key error mentions config.toml warning."""
    from agency_toolkit.providers.mistral_provider import MistralProvider
    import os

    # Remove API key
    os.environ.pop("MISTRAL_API_KEY", None)

    with pytest.raises(ValueError) as exc_info:
        MistralProvider()

    error_msg = str(exc_info.value)
    assert "MUST be environment variables" in error_msg
    assert "NOT in config.toml" in error_msg
    assert "export MISTRAL_API_KEY" in error_msg


def test_stab_1_3_model_validation():
    """STAB-1.3: Model validation before API call."""
    from agency_toolkit.commands.ai import ai
    # Mock test that model validation rejects invalid model
    # ... implementation ...


def test_stab_2_2_placeholder_validation():
    """STAB-2.2: Missing placeholder raises ValueError."""
    from agency_toolkit.core.orchestrator import _format_task_params

    task = {"tool": "social", "params": {"text": "{missing_var}"}}
    context = {"project_name": "Test"}

    with pytest.raises(ValueError) as exc_info:
        _format_task_params(task, context)

    error_msg = str(exc_info.value)
    assert "missing_var" in error_msg
    assert "Available" in error_msg


def test_stab_3_3_dry_run_mode():
    """STAB-3.3: Dry-run shows plan without executing."""
    from agency_toolkit.commands.os import execute_project_workflow

    summary = execute_project_workflow(
        project_name="Test",
        archetype_id="archetype-i",
        solution_id="solution-a1",
        module_id="mod-a1-1",
        dry_run=True
    )

    assert summary["dry_run"] is True
    assert "execution_plan" in summary
    assert len(summary["execution_plan"]) > 0
    # Verify no actual tasks ran
```

### Integration Tests
```bash
# Create integration test script
./scripts/test_stabilization.sh

# Should test:
# - All API key error messages
# - Model validation for each provider
# - Dry-run vs normal execution
# - Config validation errors
# - Placeholder validation in real workflows
```

### Manual QA Checklist
- [ ] Mistral API key error shows config.toml warning
- [ ] Google API key error shows config.toml warning
- [ ] Replicate token error shows config.toml warning
- [ ] Invalid model for provider shows available models
- [ ] Missing placeholder shows available context keys
- [ ] Invalid config.toml fails at startup, not during execution
- [ ] `toolkit info providers` shows correct status for all providers
- [ ] Dry-run shows execution plan without running tasks
- [ ] Registry rename doesn't break any imports

---

## Rollback Plan

If any work unit causes regressions:

1. **Phase 1 (Critical):** Revert immediately
   - Use `git revert <commit-hash>`
   - Deploy hotfix to production

2. **Phase 2 (Medium):** Revert if blocking work
   - Can be deferred to next sprint
   - Document issue in GitHub

3. **Phase 3 (Nice-to-have):** Optional revert
   - Feature flag if possible
   - Document and plan fix

---

## Success Metrics

### Quantitative
- **Error Clarity:** 0 cryptic error messages for missing API keys
- **Fail-Fast:** Model validation prevents 100% of wrong-model-for-provider errors
- **Silent Failures:** Placeholder validation catches 100% of missing context vars

### Qualitative
- **User Feedback:** "Error messages are clear and actionable"
- **Developer Experience:** "I know which providers are configured without trial-and-error"
- **Confidence:** "I can preview what a workflow will do before running it"

---

## Documentation Updates

After implementation, update:

1. **README.md** — Add "Provider Configuration" section with `info providers` command
2. **DEVELOPMENT.md** — Update architecture diagram (registry renames)
3. **docs/USER_GUIDE.md** — Add dry-run examples
4. **config.toml.example** — Add comments warning against API keys in config

---

## Completion Checklist

### Phase 1
- [ ] STAB-1.1: ✅ Already complete
- [ ] STAB-1.2: Enhanced API key error messages
- [ ] STAB-1.3: Model validation before API call

### Phase 2
- [ ] STAB-2.1: Registry files renamed + imports updated
- [ ] STAB-2.2: Placeholder validation in orchestrator
- [ ] STAB-2.3: ✅ Already complete

### Phase 3
- [ ] STAB-3.1: Config validation at startup
- [ ] STAB-3.2: `info providers` command
- [ ] STAB-3.3: Dry-run mode for orchestrator

### Post-Implementation
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Manual QA completed
- [ ] User acceptance testing
- [ ] Epic closed in project management tool

---

## Notes for Implementation

### Git Workflow
```bash
# Create feature branch for each phase
git checkout -b feature/stabilization-phase-1
git checkout -b feature/stabilization-phase-2
git checkout -b feature/stabilization-phase-3

# Commit each work unit separately
git commit -m "STAB-1.2: Improve API key error messages"
git commit -m "STAB-1.3: Add model validation before provider call"
```

### Code Review Focus Areas
1. **Error Message Clarity:** Are errors actionable?
2. **Fail-Fast Behavior:** Do we validate early?
3. **Test Coverage:** Are edge cases covered?
4. **Documentation:** Are changes documented?
5. **Backward Compatibility:** Do existing workflows still work?

---

**Epic Status:** READY FOR IMPLEMENTATION
**Next Action:** Create feature branch + start Phase 1 Sprint
**Estimated Total Time:** 8-11 days (across 3 sprints)
