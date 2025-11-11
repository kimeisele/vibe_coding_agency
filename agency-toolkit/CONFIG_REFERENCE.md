# 🔧 Agency Toolkit - Configuration Reference

## Quick Setup

### 1. Environment Variables (Required)

```bash
# Mistral AI API Key (required for mistral commands)
export MISTRAL_API_KEY='sk-...'

# Replicate API Token (required for image generation)
export REPLICATE_API_TOKEN='r8_...'
```

### 2. Configuration File (Optional)

Create `~/.config/agency-toolkit/config.toml`:

```toml
[settings]
output_dir = "~/Projects/Agency_Output"
briefing_type = "default"
social_style = "modern"
social_color = "blue"
social_format = "square"

[colors]
# Named colors (can be overridden)
blue = "#2E5EAA"
red = "#D32F2F"
green = "#43A047"
purple = "#8E24AA"

[formats]
# Image format dimensions
square = [1080, 1080]
story = [1080, 1920]
landscape = [1200, 630]

[mistral]
# Default Mistral settings
model = "mistral-small-latest"
temperature = 0.7
max_tokens = 1000

# Mistral Profiles - Pre-configured settings
[mistral.profiles.code]
model = "mistral-small-latest"
temperature = 0.1
system_prompt = "You are an expert code reviewer. Be concise, accurate, and focus on logic, potential bugs, and adherence to DRY/SRP principles. Provide output as commented code blocks."

[mistral.profiles.creative]
model = "mistral-medium"
temperature = 0.9
system_prompt = "You are a creative copywriter for a young, bold brand. Be witty, informal, and generate 5 distinct options for social media posts."

[mistral.profiles.agency_comms]
model = "mistral-medium"
temperature = 0.7
system_prompt = "You are a senior account manager at a digital agency. Write professional, clear, and empathetic client-facing emails. Be polite, set clear expectations, and confirm next steps."

[mistral.profiles.debug]
model = "mistral-large-latest"
temperature = 0.0
system_prompt = "You are a debugging assistant. Analyze the following error log and code. Identify the root cause, explain it clearly, and provide the corrected code. State your hypothesis first."
```

---

## 🆕 Configuration Priority Chain (v1.1+)

**NEW**: The toolkit now supports **project-based configuration** with automatic merging from multiple locations.

### Priority Order (Highest to Lowest)

1. **Project Config** - `./config.toml` in current working directory
   - Highest priority - overrides all other settings
   - Perfect for client/project-specific settings
   - Can be version-controlled and shared with team

2. **User Config** - `~/.config/agency-toolkit/config.toml`
   - Medium priority - your personal global defaults
   - Settings used across all projects (unless overridden)

3. **Application Defaults** - Hardcoded fallbacks
   - Lowest priority - used when no config files exist

### Configuration Merging Example

```toml
# User config: ~/.config/agency-toolkit/config.toml
[settings]
output_dir = "./global-output"
social_style = "modern"
social_color = "blue"
```

```toml
# Project config: ~/clients/acme/config.toml
[settings]
output_dir = "./acme-renders"  # Overrides user config
social_color = "red"            # Overrides user config
# social_style NOT set - inherits "modern" from user config
```

**Result when running from** `~/clients/acme/`:
- `output_dir` = `"./acme-renders"` (from project)
- `social_color` = `"red"` (from project)
- `social_style` = `"modern"` (from user - not overridden)

---

## 🆕 Batch Social Media Generation (v1.1+)

**NEW**: Generate entire campaigns from CSV or JSON files.

### CSV Format

```bash
toolkit social generate --from-csv campaign.csv
```

**Required CSV header**: `text`
**Optional headers**: `style`, `color`, `format`, `bg_concept`

Example `campaign.csv`:
```csv
text,style,color,format
"Launch Day! 🚀","bold","blue","square"
"Summer Sale - 50% OFF","modern","red","landscape"
"New Product Coming","minimal","green","story"
```

### JSON Format

```bash
toolkit social generate --from-json posts.json
```

Example `posts.json`:
```json
[
  {
    "text": "Monday Motivation ✨",
    "style": "modern",
    "color": "blue"
  },
  {
    "text": "Flash Sale Ends Tonight!",
    "style": "bold",
    "color": "red",
    "format": "story"
  }
]
```

### Batch Processing Features

- **Automatic validation**: Skips rows with empty text, continues processing
- **Error handling**: Reports which rows failed while continuing with others
- **Summary report**: Shows `Generated X/Y posts` with failure count
- **Optional parameters**: Missing columns use config defaults or application defaults

---

## Available Options

### Global Options (all commands)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--help` | flag | - | Show help message |
| `--version` | flag | - | Show version |
| `--verbose` / `-v` | flag | false | Enable debug logging |
| `--quiet` / `-q` | flag | false | Suppress output (warnings only) |
| `--output-dir` | path | `./output` | Override default output directory |
| `--json` | flag | false | Output as JSON (for automation/agents) |

### Social Command

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `--text` | string | - | **YES** | Main text content for the post |
| `--style` | enum | `modern` | no | Template style: `modern`, `bold`, `minimal` |
| `--color` | enum | `blue` | no | Color: `blue`, `red`, `green`, `purple`, or hex `#RRGGBB` |
| `--custom-color` | string | - | no | Custom hex color (if `--color custom`) |
| `--format` | enum | `square` | no | Image format: `square`, `story`, `landscape` |
| `--output` | path | `./output/social` | no | Custom output directory |
| `--dry-run` | flag | false | no | Preview without saving |

**Examples**:
```bash
toolkit social --text "Hello World"
toolkit social --text "Hello" --style bold --color red
toolkit social --text "Post" --format story --custom-color "#FF6600"
toolkit --json social --text "Hello"
```

---

### Briefing Command

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `--type` | enum | `default` | no | Template type: `default`, `web`, `video` |
| `--format` | enum | `pdf` | no | Output format: `pdf` or `md` |
| `--from-json` | path | - | no | Load briefing from JSON file (instead of interactive) |
| `--dry-run` | flag | false | no | Preview without saving |

**Templates**:
- `default`: The 5 W's (Who, What, When, Where, Why)
- `web`: Web project specifics (pages, CMS, hosting, SEO)
- `video`: Video production specifics (platform, format, voiceover, music)

**Examples**:
```bash
toolkit briefing
toolkit briefing --type web
toolkit briefing --type video --format md
toolkit briefing --from-json briefing.json
toolkit --json briefing --type default
```

---

### Structure Command

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `--client` | string | - | **YES** | Client name |
| `--project` | string | - | **YES** | Project name |
| `--type` | enum | `web` | no | Structure type: `default`, `web`, `video`, `print`, `social` |
| `--base-path` | path | `./output` | no | Custom base directory |
| `--dry-run` | flag | false | no | Preview without creating |
| `--force` | flag | false | no | Overwrite existing structure |

**Structure Types**:
- `default`: Generic project structure (src, docs, data, tests)
- `web`: React/Vue frontend (components, pages, styles, assets)
- `video`: Video editing (footage, audio, assets, renders)
- `print`: Print design project
- `social`: Social media project

**Examples**:
```bash
toolkit structure --client "Acme" --project "Website 2024" --type web
toolkit structure --client "Studio" --project "Brand Video" --type video
toolkit structure --client "Test" --project "Test" --base-path /custom/path
toolkit structure --client "Acme" --project "Web" --force
toolkit --json structure --client "Acme" --project "Web"
```

---

### Image Command

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `prompt` | string | - | **YES** | Text prompt for image generation |
| `--seed` | integer | auto | no | Random seed (same seed = reproducible image) |
| `--width` | integer | 1024 | no | Image width in pixels |
| `--height` | integer | 1024 | no | Image height in pixels |

**Examples**:
```bash
toolkit image generate "modern office with windows"
toolkit image generate "sunset landscape" --width 1200 --height 630
toolkit image generate "cat portrait" --seed 12345
toolkit --json image generate "beautiful nature scene"
```

---

### Mistral Command

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `--prompt` / `-p` | string | - | no | Direct prompt text |
| `--prompt-file` / `-f` | path | - | no | Load prompt from file |
| `--stdin` | flag | false | no | Read prompt from stdin (pipe) |
| `--profile` | enum | - | no | Profile: `code`, `creative`, `debug`, `agency_comms` |
| `--model` / `-m` | enum | `mistral-small-latest` | no | Model to use |
| `--temperature` | float | 0.7 | no | Randomness (0.0 = deterministic, 1.0 = creative) |
| `--max-tokens` | integer | 1000 | no | Maximum output tokens |

**Profiles**:
- `code`: Code review (temperature 0.1) - precise, analytical
- `creative`: Creative copywriting (temperature 0.9) - multiple options
- `agency_comms`: Professional communication (temperature 0.7)
- `debug`: Debugging assistant (temperature 0.0) - deterministic

**Models**:
- `mistral-tiny` - Fastest, smallest
- `mistral-small-latest` - Default, good balance
- `mistral-medium` - Larger context
- `mistral-large-latest` - Most capable

**Examples**:
```bash
# Direct prompt
toolkit ai --prompt "Hello, world!"

# Using profiles
toolkit ai --profile code --prompt "Review this function"
toolkit ai --profile creative --prompt "Generate headlines"
toolkit ai --profile debug --prompt "Error analysis"

# From file
toolkit ai --prompt-file prompt.txt

# From stdin
cat code.py | toolkit ai --profile code --stdin

# Custom temperature
toolkit ai --prompt "Hello" --temperature 0.1

# JSON output
toolkit --json mistral --prompt "Hello"

# Interactive
toolkit ai
```

---

## Priority Order

Configuration is loaded in this priority order (highest to lowest):

1. **CLI flags** (e.g., `--prompt`, `--profile`, `--temperature`)
2. **Mistral profile** (from `--profile`, merged into config)
3. **User config** (`~/.config/agency-toolkit/config.toml`)
4. **Program defaults** (from `config.py`)

Example:
```bash
# Temperature: 0.2 (from CLI flag)
toolkit ai --prompt "Hello" --temperature 0.2

# Temperature: 0.1 (from code profile)
toolkit ai --profile code --prompt "Hello"

# Temperature: 0.7 (from config.toml [mistral] section)
toolkit ai --prompt "Hello"
```

---

## JSON Output Format

When using `--json` flag, all commands output:

```json
{
  "status": "success|error",
  "module": "social|briefing|structure|mistral|image",
  "message": "error message (if status=error)",
  ... (module-specific fields)
}
```

**Social**:
```json
{
  "status": "success",
  "module": "social",
  "path": "/path/to/image.png",
  "style": "modern",
  "color": "#2E5EAA",
  "format": "square"
}
```

**Mistral**:
```json
{
  "status": "success",
  "module": "mistral",
  "response": "The AI response text",
  "model": "mistral-small-latest",
  "temperature": 0.7
}
```

**Briefing**:
```json
{
  "status": "success",
  "module": "briefing",
  "path": "/path/to/briefing.pdf",
  "type": "default",
  "format": "pdf"
}
```

**Structure**:
```json
{
  "status": "success",
  "module": "structure",
  "path": "/path/to/project",
  "client": "Acme",
  "project": "Website 2024",
  "type": "web"
}
```

---

## Default Locations

- **Output**: `./output/`
- **Config**: `~/.config/agency-toolkit/config.toml`
- **Logs**: `./output/toolkit.log`
- **Social posts**: `./output/social/`
- **Briefings**: `./output/briefings/`
- **Structures**: `./output/`
