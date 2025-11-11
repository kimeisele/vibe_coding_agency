# 🚀 Agency Toolkit

**Professional CLI automation platform for creative agencies**

> Automate repetitive workflows, generate branded assets, and enhance productivity with AI—all from the command line.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-166%20passed-success.svg)](./tests/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com/)

---

## ✨ Why Agency Toolkit?

Traditional agency workflows involve repetitive manual tasks: creating social media posts, writing project briefings, organizing folders. **Agency Toolkit automates all of this**, letting your team focus on actual creative work.

**Key Benefits**:
- ⚡ **Save hours weekly** - Automate repetitive tasks
- 🎨 **Brand consistency** - Template-driven outputs
- 🤖 **AI-enhanced** - Multiple providers (Mistral, Google, Ollama)
- 🆓 **FREE image generation** - Pollinations.ai provider (no API tokens required!)
- 🔌 **Plugin architecture** - Support for multiple image providers (Replicate, Pollinations, extensible)
- 🔧 **Composable** - Unix philosophy: pipe, combine, extend
- ✅ **Production-ready** - 166 tests, type-safe, well-documented

## 🎯 Features

### Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `social` | Generate branded social media posts | `toolkit social --text "Hello!" --style modern` |
| `briefing` | Create project briefing PDFs | `toolkit briefing --interactive` |
| `structure` | Setup standardized project folders | `toolkit structure --client "Acme" --project "Web 2024"` |
| `ai` | Multi-provider AI assistant | `toolkit ai --provider google --prompt "Suggest improvements"` |

### Social Media Post Generator
Create professional social media graphics in seconds with customizable templates.

### Project Briefing System
Generate standardized client briefings in PDF or Markdown format with interactive prompts.

### Folder Structure Generator
Instantly create organized project structures for web, print, social, or video projects.

### AI Text Generation (Multi-Provider) 🆕
Use AI providers like Mistral, Google GenAI, or Ollama for intelligent text generation and analysis.

## 📊 Performance Guarantees

Agency Toolkit is built for professional use. Here are our validated performance SLOs:

| Metric | Target | Status |
|--------|--------|--------|
| **100-post batch** | < 5 minutes | ✅ Validated |
| **Throughput** | > 10 posts/sec | ✅ Validated |
| **Success Rate** | ≥ 95% | ✅ Validated |
| **Memory/Batch** | Bounded | ✅ Validated |

**What this means:**
- Generate 100 social media posts in under 5 minutes
- Process batches of 1000+ posts without memory leaks
- Graceful handling of API failures (batch continues, failures reported)

**Detailed Metrics**: See [docs/PERFORMANCE.md](./docs/PERFORMANCE.md) for comprehensive benchmarks, production vs. mocked performance, and release procedures.

**UAT Tests**: Performance validated in `tests/uat/test_performance.py` (runs in CI)

## Installation & Distribution

### Option 1: Standalone Binary (Recommended - Click & Run!) 🎯

**NEW in v1.1**: Download a single executable file—no Python installation required!

1. Download the latest release for your platform:
   - **macOS**: `agency-toolkit-macos`
   - **Linux**: `agency-toolkit-linux`
   - **Windows**: `agency-toolkit-windows.exe`

2. Make it executable (macOS/Linux):
   ```bash
   chmod +x agency-toolkit-macos
   ./agency-toolkit-macos --help
   ```

3. Optional: Move to your PATH for system-wide access:
   ```bash
   sudo mv agency-toolkit-macos /usr/local/bin/toolkit
   toolkit --help
   ```

### Option 2: Install from Source (Development)

```bash
git clone https://github.com/yourusername/agency-toolkit
cd agency-toolkit
pip install -e .
```

**Optional AI Providers**: Install specific providers as needed:

```bash
# Google GenAI support
pip install -e ".[google]"

# Mistral AI support
pip install -e ".[mistral]"

# All AI providers
pip install -e ".[google,mistral]"
```

For development (includes all optional dependencies):

```bash
pip install -e ".[dev]"
```

### Building Your Own Binary

```bash
make build-binary
# Binary will be in dist/agency-toolkit
```

## Quick Start

### 🎨 Interactive Mode (Zero Guesswork!)

**New in v1.0**: Just type the command and follow the prompts! The toolkit dynamically discovers all available options and presents them with descriptions.

```bash
# Social media post - fully guided
toolkit social generate
# → Prompts for text, style (with descriptions), color, format
# → Option to add AI-generated background from registry templates
# → Shows all available seed concepts (moody, corporate, playful, etc.)

# Project briefing - choose your template
toolkit briefing generate
# → Shows: web, video, brand, campaign (with descriptions)

# Folder structure - guided setup
toolkit structure create
# → Walks through client, project, type selection
```

### 1. Generate Social Media Post

```bash
# Interactive mode (recommended!)
toolkit social generate

# Or use command-line args
toolkit social generate "Hello World" --style modern --color blue

# Available styles: modern, bold, minimal, playful
# Available colors: blue, red, green, purple, or custom hex (#RRGGBB)
# Available formats: square (1:1), landscape (16:9), portrait (9:16), twitter

# With AI background from registry
toolkit social generate "Check it out" --bg-concept "registry:moody"

# **NEW in v1.1: Batch Campaign Generation!** 🚀
# Generate entire campaigns from a CSV or JSON file
toolkit social generate --from-csv campaign.csv
toolkit social generate --from-json posts.json

# Batch with custom output directory
toolkit --output-dir ./client-renders social generate --from-csv campaign.csv
```

**Batch Processing (v1.1+)**:

Create a `campaign.csv` file:
```csv
text,style,color,format
"Launch Day! 🚀","bold","blue","square"
"Summer Sale - 50% OFF","modern","red","landscape"
"New Product Arriving","minimal","green","story"
```

Or `campaign.json`:
```json
[
  {"text": "Monday Motivation ✨", "style": "modern", "color": "blue"},
  {"text": "Flash Sale!", "style": "bold", "color": "red", "format": "story"}
]
```

Then run:
```bash
toolkit social generate --from-csv campaign.csv
# ✓ Batch processing complete. Generated 3/3 posts.
```

**CSV Headers** (case-insensitive):
- `text` (required) - Post content
- `style` (optional) - modern, minimal, or bold (defaults to config value)
- `color` (optional) - blue, red, green, purple, or hex code
- `format` (optional) - square, story, or landscape
- `bg_concept` (optional) - Background concept for AI generation

# With custom AI background concept
toolkit social generate "Hello" --bg-concept "futuristic cityscape at sunset"

# Dry run (preview without saving)
toolkit social generate "Preview only" --dry-run

# JSON output (for automation)
toolkit --json social generate "Hello" --style modern
```

### 2. Generate Project Briefing

```bash
# Interactive mode (asks questions based on template)
toolkit briefing

# Use web-specific template
toolkit briefing --type web

# Use video-specific template
toolkit briefing --type video

# From JSON file
toolkit briefing --from-json briefing_data.json

# Output as Markdown instead of PDF
toolkit briefing --type default --format md

# Dry run
toolkit briefing --type web --dry-run

# JSON output
toolkit --json briefing --type default
```

**Available Briefing Types**:
- `default`: The 5 W's (Who, What, When, Where, Why)
- `web`: Web project specifics (pages, CMS, hosting, SEO)
- `video`: Video production specifics (platform, format, voiceover, music)

### 3. Create Project Folder Structure

```bash
# Create a web project structure
toolkit structure --client "Acme Corp" --project "Website 2024" --type web

# Create a video project structure
toolkit structure --client "Creative Studio" --project "Brand Video" --type video

# Custom base path
toolkit structure --client "Acme" --project "Web" --base-path /custom/projects

# Dry run
toolkit structure --client "Test" --project "Test" --type web --dry-run

# Force overwrite existing
toolkit structure --client "Acme" --project "Web" --force

# JSON output
toolkit --json structure --client "Acme" --project "Web" --type web
```

**Available Structure Types**:
- `default`: Generic project structure
- `web`: React/Vue frontend project (components, pages, styles, assets)
- `video`: Video editing project (footage, audio, assets, renders)
- `print`: Print design project
- `social`: Social media project

### 4. AI Image Generation (FREE with Pollinations.ai! 🆓)

```bash
# Generate an image from a text prompt (uses FREE Pollinations.ai by default)
toolkit image generate "modern minimalist office with large windows"

# With custom dimensions
toolkit image generate "beautiful sunset" --width 1024 --height 1024

# With deterministic seed (same seed = same image)
toolkit image generate "landscape" --seed 12345

# Use Replicate provider (if you have API token)
toolkit image generate "cat portrait" --provider replicate

# JSON output
toolkit --json image generate "cat portrait"
```

**Available Image Providers:**
- `pollinations` (default) - FREE, no API token required, great quality
- `replicate` - Paid, requires REPLICATE_API_TOKEN, more fine-grained control

### 5. Use AI Text Assistant (Multi-Provider)

**NEW in v1.1**: Support for multiple text AI providers! Choose between Mistral (cloud) or Ollama (free, local).

```bash
# Mistral (default - requires MISTRAL_API_KEY)
toolkit ai --prompt "Explain design thinking in 3 sentences"

# Ollama (FREE, runs locally - requires Ollama installed)
toolkit ai --provider ollama --prompt "Explain quantum computing"
toolkit ai --provider ollama --model llama3.2 --prompt "Review this code"

# Using a profile (pre-configured settings)
toolkit ai --profile code --prompt "Review this function: def foo(): pass"
toolkit ai --profile creative --prompt "Generate 5 social media headlines for a new product"
toolkit ai --profile debug --prompt "Why is this error occurring?"
toolkit ai --profile agency_comms --prompt "Draft a client update email"

# Load prompt from file
toolkit ai --prompt-file analysis_request.txt

# Pipe input (Unix style!)
cat project_notes.md | toolkit ai --stdin
cat code_snippet.py | toolkit ai --profile code --stdin

# Interactive mode (prompts for input)
toolkit ai

# Custom temperature (0.0 = deterministic, 1.0 = creative)
toolkit ai --prompt "Hello" --temperature 0.1

# Custom max tokens
toolkit ai --prompt "Hello" --max-tokens 500

# Custom model (provider-specific)
toolkit ai --provider mistral --model mistral-large-latest --prompt "Hello"
toolkit ai --provider ollama --model llama3.1 --prompt "Hello"

# JSON output
toolkit --json mistral --prompt "Hello"
```

**Available Providers**:
- `mistral` (default) - Cloud-based, requires API key, high quality
- `ollama` - FREE, runs locally, requires Ollama installation ([ollama.ai](https://ollama.ai))

**Available Profiles**:
- `code`: Code review with low temperature (0.1) - precise, analytical
- `creative`: Creative copywriting with high temperature (0.9) - multiple options
- `agency_comms`: Professional client communication (0.7)
- `debug`: Debugging assistant with zero temperature (0.0) - deterministic
- Custom profiles can be added in `~/.config/agency-toolkit/config.toml`

**Mistral Models**:
- `mistral-tiny` - Fastest, smallest
- `mistral-small-latest` - Default, good balance
- `mistral-medium` - Larger context
- `mistral-large-latest` - Most capable

**Ollama Models** (install with `ollama pull <model>`):
- `llama3.2` - Default, general purpose
- `llama3.1` - Larger, more capable
- `mistral` - Mistral 7B, fast and efficient
- `codellama` - Code-specialized
- `phi3` - Compact, efficient

## 🔄 Workflow Orchestration

**NEW in v2.5**: Automate complex multi-step workflows with JSON configuration and AI-powered task execution!

The Workflow Orchestration System enables you to define sophisticated business processes as code. Execute multiple tasks in sequence, chain outputs between tasks, handle errors gracefully, and track execution metrics—all declaratively through JSON.

### Why Workflow Orchestration?

Traditional workflow automation requires custom scripting. Agency Toolkit workflows are:
- **Declarative**: Define what you want in JSON, not how to do it
- **Composable**: Chain task outputs as inputs to subsequent tasks
- **Resilient**: Gracefully handle failures with per-task error modes
- **Observable**: Structured logging and progress tracking
- **Validated**: JSON schema validation catches errors early

### Quick Example

Create a workflow that generates a tagline, then creates social media content:

```json
{
  "id": "SOCIAL_CAMPAIGN",
  "modules": [
    {
      "id": "M1",
      "tasks": [
        {
          "tool": "ai",
          "output_key": "tagline",
          "params": {
            "prompt": "Create a tagline for {project_name}"
          }
        },
        {
          "tool": "social",
          "params": {
            "text": "{tagline}"
          }
        }
      ]
    }
  ]
}
```

Execute it:

```bash
toolkit os init --from-json examples/workflows/simple-campaign.json \
  --project "Acme Corp" \
  --archetype I \
  --solution A1
```

The `{tagline}` placeholder is automatically replaced with the output from the first task.

### Workflow Features

#### 📋 Task Chaining
Output from one task becomes input for the next:

```json
{
  "tasks": [
    {
      "tool": "ai",
      "output_key": "hero_text",
      "params": {"prompt": "Create headline for {project_name}"}
    },
    {
      "tool": "social",
      "params": {"text": "{hero_text}"}
    }
  ]
}
```

#### 🛡️ Graceful Error Handling
Use `on_error` to control workflow behavior:

```json
{
  "tool": "ai",
  "on_error": "continue",
  "params": {"prompt": "Optional task..."}
}
```

- `stop` (default): Halt workflow on error
- `continue`: Log error and skip task, workflow continues

#### 🔗 Module Dependencies
Execute modules in dependency order:

```json
[
  {"id": "M1", "tasks": [...], "dependencies": []},
  {"id": "M2", "tasks": [...], "dependencies": ["M1"]},
  {"id": "M3", "tasks": [...], "dependencies": ["M1", "M2"]}
]
```

System automatically topologically sorts modules and detects circular dependencies.

#### 📊 Built-in Observability
```bash
# Enable verbose logging to see all execution events
toolkit os init --verbose
# → Shows: module_started, task_executing, task_completed, module_completed
```

Structured logging tracks:
- Module execution start/end
- Each task's execution time
- Success/failure counts
- Error messages and stack traces

#### ✅ Workflow Validation
JSON schema validation ensures workflows are correct:

```bash
# Validate a workflow file
toolkit validate workflow path/to/workflow.json
```

Invalid workflows are caught at load time with clear error messages.

### Available Task Handlers

| Handler | Purpose | Example |
|---------|---------|---------|
| `ai` | Generate AI content | `{"tool": "ai", "params": {"prompt": "..."}}` |
| `social` | Create social media content | `{"tool": "social", "params": {"text": "..."}}` |
| `briefing` | Generate briefing PDFs | `{"tool": "briefing", "params": {"type": "Web"}}` |
| `structure` | Create folder structures | `{"tool": "structure", "params": {"type": "web"}}` |

### Example Workflows

Three complete examples are provided:

1. **simple-campaign.json** - Basic 3-task workflow demonstrating output chaining
2. **multi-module.json** - Complex workflow with 3 modules and dependencies
3. **error-handling.json** - Shows graceful degradation with `on_error: continue`

```bash
# Run example workflows
toolkit os init --from-json examples/workflows/simple-campaign.json \
  --project "My Project" --archetype I --solution A1

toolkit os init --from-json examples/workflows/multi-module.json \
  --project "Full Solution" --archetype I --solution A1

toolkit os init --from-json examples/workflows/error-handling.json \
  --project "Resilient Workflow" --archetype I --solution A1
```

### Complete Documentation

For detailed documentation on:
- Writing workflows from scratch
- Context variables and data passing
- Error handling strategies
- Custom task handlers
- Debugging workflows

See **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** for comprehensive guide.

---

## 🛡️ Production Features (v1.0)

### Quality Validation

Snapshot-based regression testing ensures output quality never degrades:

```bash
# Generate test artifacts
toolkit social generate "Test" --output snapshots/current/social_test.png
toolkit briefing generate web --output snapshots/current/briefing_web.pdf

# Validate against approved baselines
toolkit validate snapshot

# Approve new baselines (after reviewing changes)
toolkit validate snapshot --approve
```

### Offline Mode

Work without network access for local-only operations:

```bash
# Enable offline mode (blocks all network calls)
toolkit --offline structure create web test-project

# Offline-safe commands: structure, info
# Network-required: social (with AI bg), mistral, image
```

### Resilience Features

Built-in error recovery for production reliability:

- **Retry Logic**: API calls automatically retry with exponential backoff (3 attempts)
- **Rate Limiting**: Mistral API calls throttled to 1 req/sec to prevent 429 errors
- **Graceful Degradation**: Provider failures logged but don't crash the tool
- **Font Fallback**: PDF generation uses font cascade (Helvetica → Arial → DejaVu)

```bash
# Test resilience (CLI remains responsive on failures)
toolkit --verbose social generate "Test" --bg-concept "invalid"
# → Logs error, continues without background
```

## 📖 Complete Command Reference

### Global Options (all commands)

```bash
toolkit --help                    # Show help
toolkit --version                 # Show version
toolkit --verbose social ...      # Enable debug logging
toolkit --quiet social ...        # Suppress output
toolkit --output-dir /path ...    # Override output directory
toolkit --json social ...         # Output as JSON (for automation)
toolkit --offline structure ...   # Offline mode (block network calls)
```

### Social Command

```bash
toolkit social --text "TEXT"                    # Required: post text
  [--style STYLE]                              # modern, bold, minimal (default: modern)
  [--color COLOR]                              # blue, red, green, purple, or #HEX
  [--custom-color #HEX]                        # Custom hex color
  [--format FORMAT]                            # square, story, landscape (default: square)
  [--output /path]                             # Custom output path
  [--dry-run]                                  # Preview without saving
```

### Briefing Command

```bash
toolkit briefing
  [--type TYPE]                                # default, web, video (default: default)
  [--format FORMAT]                            # pdf or md (default: pdf)
  [--from-json /path/file.json]                # Load from JSON instead of interactive
  [--dry-run]                                  # Preview without saving
```

### Structure Command

```bash
toolkit structure
  --client "NAME"                              # Required: client name
  --project "NAME"                             # Required: project name
  [--type TYPE]                                # default, web, video, print, social (default: web)
  [--base-path /path]                          # Custom base directory
  [--dry-run]                                  # Preview without creating
  [--force]                                    # Overwrite existing structure
```

### Image Command

```bash
toolkit image generate "PROMPT"
  [--seed SEED]                                # Random seed for reproducibility
  [--width WIDTH]                              # Width in pixels (default: 1024)
  [--height HEIGHT]                            # Height in pixels (default: 1024)
```

### Mistral Command

```bash
toolkit ai
  [--prompt "TEXT"]                            # Direct prompt text
  [--prompt-file /path/file.txt]               # Load prompt from file
  [--stdin]                                    # Read from stdin (pipe)
  [--profile PROFILE]                          # code, creative, debug, agency_comms
  [--model MODEL]                              # mistral-tiny, mistral-small-latest, etc
  [--temperature TEMP]                         # 0.0-1.0 (default: 0.7)
  [--max-tokens TOKENS]                        # Max output tokens (default: 1000)
```

## 🔧 Environment Setup

### 1. Installation

```bash
git clone https://github.com/yourusername/agency-toolkit
cd agency-toolkit
pip install -e .

# For development (includes test dependencies)
pip install -e ".[dev]"
```

### 2. Mistral API Key (Required for Mistral commands)

```bash
export MISTRAL_API_KEY='your-api-key-here'
```

Get your key at: https://console.mistral.ai/

### 3. Replicate API Token (Optional - only if using Replicate provider)

```bash
export REPLICATE_API_TOKEN='your-token-here'  # Optional, use for Replicate
```

Get your token at: https://replicate.com/account/api-tokens

> **Note**: Image generation works OUT-OF-THE-BOX with Pollinations.ai (FREE) - no API token required!

### 4. Optional: Pre-commit Hooks (Recommended for developers)

```bash
pip install pre-commit
pre-commit install
```

This will automatically check code quality before committing.

### 5. Optional: Configuration File

Create `~/.config/agency-toolkit/config.toml`:

```toml
[settings]
output_dir = "~/Projects/Agency_Output"
briefing_type = "default"

[colors]
blue = "#0066FF"
red = "#FF0000"
green = "#00AA00"
purple = "#AA00AA"

[formats]
square = [1080, 1080]
story = [1080, 1920]
landscape = [1200, 630]

[mistral]
model = "mistral-small-latest"
temperature = 0.7
max_tokens = 1000

# Mistral Profiles
[mistral.profiles.code]
model = "mistral-small-latest"
temperature = 0.1
system_prompt = "You are an expert code reviewer. Be concise and focus on logic, potential bugs, and DRY principles."

[mistral.profiles.creative]
model = "mistral-medium"
temperature = 0.9
system_prompt = "You are a creative copywriter. Be witty, informal, and generate multiple distinct options."

[mistral.profiles.agency_comms]
model = "mistral-medium"
temperature = 0.7
system_prompt = "You are a senior account manager. Write professional, clear, and empathetic client-facing communications."

[mistral.profiles.debug]
model = "mistral-large-latest"
temperature = 0.0
system_prompt = "You are a debugging assistant. Identify root causes and provide corrected code."
```

## ⚙️ Configuration

### Config File Priority (v1.1+)

**NEW: Project-Based Configuration!** The toolkit now supports multi-level configuration with automatic merging:

**Configuration Priority (highest to lowest)**:
1. **Project config** (`./config.toml` in current directory) - Highest priority
2. **User config** (`~/.config/agency-toolkit/config.toml`) - Medium priority
3. **Application defaults** - Lowest priority

This allows you to:
- Set **global defaults** in your user config
- Override settings **per-project** for different clients
- Share project configs with your team via version control

**Example Workflow**:
```bash
# Global user config at ~/.config/agency-toolkit/config.toml
[settings]
social_style = "modern"
social_color = "blue"

# Client A project config at ~/clients/acme/config.toml
[settings]
output_dir = "./renders"
social_color = "red"  # Brand color overrides global blue

# When you run commands from ~/clients/acme/:
cd ~/clients/acme
toolkit social generate "Hello"
# ✓ Uses red (from project config)
# ✓ Uses modern style (from user config)
# ✓ Outputs to ./renders (from project config)
```

### Config File Format

Create `config.toml` in your project root or `~/.config/agency-toolkit/config.toml`:

```toml
[settings]
output_dir = "~/Documents/Agency_Output"
log_level = "INFO"
social_style = "minimal"
social_color = "blue"

[colors]
blue = "#0000FF"  # Custom brand blue
red = "#FF0000"
```

### Environment Variables
```bash
export MISTRAL_API_KEY="your_api_key_here"  # Required for AI features
```

Get your API key at [console.mistral.ai](https://console.mistral.ai/)

## 📖 Detailed Command Reference

### Social Media (`toolkit social`)

Generate social media post images with various styles and formats.

**Options:**
- `--text TEXT` - Post content (required)
- `--style {modern,minimal,bold}` - Template style (default: modern)
- `--color {blue,red,green,purple,custom}` - Color (default: blue)
- `--custom-color HEX` - Custom hex color (required if color=custom)
- `--format {square,story,landscape}` - Image format (default: square)
- `--dry-run` - Preview without saving

**Example:**

```bash
toolkit social --text "Check out our new project!" --style bold --color purple
```

### Briefing (`toolkit briefing`)

Generate project briefing PDFs with client and project information.

**Modes:**
- `--interactive` - Interactive prompts for each field
- `--from-json FILE` - Load from JSON file

**Example:**

```bash
toolkit briefing --interactive
```

### Structure (`toolkit structure`)

Create organized project folder structures.

**Options:**
- `--client NAME` - Client name (required)
- `--project NAME` - Project name (required)
- `--type {print,web,social,video}` - Structure type (default: web)
- `--base-path PATH` - Base directory (default: output)
- `--force` - Overwrite existing
- `--dry-run` - Preview without creating

**Example:**

```bash
toolkit structure --client "Acme Corp" --project "Website 2024" --type web
```

### AI Assistant (`toolkit ai`)

Interact with Mistral AI models for intelligent assistance.

**Options:**
- `--prompt TEXT` / `-p` - Direct prompt (optional)
- `--prompt-file PATH` / `-f` - Load prompt from file
- `--stdin` - Read prompt from pipe
- `--model TEXT` / `-m` - Model name (default: mistral-small-latest)
- `--temperature FLOAT` - Randomness (0.0-1.0, default: 0.7)
- `--max-tokens INT` - Max response length (default: 1000)
- `--json-output` - Format response as JSON

**Examples:**

```bash
# Quick query
toolkit ai -p "Summarize design thinking principles"

# Analyze code from file
toolkit ai -f code_review_prompt.txt

# Pipe workflow (Unix style!)
cat project_requirements.md | toolkit ai --stdin

# JSON output for scripting
toolkit ai --prompt "List 3 color schemes" --json-output

# Interactive mode (prompts for input)
toolkit ai
```

## 📁 Folder Structure Types

- **web** - For web projects (design, frontend, backend, testing, deployment)
- **print** - For print projects (concept, design, production, final files)
- **social** - For social media (content calendar, assets, posts, analytics)
- **video** - For video projects (scripts, storyboard, footage, editing, export)

## 🧪 Development

### Run tests

```bash
# All tests
pytest tests/ -v --cov=agency_toolkit --cov-report=term-missing

# Specific module
pytest tests/test_mistral.py -v

# Dogfooding test (real API call)
bash scripts/dogfood_test.sh
```

### Quality Checks

```bash
# Code formatting
black agency_toolkit/ tests/

# Linting
ruff check agency_toolkit/ tests/

# Type checking
mypy agency_toolkit/ --strict

# Run all checks
black --check agency_toolkit/ && \
ruff check agency_toolkit/ && \
mypy agency_toolkit/ --strict && \
pytest tests/ -v
```

## 🏗️ Architecture

**Design Philosophy**: Clean architecture + Plugin systems + Unix philosophy

```
agency_toolkit/
├── core/                          # Business logic layer (refactored)
│   ├── social/                   # Social media post generation
│   │   ├── generator.py         # Main orchestrator
│   │   ├── layout.py            # Position & dimension calculations
│   │   ├── rendering.py         # Image drawing
│   │   ├── validators.py        # Input validation
│   │   └── constants.py         # Magic numbers
│   ├── structure/                # Folder structure generation
│   ├── briefing/                 # PDF/MD briefing generation
│   └── mistral/                  # Mistral AI integration
│
├── providers/                     # Plugin architecture for image providers
│   ├── base.py                   # Abstract ImageProvider interface
│   ├── registry.py               # Provider discovery & registration
│   ├── replicate.py              # Replicate API provider
│   └── pollinations.py           # Pollinations.ai provider (FREE)
│
├── commands/                      # Thin CLI command handlers
│   ├── image.py, social.py, etc.
│
├── cli_app.py                     # Typer CLI entry point
├── models.py                      # Pydantic validation models
├── config.py                      # Configuration loading
├── constants.py                   # Global constants
├── exceptions.py                  # Custom exceptions
├── utils.py                       # Shared utilities
└── logger.py                      # Logging setup

templates/                         # JSON templates with schemas
tests/                            # 166 unit & integration tests
  ├── unit/                       # Unit tests
  ├── integration/                # Integration tests
  └── unit/providers/             # Provider plugin tests
scripts/                          # Utility scripts
docs/                            # Documentation
```

**Key Principles**:
- ✅ **Clean Architecture**: Separated concerns (core, providers, commands)
- ✅ **Plugin System**: Extensible image provider architecture
- ✅ **Type-safe**: Full type hints, MyPy strict mode
- ✅ **Tested**: 166 tests, >80% coverage
- ✅ **Validated**: Pydantic models, JSON schemas
- ✅ **Zero Dependencies**: Core features work without API tokens
- ✅ **Composable**: Unix-style pipes and file I/O

## 💻 Tech Stack

| Category | Technology |
|----------|-----------|
| **CLI Framework** | [Typer](https://typer.tiangolo.com/) with Rich output |
| **Image Generation** | [Pillow](https://pillow.readthedocs.io/) |
| **PDF Generation** | [FPDF2](https://pyfpdf.github.io/fpdf2/) |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev/) v2 |
| **AI Integration** | [Mistral AI](https://mistral.ai/) Python SDK |
| **Testing** | [Pytest](https://pytest.org/) with coverage |
| **Code Quality** | Black, Ruff, MyPy |

## 🧑‍💻 Development

For detailed development setup and contribution guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).

**Quick Start for Developers:**
```bash
# Clone and setup
git clone https://github.com/yourusername/agency-toolkit
cd agency-toolkit
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Code quality checks
black --check agency_toolkit/
ruff check agency_toolkit/
mypy agency_toolkit/ --ignore-missing-imports
```

## 🤝 Contributing

Contributions welcome! This project follows:
- **Black** code formatting (88 char line length)
- **Ruff** linting (E, F, W, I, UP, N rules)
- **MyPy** type checking (strict mode in development)
- **Pre-commit hooks** for automated quality checks
- **Pytest** for all new features (aim for 80%+ coverage)

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Architecture guide for adding features
- How to add new image providers
- How to add new CLI commands
- Testing best practices
- Troubleshooting guide

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👤 Author

**Kim Eisele**
- 🌐 GitHub: [github.com/yourusername](https://github.com/yourusername)
- 📧 Contact: Via GitHub Issues

---

**Built with ❤️ for creative agencies**

*This project demonstrates professional Python development practices: type-safe code, comprehensive testing, clean architecture, and production-ready quality.*
