# Migration Guide: v0.1 → v0.2+

This guide explains the architectural changes in v0.2+ and how to update your code if you have custom integrations.

## 📋 Overview of Changes

The v0.2+ release includes a major architectural refactoring to improve maintainability and extensibility:

1. **New Plugin Architecture** - Image generation now supports multiple providers
2. **Core/Providers Split** - Business logic separated from provider implementations
3. **God Function Refactoring** - Large functions broken into smaller, testable units
4. **Free Image Generation** - Pollinations.ai provider (no API token required by default)
5. **Backward Compatibility** - All old APIs still work via compatibility wrappers

**Migration Difficulty**: ⚠️ **Low** (backward compatible)

---

## 🔄 What Changed?

### Image Generation (Biggest Change)

#### Before (v0.1)
```bash
# Only Replicate supported, required API token
export REPLICATE_API_TOKEN="your-token"
toolkit image generate "A sunset"
```

#### After (v0.2+)
```bash
# Pollinations.ai is default (FREE - no token needed!)
toolkit image generate "A sunset"

# Still supports Replicate if you have token
toolkit image generate "A sunset" --provider replicate
```

**No code changes needed** - the CLI interface is the same!

### Python API Changes (If you use the library)

#### Before (v0.1)
```python
from agency_toolkit import image_gen

# Direct function import
result = image_gen.generate_image(
    prompt="A sunset",
    seed=42,
    config=config
)
```

#### After (v0.2+)
```python
from agency_toolkit import image_gen

# Same interface, but now uses plugin architecture under the hood
result = image_gen.generate_image(
    prompt="A sunset",
    seed=42,
    provider="pollinations",  # Optional, defaults to pollinations
    config=config
)
```

**✅ Backward compatible** - old code still works!

---

## 🛠️ Do I Need To Update?

### If you're using the CLI
**No action needed.** All CLI commands work identically to before.

Example (no changes):
```bash
toolkit social --text "Hello" --style modern
toolkit structure --client "Acme" --project "Web"
toolkit briefing --type web
```

### If you're importing from agency_toolkit
**No action needed.** All imports still work via backward-compatibility wrappers.

Example (no changes):
```python
from agency_toolkit.social import generate_social_post
from agency_toolkit.structure import create_folder_structure
```

### If you're adding custom image providers
**New capability!** You can now add providers by implementing the `ImageProvider` interface:

```python
from agency_toolkit.providers.base import ImageProvider
from agency_toolkit.providers.registry import register_provider

class MyCustomProvider(ImageProvider):
    def generate(self, prompt, seed, width, height, config):
        # Your implementation
        return {
            "path": str(image_path),
            "cost": cost,
            "seed": seed,
            "model": model_name,
            "provider": "my_provider",
        }

    def estimate_cost(self) -> float:
        return 0.0

    def supports_seed(self) -> bool:
        return True

    def max_dimensions(self) -> tuple[int, int]:
        return (2048, 2048)

# Register your provider
register_provider("my_provider", MyCustomProvider)

# Use it
from agency_toolkit import image_gen
result = image_gen.generate_image(
    "A test",
    provider="my_provider",
    config=config
)
```

---

## 🔌 Architecture Changes

### Old Architecture
```
agency_toolkit/
├── social.py        # 129-line god function ❌
├── structure.py     # 114-line god function ❌
├── briefing.py      # 94-line god function ❌
├── image_gen.py     # Hardcoded Replicate API ❌
└── models.py        # Global config
```

### New Architecture
```
agency_toolkit/
├── core/                 # ✅ New: Modular business logic
│   ├── social/          # Refactored: 10+ small functions
│   ├── structure/       # Refactored: 10+ small functions
│   ├── briefing/        # Refactored: 10+ small functions
│   └── mistral/         # New module
│
├── providers/           # ✅ New: Plugin system
│   ├── base.py         # Abstract provider interface
│   ├── registry.py     # Provider registration
│   ├── replicate.py    # Replicate provider
│   └── pollinations.py # Pollinations provider (FREE)
│
├── social.py           # ✅ Backward-compat wrapper
├── structure.py        # ✅ Backward-compat wrapper
├── briefing.py         # ✅ Backward-compat wrapper
├── image_gen.py        # ✅ Now uses providers
└── models.py           # Updated: supports multiple providers
```

---

## 📝 What's Backward Compatible

### CLI Commands
✅ **All commands work identically**
```bash
toolkit social --text "..." --style modern
toolkit structure --client "..." --project "..."
toolkit briefing --type web
toolkit image generate "..."
toolkit ai --prompt "..."
```

### Python Imports
✅ **All old imports still work**
```python
# These all still work:
from agency_toolkit.social import generate_social_post
from agency_toolkit.structure import create_folder_structure
from agency_toolkit.briefing import generate_briefing
from agency_toolkit import image_gen
from agency_toolkit.mistral import call_mistral_api
```

### Configuration
✅ **Existing config files work as-is**
```toml
# Old config files still work
[settings]
output_dir = "~/output"
social_style = "modern"
```

### API Responses
✅ **Return values unchanged**
```python
result = image_gen.generate_image(...)
# Still returns:
# {
#     "path": "...",
#     "cost": 0.0,
#     "seed": 42,
#     "model": "...",
#     "provider": "..."
# }
```

---

## ⚠️ What's NOT Backward Compatible

### Internal Implementation Details
❌ **These internal functions changed (shouldn't use them anyway)**
- `agency_toolkit.image_gen._generate_replicate()` → Now `replicate.py`
- `agency_toolkit.image_gen._estimate_cost()` → Now in providers

**If you were using these private functions**, use the public API instead:
```python
# ❌ Don't do this (private function)
from agency_toolkit.image_gen import _generate_replicate

# ✅ Do this instead (public API)
from agency_toolkit.image_gen import generate_image
result = generate_image("prompt", provider="replicate", config=config)
```

### Internal File Organization
❌ **Internal code moved to core/**

If you were importing directly from internal modules, update imports:
```python
# ❌ Old (may not work)
from agency_toolkit.social import _layout_dimensions

# ✅ New
from agency_toolkit.core.social.layout import calculate_dimensions
```

---

## 🔄 Migration Steps

### For Most Users (No Action Needed)
If you only use the CLI, no migration needed! Everything works as before.

### For Library Users
If you import from `agency_toolkit`, no migration needed! Backward-compat wrappers handle it.

### If You Extended the Code

**Old way:**
```python
# Modifying global variables in social.py
import agency_toolkit.social as social
social.TITLE_SIZE = 50  # ❌ Don't do this
```

**New way:**
```python
# Modify constants in the right place
from agency_toolkit.core.social.constants import TITLE_FONT_SIZE_RATIO
# Update the constant in agency_toolkit/core/social/constants.py instead
```

### If You Added Custom Providers

**Before:**
You had to modify `image_gen.py` directly.

**After:**
```python
# ✅ Create your provider as a plugin
from agency_toolkit.providers.base import ImageProvider
from agency_toolkit.providers.registry import register_provider

class MyProvider(ImageProvider):
    # ... implementation ...

register_provider("my_provider", MyProvider)
```

---

## 🧪 Testing Your Migration

### Verify CLI Still Works
```bash
# These should all still work
toolkit social --text "Test" --style modern
toolkit structure --client "Test" --project "Test"
toolkit briefing --type default
toolkit image generate "A test"
```

### Verify Python API Still Works
```python
# These should all still work
from agency_toolkit.social import generate_social_post
from agency_toolkit.structure import create_folder_structure
from agency_toolkit import image_gen

result = image_gen.generate_image("test", config=config)
```

### Verify Free Image Generation Works
```bash
# This should work WITHOUT REPLICATE_API_TOKEN
toolkit image generate "A sunset"

# Check it used Pollinations (should show "Provider: pollinations")
```

---

## 📊 Performance Changes

### Good News
- ✅ **Faster imports** - Lazy loading of providers
- ✅ **Faster image generation** - Pollinations.ai is fast!
- ✅ **Lower latency** - No need to wait for Replicate startup

### No Changes
- Image quality remains the same
- CLI output format unchanged
- Configuration behavior unchanged

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'agency_toolkit.core.social'"
This means you're importing a private internal module. Use the public API instead.

**Fix:**
```python
# ❌ Wrong
from agency_toolkit.core.social.layout import calculate_dimensions

# ✅ Right
from agency_toolkit.core.social import generate  # Public function
```

### "ImageProviderError: Unknown provider 'my_provider'"
You created a custom provider but didn't register it.

**Fix:**
```python
from agency_toolkit.providers.registry import register_provider

class MyProvider(...):
    ...

# Register it!
register_provider("my_provider", MyProvider)
```

### "Image generation failing despite no API token change"
Check the default provider:

```bash
# Verify Pollinations is working
toolkit image generate "A test" --provider pollinations

# If Replicate token is set, it tries Replicate by default in v0.1
# In v0.2+, use explicit --provider flag
toolkit image generate "A test" --provider replicate
```

---

## 📚 Documentation

New documentation for the refactored architecture:
- [DEVELOPMENT.md](DEVELOPMENT.md) - How to contribute and develop
- [REFACTORING_EPIC.md](REFACTORING_EPIC.md) - Technical details of changes
- [PROGRESS_ASSESSMENT.md](PROGRESS_ASSESSMENT.md) - Current state and metrics

---

## 🎯 Checklist for Migration

- [ ] Review this guide
- [ ] Test that your CLI commands still work
- [ ] Test that your Python imports still work
- [ ] Verify free image generation works (no token needed)
- [ ] Update any custom provider code to use new plugin system
- [ ] Review [DEVELOPMENT.md](DEVELOPMENT.md) if you plan to extend

---

**Need help?** Check [DEVELOPMENT.md](DEVELOPMENT.md) or create an issue on GitHub.

---

**Last Updated**: November 7, 2025
**Version**: v0.2+
