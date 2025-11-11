# Image Generation - Quick Start Guide

> **Status**: Design complete, ready for implementation
> **Architecture**: Blueprint-compliant, fully validated
> **Timeline**: 4 weeks (see ROADMAP Phase 6)

---

## 🎯 What We're Building

**Feature**: AI-generated backgrounds for social media posts

**User Experience**:
```bash
# Before (current)
toolkit social "Product Launch!" --style modern --color blue

# After (new feature)
toolkit social "Product Launch!" --bg-concept "tech startup office"
# → Mistral enhances prompt
# → Replicate generates image
# → Social module overlays text
# → Output: professional post with AI background
```

---

## ✅ Design Validation Checklist

- ✅ **Blueprint Compliant**: NO module cross-imports
- ✅ **Orchestration Layer**: cli_app.py only
- ✅ **Provider Abstraction**: ImageProvider enum (extensible)
- ✅ **Cost Transparent**: Every call returns {"cost": float}
- ✅ **Deterministic**: Same prompt → same seed → same image
- ✅ **Registry Ready**: Pre-optimized prompts in JSON

---

## 📋 Implementation Order (From ROADMAP)

### Week 1: Image Module (Standalone)
**Goal**: `toolkit image "prompt"` command works

**Files to create**:
- `agency_toolkit/image_gen.py` (new)
- `tests/test_image_gen.py` (new)

**Key functions**:
```python
def generate_image(
    prompt: str,
    seed: Optional[int] = None,
    width: int = 1024,
    height: int = 1024,
    provider: ImageProvider = ImageProvider.REPLICATE,
    config = None
) -> dict:
    """
    Returns:
        {
            "path": str,      # Where image saved
            "cost": float,    # USD estimate
            "seed": int,      # Used seed (for reproducibility)
            "model": str      # Model identifier
        }
    """
```

**Dependencies**:
```bash
pip install replicate
export REPLICATE_API_TOKEN='r8_...'  # Get from replicate.com/account
```

---

### Week 2: Orchestration (Social Integration)
**Goal**: `toolkit social "text" --bg-concept "office"` works

**Files to modify**:
- `agency_toolkit/mistral.py` (add enhance_image_prompt)
- `agency_toolkit/social.py` (add background_image_path param)
- `agency_toolkit/cli_app.py` (add --bg-concept flag + orchestration)

**Orchestration flow**:
```python
# In cli_app.py social_cmd()
if bg_concept:
    # Step 1: Enhance prompt (Mistral)
    enhanced = mistral.enhance_image_prompt(bg_concept, config)

    # Step 2: Generate image (Replicate)
    img_result = image_gen.generate_image(enhanced, config=config)

    # Step 3: Overlay text (Social)
    result = social.generate_social_post(
        text=text,
        background_image_path=img_result["path"],
        config=config
    )

    # Step 4: Show cost
    typer.secho(f"💰 Cost: ${img_result['cost']:.4f}", fg="cyan")
```

---

### Week 3: Registry (Pre-optimized Prompts)
**Goal**: `toolkit social "Hi" --bg-concept registry:tech-startup` works

**Files to create**:
- `registry/prompts/image-concepts.json` (new)

**Structure**:
```json
{
  "metadata": {
    "id": "image-concepts",
    "type": "prompts"
  },
  "entries": {
    "tech-startup": {
      "name": "Tech Startup Office",
      "prompt": "modern minimalist tech startup office, large windows...",
      "tags": ["tech", "office"]
    },
    "abstract-gradient": {
      "prompt": "smooth flowing abstract gradient, vibrant blue and purple..."
    }
  }
}
```

---

### Week 4: Polish
- Documentation (README examples)
- Cost estimation guide
- GIF demos
- All tests passing

---

## 🚨 Critical Architecture Rules

### ❌ NEVER DO THIS (Breaks Blueprint)
```python
# social.py
from . import mistral, image_gen  # ❌ WRONG

def generate_social_post(...):
    prompt = mistral.enhance_image_prompt(...)  # ❌ WRONG
    image = image_gen.generate_image(...)       # ❌ WRONG
```

### ✅ ALWAYS DO THIS (Blueprint-Compliant)
```python
# cli_app.py (ONLY place for orchestration)
def social_cmd(...):
    enhanced = mistral.enhance_image_prompt(...)  # ✅ CORRECT
    img_result = image_gen.generate_image(...)    # ✅ CORRECT
    result = social.generate_social_post(
        ...,
        background_image_path=img_result["path"]  # ✅ CORRECT
    )
```

**Why?** Modules must be **pure functions** (testable, reusable, no side effects)

---

## 📊 Cost Estimation (MVP - Phase 1)

**Display per request** (NO persistence in Week 1-4):
```bash
$ toolkit social "Launch!" --bg-concept "office"
🎨 Background generated (seed: 42, cost: $0.0032)
✅ Social post created: output/social_post_20241106.png
💰 Total cost: $0.0032
```

**Replicate pricing** (SDXL model):
- ~$0.003 per image
- Monthly free tier: ~$5 credit
- Deterministic seeds → no wasted generations

---

## 🧪 Testing Strategy

**Every feature MUST have tests**:

```python
# tests/test_image_gen.py
@mock.patch('replicate.Client.run')
def test_generate_image_replicate(mock_run):
    mock_run.return_value = ["https://example.com/image.png"]
    result = image_gen.generate_image("test prompt")
    assert "path" in result
    assert "cost" in result
    assert result["cost"] > 0

# tests/test_cli_orchestration.py
def test_social_with_bg_concept(mock_mistral, mock_image_gen):
    # Test full flow: mistral → image_gen → social
    ...
```

---

## 📚 Reference Documents

- **Full design**: `docs/implementation_image_gen.yaml` (420 lines)
- **Architecture**: `docs/BLUEPRINT.yaml` (updated with image_gen)
- **Implementation**: `docs/IMPLEMENTATION.yaml` (now includes image_gen section)
- **Roadmap**: `docs/ROADMAP.md` (Phase 6 = 4-week breakdown)

---

## 🏁 Ready to Start?

**Immediate next action**:
```bash
# 1. Install dependency
pip install replicate

# 2. Get API token
# Visit: https://replicate.com/account/api-tokens
# Export: export REPLICATE_API_TOKEN='r8_...'

# 3. Create module
touch agency_toolkit/image_gen.py

# 4. Start with _generate_seed() function (simplest)
# Then generate_image() with Replicate API
```

**First milestone**: `toolkit image "test"` generates a PNG file

---

## 💡 Pro Tips

1. **Start small**: `_generate_seed()` → `generate_image()` → tests
2. **Mock early**: Don't spam Replicate API during dev (costs money)
3. **Seed everything**: Use deterministic seeds for reproducible tests
4. **Cost first**: Return cost from Day 1 (easy to forget later)
5. **No shortcuts**: Don't skip orchestration layer (cli_app.py does the wiring)

---

**Questions?** Check `docs/BLUEPRINT.yaml` (module rules) or `docs/IMPLEMENTATION.yaml` (image_gen section)
