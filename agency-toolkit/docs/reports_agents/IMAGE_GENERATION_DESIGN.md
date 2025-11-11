# Image Generation Service Design

**Status:** 📋 Design Phase
**Created:** 2025-11-06
**Author:** Deep Dive Research

---

## 1. EXECUTIVE SUMMARY

This document outlines the design for adding **AI-powered image generation** to Agency Toolkit, integrated with the existing Mistral service for intelligent prompt creation. The goal is to provide **deterministic, configurable, professional-quality** images for social media posts and other use cases.

### Key Insight
**Mistral AI does NOT provide image generation**. Pixtral is a vision model (image→text), not a generative model (text→image). We need a hybrid approach: **Mistral generates/optimizes prompts → External image API generates images**.

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 Hybrid Architecture (Recommended)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│   User      │──────▶│   Mistral    │──────▶│  Image Provider │
│  Request    │ text  │   Service    │prompt │   (Pluggable)   │
└─────────────┘       └──────────────┘       └─────────────────┘
                              │                        │
                              │                        ▼
                              │                 ┌─────────────┐
                              │                 │  PNG/JPEG   │
                              └────────────────▶│   Output    │
                                     metadata   └─────────────┘
```

**Flow:**
1. User provides concept/description (e.g., "tech startup launch")
2. Mistral enriches into optimized prompt (e.g., "modern minimalist tech startup office, sunrise lighting, professional photography, 4k")
3. Image provider generates image with deterministic seed
4. Result cached/returned with metadata

---

## 3. PROVIDER OPTIONS ANALYSIS

### Option A: Stable Diffusion (stability.ai) ⭐ **RECOMMENDED**
- **Pros:** Professional quality, API available, good pricing, flexible models
- **Cons:** Requires API key, costs ~$0.002-0.01/image
- **Deterministic:** ✅ Via seed parameter
- **Setup:** Medium (API key, HTTP client)
- **Models:** SDXL, SD 1.5, SD 3.0

### Option B: DALL-E (OpenAI)
- **Pros:** Excellent quality, simple API, familiar ecosystem
- **Cons:** More expensive (~$0.04/image), less control over seeds
- **Deterministic:** ⚠️ Limited (no seed control in API v1)
- **Setup:** Easy (similar to Mistral integration)
- **Models:** DALL-E 3, DALL-E 2

### Option C: Local Stable Diffusion (ComfyUI/A1111)
- **Pros:** Free, full control, no API limits, 100% deterministic
- **Cons:** Requires GPU, complex setup, not portable
- **Deterministic:** ✅ Full control
- **Setup:** Hard (local server, model downloads)
- **Models:** Any HuggingFace model

### Option D: Flux.1 (Black Forest Labs) ⭐ **FUTURE**
- **Pros:** Open source, state-of-the-art quality, fast
- **Cons:** Still new, API availability unclear, local setup needed
- **Deterministic:** ✅ Open source = full control
- **Setup:** Hard (emerging ecosystem)
- **Models:** Flux.1 [dev], Flux.1 [schnell]

### Option E: Replicate (replicate.com) 💡 **EASIEST**
- **Pros:** Dead simple API, multiple models, pay-per-use
- **Cons:** Costs add up, less control
- **Deterministic:** ✅ Via seed parameter
- **Setup:** Easy (API key only)
- **Models:** SDXL, Flux, Kandinsky, etc.

---

## 4. RECOMMENDED IMPLEMENTATION

### 4.1 Phase 1: MVP with Replicate (Week 1)
**Why:** Fastest time-to-value, test concept, validate UX

```python
# New module: agency_toolkit/image_gen.py

from enum import Enum
from typing import Optional, Dict
from pathlib import Path

class ImageProvider(Enum):
    REPLICATE = "replicate"
    STABILITY = "stability"
    DALLE = "dalle"
    # Future: LOCAL = "local"

def generate_image(
    prompt: str,
    provider: ImageProvider = ImageProvider.REPLICATE,
    model: str = "stability-ai/sdxl",
    seed: Optional[int] = None,
    width: int = 1024,
    height: int = 1024,
    output_path: Optional[Path] = None,
    **kwargs
) -> Dict:
    """Generate image from text prompt.

    Args:
        prompt: Text description of desired image
        provider: Which image generation service to use
        model: Provider-specific model name
        seed: Random seed for deterministic generation
        width, height: Output dimensions
        output_path: Where to save (None = temp file)
        **kwargs: Provider-specific options

    Returns:
        Dict with keys: path, url, seed, cost, metadata
    """
    pass
```

### 4.2 Phase 2: Mistral Prompt Enhancement (Week 2)
Leverage Mistral to create better prompts:

```python
# In agency_toolkit/mistral.py

PROMPT_ENHANCER_PROFILE = {
    "name": "image_prompt_enhancer",
    "system_prompt": """You are an expert at writing prompts for AI image generation.

Given a concept or brief description, create a detailed, professional prompt optimized for
Stable Diffusion / DALL-E. Include:
- Art style and medium
- Lighting and mood
- Composition details
- Quality tags (4k, professional, etc.)

Output ONLY the enhanced prompt, no explanation.""",
    "temperature": 0.3,  # Lower for consistency
    "max_tokens": 200
}

def enhance_image_prompt(concept: str) -> str:
    """Use Mistral to convert concept into optimized image prompt."""
    return query_mistral(
        prompt=f"Concept: {concept}",
        profile="image_prompt_enhancer"
    )["response"]
```

### 4.3 Phase 3: Integration with Social Module (Week 3)
Add image background generation:

```python
# Enhanced agency_toolkit/social.py

def generate_social_post(
    text: str,
    style: str = "modern",
    background: str = "gradient",  # NEW: "gradient" | "image" | "solid"
    background_concept: Optional[str] = None,  # NEW: AI image concept
    seed: Optional[int] = None,  # NEW: Deterministic images
    **kwargs
) -> dict:
    """Generate social media post with optional AI background."""

    if background == "image" and background_concept:
        # Use Mistral to enhance prompt
        enhanced_prompt = enhance_image_prompt(background_concept)

        # Generate background image
        bg_result = generate_image(
            prompt=enhanced_prompt,
            seed=seed or hash(text),  # Deterministic from text
            width=1080, height=1080
        )

        # Composite text over generated image
        # ... (existing PIL logic but with generated background)
```

---

## 5. CONFIGURATION STRATEGY

### 5.1 Config Structure (`config.toml`)

```toml
[image_generation]
# Provider selection (replicate, stability, dalle, local)
provider = "replicate"

# Default model per provider
replicate_model = "stability-ai/sdxl:latest"
stability_model = "stable-diffusion-xl-1024-v1-0"
dalle_model = "dall-e-3"

# Determinism controls
default_seed = null  # null = random, int = fixed
seed_strategy = "hash_content"  # "hash_content" | "fixed" | "random"

# Quality settings
default_width = 1024
default_height = 1024
default_quality = "standard"  # "draft" | "standard" | "hd"

# Cost controls
max_cost_per_image = 0.10  # USD
daily_budget = 5.00  # USD
enable_caching = true  # Cache by prompt hash

# Mistral integration
use_mistral_enhancement = true
enhancement_profile = "image_prompt_enhancer"
```

### 5.2 Environment Variables

```bash
# Provider API keys (at least one required)
export REPLICATE_API_TOKEN="r8_..."
export STABILITY_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."  # For DALL-E

# Optional overrides
export IMAGE_PROVIDER="replicate"
export IMAGE_DEFAULT_SEED="42"
```

---

## 6. DETERMINISTIC IMAGE GENERATION

### 6.1 Seed Strategies

**Strategy A: Hash Content** (Default)
- Pros: Same content = same image, no manual seed tracking
- Cons: Small text changes = different image
```python
seed = hash(text + background_concept) % (2**32)
```

**Strategy B: Fixed Seed**
- Pros: Perfect consistency across all generations
- Cons: Every image identical (boring)
```python
seed = 42  # From config
```

**Strategy C: Incremental Seed**
- Pros: Reproducible sequence, varied but trackable
- Cons: Requires state management
```python
seed = last_seed + 1  # Stored in DB/file
```

**Strategy D: Date-based Seed**
- Pros: Daily variety, reproducible by date
- Cons: Not content-aware
```python
seed = int(datetime.now().strftime("%Y%m%d"))
```

### 6.2 Recommended Approach
**Hybrid: Hash + Salt**
```python
def generate_deterministic_seed(
    content: str,
    salt: Optional[str] = None,
    date_aware: bool = False
) -> int:
    """Generate reproducible but configurable seed."""
    components = [content]

    if salt:
        components.append(salt)

    if date_aware:
        components.append(datetime.now().strftime("%Y-%m-%d"))

    combined = "|".join(components)
    return int(hashlib.sha256(combined.encode()).hexdigest()[:8], 16)
```

---

## 7. IMPLEMENTATION CHECKLIST

### 7.1 Core Module (`agency_toolkit/image_gen.py`)
- [ ] Abstract provider interface
- [ ] Replicate provider implementation
- [ ] Seed management utilities
- [ ] Cost tracking (optional)
- [ ] Result caching (optional)
- [ ] Error handling (rate limits, quotas)

### 7.2 Mistral Integration
- [ ] Add prompt enhancement profile
- [ ] `enhance_image_prompt()` function
- [ ] Optional: Batch prompt enhancement

### 7.3 Social Module Integration
- [ ] Add `background="image"` option
- [ ] Add `background_concept` parameter
- [ ] Add `seed` parameter for determinism
- [ ] Composite logic for text over AI image

### 7.4 Configuration
- [ ] Add `[image_generation]` section to config.toml
- [ ] Environment variable handling
- [ ] Provider auto-detection (check API keys)

### 7.5 CLI Commands
- [ ] `agency image "concept" --seed 42` (standalone image gen)
- [ ] `agency social "text" --bg-concept "sunset" --seed 42`
- [ ] `agency image-prompt "concept"` (test prompt enhancement)

### 7.6 Testing
- [ ] Unit tests for seed generation
- [ ] Integration tests with mocked APIs
- [ ] Manual tests with real providers
- [ ] Determinism validation tests

### 7.7 Documentation
- [ ] Update README with image gen examples
- [ ] Provider setup guides (API keys)
- [ ] Prompt engineering tips
- [ ] Cost estimation table

---

## 8. COST ANALYSIS

### 8.1 Pricing (as of Nov 2024)

| Provider    | Model         | Cost/Image | Quality | Speed  |
|-------------|---------------|------------|---------|--------|
| Replicate   | SDXL          | ~$0.0032   | High    | ~5s    |
| Stability AI| SDXL          | ~$0.004    | High    | ~3s    |
| OpenAI      | DALL-E 3 HD   | $0.080     | Highest | ~10s   |
| OpenAI      | DALL-E 3 Std  | $0.040     | High    | ~10s   |
| Local SD    | SDXL (local)  | $0.00      | High    | ~8s*   |

*Requires GPU, electricity costs not included

### 8.2 Budget Recommendations
- **Hobbyist/Testing:** $5/month (~1,500 images with Replicate)
- **Small Agency:** $20/month (~6,000 images)
- **Production:** $100+/month or local setup

---

## 9. EXAMPLE USAGE SCENARIOS

### 9.1 Deterministic Social Posts
```bash
# Same command always generates same image
agency social "New Product Launch!" \
  --bg-concept "tech startup office" \
  --seed 12345 \
  --style modern \
  --color blue
```

### 9.2 Daily Themed Content
```python
# Each day gets unique but reproducible images
today_seed = int(datetime.now().strftime("%Y%m%d"))

generate_social_post(
    text="Monday Motivation",
    background="image",
    background_concept="inspiring workspace",
    seed=today_seed
)
```

### 9.3 Brand-Consistent Variations
```python
# Use brand hash as salt for consistency
brand_salt = "acme_corp_2024"

for message in campaign_messages:
    seed = generate_deterministic_seed(message, salt=brand_salt)
    generate_social_post(text=message, seed=seed, ...)
```

---

## 10. RISKS & MITIGATIONS

### Risk 1: API Costs Spiral
**Mitigation:**
- Implement daily budget limits
- Cache results by prompt hash
- Dry-run mode for testing
- Cost alerts

### Risk 2: Inconsistent Quality
**Mitigation:**
- Use Mistral prompt enhancement
- Provider-specific quality presets
- Manual prompt override option

### Risk 3: API Rate Limits
**Mitigation:**
- Exponential backoff
- Queue system for batch jobs
- Multiple provider fallback

### Risk 4: Determinism Fails
**Mitigation:**
- Store seed in image metadata
- Test suite validates reproducibility
- Document provider-specific behaviors

---

## 11. FUTURE ENHANCEMENTS

### Phase 4: Advanced Features
- **Template Library:** Pre-made concepts ("tech", "nature", "abstract")
- **Style Transfer:** Apply brand visual identity
- **Multi-Image:** Generate variations, pick best
- **Upscaling:** Integrate with Real-ESRGAN
- **Inpainting:** Edit specific image regions

### Phase 5: Local Setup
- ComfyUI integration for offline generation
- Model management (download SDXL, etc.)
- GPU auto-detection

### Phase 6: Smart Features
- **Prompt Library:** Learn from successful prompts
- **A/B Testing:** Generate variants, track engagement
- **Brand Safety:** Filter inappropriate content
- **Auto-tagging:** Extract metadata from images

---

## 12. DECISION: NEXT STEPS

### Recommended Path Forward

1. **Week 1:** Implement Replicate provider (fastest MVP)
2. **Week 2:** Add Mistral prompt enhancement
3. **Week 3:** Integrate with social module
4. **Week 4:** Add Stability AI provider (more control)
5. **Future:** Local setup for advanced users

### Go/No-Go Criteria
- ✅ **GO if:** User wants AI backgrounds for social posts
- ✅ **GO if:** Budget allows ~$5-20/month for API costs
- ✅ **GO if:** Deterministic/reproducible images needed
- ⚠️ **HOLD if:** Pure text overlays sufficient for now
- 🛑 **NO-GO if:** Zero budget, no API access possible

---

## 13. QUESTIONS FOR USER

Before implementation, please confirm:

1. **Budget:** What's acceptable monthly cost for image generation?
2. **Provider:** Start with Replicate (easy) or Stability (more control)?
3. **Scope:** Social media only, or broader use cases?
4. **Determinism:** Hash-based seeds (auto) or manual seed control?
5. **Quality:** Draft quality OK for testing, or need HD from day 1?

---

**END OF DESIGN DOCUMENT**

*Next step: Review & approve, then create implementation tickets*
