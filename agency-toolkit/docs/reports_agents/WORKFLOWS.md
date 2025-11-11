# Workflow Orchestration System

## Overview

The Workflow Orchestration System is the core execution engine of GRAND AGENCY OS. It enables you to define complex, multi-step business processes as JSON workflows that execute tasks in sequence, passing data between tasks and handling errors gracefully.

**Key Capabilities**:
- 📋 **Task Chaining**: Output from one task becomes input for the next
- 🔗 **Module Dependencies**: Execute modules in dependency order
- 🛡️ **Graceful Error Handling**: Continue workflows after non-critical failures
- 📊 **Observability**: Structured logging and progress tracking
- ✅ **Validation**: Automatic JSON schema validation of workflow definitions
- 🎯 **Context Passing**: Share data between tasks with smart context management

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│  commands/os.py (CLI Entry Point)                       │
│  - Parses user input (archetype, solution, module)      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  core/os_executor.py (Workflow Coordinator)             │
│  - Finds archetype, solution, module from registry      │
│  - Resolves module dependencies                         │
│  - Builds execution context                             │
│  - Executes workflow modules                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  core/orchestrator.py (Task Execution Engine)           │
│  - Execute each task with proper handler                │
│  - Manage context (step_context + raw_context)          │
│  - Handle errors based on on_error mode                 │
│  - Track execution metrics                              │
│  - Generate WorkflowExecutionReport                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  tasks/*.py (Task Handler Plugins)                      │
│  - ai: AI content generation                            │
│  - social: Social media content                         │
│  - briefing: Document generation                        │
│  - structure: Project file structure                    │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Workflow Definition** (JSON)
   ```json
   {
     "id": "A1",
     "modules": [
       {
         "id": "A1_M1",
         "tasks": [
           {"tool": "ai", "output_key": "tagline", "params": {...}},
           {"tool": "social", "params": {"text": "{tagline}"}}
         ]
       }
     ]
   }
   ```

2. **Execution Context** (Dictionary)
   - Initial context: `{"project_name": "Acme Corp", "archetype_id": "I", ...}`
   - Updated after each task: `{"project_name": "...", "tagline": "Amazing Solutions"}`

3. **Task Results** (TaskResult Objects)
   ```python
   TaskResult(
     tool="ai",
     success=True,
     output="Amazing Solutions",
     error=""
   )
   ```

4. **Execution Report** (WorkflowExecutionReport)
   ```python
   WorkflowExecutionReport(
     module_id="A1_M1",
     total_tasks=2,
     successful=2,
     failed=0,
     skipped=0,
     errors=[],
     task_results=[TaskResult(...), TaskResult(...)]
   )
   ```

---

## Writing Workflows

### Basic Structure

Every workflow is a JSON file with this top-level structure:

```json
{
  "id": "SOLUTION_ID",
  "name": "Solution Name",
  "archetype_id": "ARCHETYPE_ID",
  "description": "What this solution does",
  "modules": [
    {
      "id": "MODULE_ID",
      "title": "Module Title",
      "description": "What this module does",
      "tasks": [
        {
          "tool": "task_name",
          "output_key": "result_variable",
          "on_error": "continue",
          "params": {
            "param1": "value",
            "param2": "{placeholder}"
          }
        }
      ],
      "dependencies": ["DEPENDENCY_MODULE_ID"],
      "context_variables": []
    }
  ]
}
```

### Fields Explained

#### Solution Level
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier (e.g., "A1", "B2"). Must be uppercase alphanumeric. |
| `name` | string | ✅ | Human-readable name (e.g., "Lokale Dominanz") |
| `archetype_id` | string | ✅ | Which archetype this solution targets (must exist in archetypes.json) |
| `description` | string | ❌ | Explains the purpose of the solution |
| `modules` | array | ✅ | List of module objects to execute |

#### Module Level
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique module identifier (e.g., "A1_M1"). Must be uppercase with underscores. |
| `title` | string | ✅ | Human-readable module title (e.g., "Foundation (Corporate Design)") |
| `description` | string | ❌ | What the module does |
| `tasks` | array | ✅ | List of task objects to execute in order |
| `dependencies` | array | ❌ | Module IDs that must execute before this module (e.g., ["A1_M1", "A1_M2"]) |
| `context_variables` | array | ❌ | Documentation of context variables used by this module |

#### Task Level
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool` | string | ✅ | Task handler name: `ai`, `social`, `briefing`, or `structure` |
| `output_key` | string | ❌ | Variable name to store task output (e.g., "tagline"). Output becomes available to subsequent tasks. |
| `on_error` | string | ❌ | Error handling mode: `stop` (default, halt workflow) or `continue` (log error, skip task) |
| `params` | object | ❌ | Parameters passed to the task handler. Supports template placeholders like `{project_name}` |

### Task Handlers

#### `ai` Handler
Generates AI content using LLM providers.

```json
{
  "tool": "ai",
  "output_key": "tagline",
  "params": {
    "prompt": "Create a tagline for {project_name}",
    "provider": "{ai_provider}",
    "temperature": 0.8,
    "max_tokens": 100
  }
}
```

**Parameters**:
- `prompt` (required): The prompt to send to the AI model. Supports context placeholders.
- `provider` (optional): AI provider name (e.g., "openai", "mistral"). Defaults to configured provider.
- `temperature` (optional): Creativity level 0-1. Lower = deterministic, higher = creative.
- `max_tokens` (optional): Maximum response length.

#### `social` Handler
Creates social media content and graphics.

```json
{
  "tool": "social",
  "params": {
    "text": "{tagline}",
    "style": "bold",
    "color": "blue",
    "format": "story",
    "output_dir": "./output/{project_name_safe}/social"
  }
}
```

**Parameters**:
- `text` (required): Content for the social media post. Supports placeholders.
- `style` (optional): "bold", "italic", "normal"
- `color` (optional): Color name or hex code
- `format` (optional): "story", "post", "reel"
- `output_dir` (optional): Where to save generated files

#### `briefing` Handler
Generates PDF documents and briefs.

```json
{
  "tool": "briefing",
  "params": {
    "type": "Web",
    "client_name": "{project_name_safe}",
    "project_name": "Website Relaunch",
    "output_format": "pdf"
  }
}
```

**Parameters**:
- `type` (required): Brief type ("Web", "Social", "Marketing", "Other")
- `client_name` (optional): Client name for the brief
- `project_name` (optional): Project name
- `output_format` (optional): "pdf", "markdown", "html"

#### `structure` Handler
Creates project folder structures and templates.

```json
{
  "tool": "structure",
  "params": {
    "client": "{project_name}",
    "project": "Website Relaunch",
    "type": "web"
  }
}
```

**Parameters**:
- `client` (optional): Client name
- `project` (optional): Project name
- `type` (optional): Folder structure type ("web", "social", "default")

---

## Context and Data Passing

### The Dual Context System

The workflow engine maintains **two contexts** simultaneously:

#### 1. Step Context (Formatted)
Used for **template substitution** in task parameters. All values are converted to strings.

```python
step_context = {
  "project_name": "Acme Corp",
  "taglines": "Amazing, Innovative, Professional",  # List converted to string
  "pain_points": "Time, Budget, Visibility"         # List converted to string
}
```

**Use in tasks**:
```json
{
  "tool": "social",
  "params": {
    "text": "{taglines}"  # Receives "Amazing, Innovative, Professional" as string
  }
}
```

#### 2. Raw Context (Typed)
Preserves original data types (lists, dicts, objects). Used when you need structured data.

```python
raw_context = {
  "project_name": "Acme Corp",
  "taglines": ["Amazing", "Innovative", "Professional"],  # List preserved
  "pain_points": ["Time", "Budget", "Visibility"]         # List preserved
}
```

**Use in custom handlers**:
```python
# In your custom task handler
context.get("taglines")        # Returns "Amazing, Innovative, Professional" (string)
context.get_raw("taglines")    # Returns ["Amazing", "Innovative", "Professional"] (list)
```

### Available Context Variables

These variables are available to all tasks:

| Variable | Type | Description |
|----------|------|-------------|
| `project_name` | string | Project name as provided by user |
| `project_name_safe` | string | Project name with underscores converted to spaces |
| `archetype_id` | string | ID of the selected archetype |
| `archetype_name` | string | Name of the selected archetype |
| `solution_id` | string | ID of the selected solution |
| `solution_name` | string | Name of the selected solution |
| `pain_points` | list | Pain points from archetype |
| `goals` | list | Goals from archetype |
| `ai_provider` | string | AI provider name (openai, mistral, etc.) |

### Storing Task Output

Use `output_key` to make a task's output available to subsequent tasks:

```json
[
  {
    "tool": "ai",
    "output_key": "tagline",  // This output is stored
    "params": {"prompt": "Create a tagline..."}
  },
  {
    "tool": "social",
    "params": {
      "text": "{tagline}"  // Can reference tagline from previous task
    }
  }
]
```

**Important**: When you store a list, the step_context automatically converts it to a comma-separated string. To access the original list, use `context.get_raw("key_name")` in custom handlers.

---

## Error Handling

### On-Error Modes

Each task can specify how errors should be handled:

```json
{
  "tool": "ai",
  "on_error": "stop",        // Default: halt on error
  "params": {...}
}
```

or

```json
{
  "tool": "social",
  "on_error": "continue",    // Log error and skip task, workflow continues
  "params": {...}
}
```

#### `stop` Mode (Default)
- If task fails, immediately halt the workflow
- Subsequent tasks don't execute
- Module is marked as failed
- Use for **critical tasks** that must succeed

#### `continue` Mode
- If task fails, log the error and skip the task
- Continue executing subsequent tasks
- Module completes even if some tasks fail
- Use for **optional or non-critical tasks** (e.g., analytics, logging)

### Error Tracking

All errors are tracked in the `WorkflowExecutionReport`:

```python
report = execute_module(module, context)

print(f"Total tasks: {report.total_tasks}")
print(f"Successful: {report.successful}")
print(f"Failed: {report.failed}")
print(f"Skipped: {report.skipped}")
print(f"Errors: {report.errors}")

for result in report.task_results:
    if not result.success:
        print(f"Task {result.tool} failed: {result.error}")
```

---

## Module Dependencies

Modules can depend on other modules to control execution order:

```json
[
  {
    "id": "A1_M1",
    "title": "Foundation",
    "dependencies": [],
    "tasks": [...]
  },
  {
    "id": "A1_M2",
    "title": "Website",
    "dependencies": ["A1_M1"],  // Must run after A1_M1
    "tasks": [...]
  },
  {
    "id": "A1_M3",
    "title": "Social",
    "dependencies": ["A1_M1", "A1_M2"],  // Must run after both M1 and M2
    "tasks": [...]
  }
]
```

The system uses **topological sorting** to determine execution order. Circular dependencies are detected and rejected with a clear error message.

---

## Observability

### Structured Logging

The workflow engine logs major events with structured data:

```
INFO     module_started: module_id=A1_M1, task_count=3
INFO     task_executing: tool=ai, output_key=tagline, task_index=1/3
INFO     task_completed: tool=ai, duration_ms=2543, success=True
INFO     module_completed: success_count=3, failed_count=0, skipped_count=0
```

**Enable verbose logging**:
```bash
toolkit os init --verbose
```

### Progress Bar

Long-running workflows display a progress bar:

```
⠦ Executing module A1_M1 [████████░░] 80%
```

Shows completion percentage in real-time.

---

## Best Practices

### 1. Design for Graceful Degradation
```json
{
  "tool": "social",
  "on_error": "continue",
  "params": {"text": "{tagline}"}
}
```
Non-critical tasks like social media posting should use `on_error: continue` so failure doesn't halt the entire workflow.

### 2. Use Descriptive Output Keys
```json
// Good
{"tool": "ai", "output_key": "recruiting_tagline", "params": {...}}

// Poor
{"tool": "ai", "output_key": "result", "params": {...}}
```
Clear names make workflows easier to understand and debug.

### 3. Organize with Module Dependencies
```json
{
  "id": "A1_M1",
  "title": "Foundation - Create basic assets",
  "dependencies": [],
  "tasks": [...]
},
{
  "id": "A1_M2",
  "title": "Build Website",
  "dependencies": ["A1_M1"],
  "tasks": [...]
}
```
Use modules to organize logical groups of related tasks.

### 4. Handle Lists Carefully
```python
# In custom handler:
names = context.get_raw("customer_names")  # Get as list
for name in names:
    print(name)

# In template:
"{customer_names}"  # Automatically becomes comma-separated string
```
Remember: step_context converts lists to strings for templates.

### 5. Document Context Dependencies
```json
{
  "id": "A1_M4",
  "title": "Social Recruiting",
  "context_variables": ["project_name", "archetype_name", "pain_points", "goals"],
  "tasks": [...]
}
```
List expected context variables for clarity.

---

## Validation and Debugging

### Validate a Workflow File
```bash
toolkit validate workflow path/to/workflow.json
```

### Debug a Failing Workflow
1. Enable verbose logging:
   ```bash
   toolkit os init --verbose
   ```

2. Check the execution report:
   ```python
   report = execute_module(module, context)
   for error in report.errors:
       print(f"Error: {error}")
   ```

3. Inspect task results:
   ```python
   for result in report.task_results:
       print(f"{result.tool}: {result.success}")
       if not result.success:
           print(f"  Error: {result.error}")
   ```

### Common Issues

**Issue**: Task output not available to next task
- **Cause**: Missing `output_key` on the first task
- **Fix**: Add `"output_key": "variable_name"` to store output

**Issue**: Template placeholder not substituting
- **Cause**: Key doesn't exist in context
- **Fix**: Check spelling and ensure previous task stored output with correct key

**Issue**: Workflow stops at first error
- **Cause**: Task has `on_error: stop` (default)
- **Fix**: Change to `on_error: continue` if error is non-critical

**Issue**: List context variable becomes string
- **Cause**: Using `context.get()` instead of `context.get_raw()`
- **Fix**: Use `context.get_raw()` in custom handlers to access original list

---

## Next Steps

- See [examples/workflows/](../examples/workflows/) for complete workflow examples
- Check [registry/seeds/](../registry/seeds/) for production workflows
- Read [agency_toolkit_roadmap.md](./agency_toolkit_roadmap.md) for architecture details
