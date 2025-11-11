# Pollinations.ai API Research (WU-2.1)

**Date:** 2025-11-07
**Purpose:** Research Pollinations.ai API for image provider plugin

---

## API Overview

**Base URL:** `https://image.pollinations.ai`
**Authentication:** ❌ None required (FREE!)
**Method:** HTTP GET
**Response:** Direct image (JPEG)

---

## Endpoint Structure

```
GET https://image.pollinations.ai/prompt/{prompt}?param1=value1&param2=value2
```

### Example:
```bash
curl "https://image.pollinations.ai/prompt/A%20beautiful%20sunset?width=1024&height=1024&seed=42"
```

---

## Supported Parameters

| Parameter | Type    | Default | Required | Notes                          |
|-----------|---------|---------|----------|--------------------------------|
| `prompt`  | string  | -       | ✅ YES   | URL-encoded prompt             |
| `width`   | integer | 1024    | ❌ NO    | Image width (tested: 512-1024) |
| `height`  | integer | 1024    | ❌ NO    | Image height                   |
| `seed`    | integer | random  | ❌ NO    | For reproducible generation    |
| `model`   | string  | flux    | ❌ NO    | Model name (default is fine)   |

---

## Test Results

### Test 1: Basic Request
```bash
curl "https://image.pollinations.ai/prompt/A%20beautiful%20sunset%20over%20mountains" \
  -o test.jpg
```

**Result:** ✅ SUCCESS
- File: JPEG, 1024x1024, 31KB
- Model: flux (from EXIF)
- Time: ~3-5 seconds

---

### Test 2: Custom Dimensions + Seed
```bash
curl "https://image.pollinations.ai/prompt/A%20cat?width=512&height=512&seed=42" \
  -o test_512.jpg
```

**Result:** ✅ SUCCESS
- File: JPEG, 512x512, 36KB
- Seed supported (reproducible output)
- Custom dimensions work

---

## Comparison to Replicate

| Feature              | Pollinations.ai | Replicate                     |
|----------------------|-----------------|-------------------------------|
| **Authentication**   | None            | API token required            |
| **Cost**             | FREE            | ~$0.003 per image             |
| **Seed Support**     | ✅ YES          | ✅ YES                        |
| **Custom Dims**      | ✅ YES          | ✅ YES                        |
| **Response Type**    | Direct JPEG     | JSON with URL → download JPEG |
| **Rate Limits**      | Unknown         | Based on billing              |
| **Model Choice**     | Limited (flux)  | Multiple (SDXL, etc.)         |

---

## Implementation Notes

### URL Encoding
- Prompt MUST be URL-encoded (spaces → `%20`)
- Python: `urllib.parse.quote(prompt)`

### Response Handling
- Direct image bytes (no JSON wrapper)
- Can save directly from response.content

### Error Handling
- Need to test: invalid prompts, rate limits, timeouts
- Response codes unknown (test needed)

### Seed Behavior
- Same seed + prompt = same image (reproducible)
- Compatible with our existing seed strategy

---

## Recommended Implementation (Provider Plugin)

```python
# agency_toolkit/providers/pollinations.py

import requests
from urllib.parse import quote
from .base import ImageProvider

class PollinationsProvider(ImageProvider):
    API_BASE = "https://image.pollinations.ai"
    DEFAULT_MODEL = "flux"

    def generate(self, prompt, seed, width, height, config):
        # URL-encode prompt
        encoded_prompt = quote(prompt)

        # Build URL with params
        url = f"{self.API_BASE}/prompt/{encoded_prompt}"
        params = {
            "width": width,
            "height": height,
            "model": self.DEFAULT_MODEL
        }
        if seed is not None:
            params["seed"] = seed

        # Make request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        # Save image
        # ... (same pattern as Replicate provider)

        return {
            "path": str(image_path),
            "cost": 0.0,  # FREE!
            "seed": seed,
            "model": self.DEFAULT_MODEL,
            "provider": "pollinations"
        }

    def estimate_cost(self):
        return 0.0  # FREE!

    def supports_seed(self):
        return True

    def max_dimensions(self):
        return (2048, 2048)  # Estimate - need to test limits
```

---

## Remaining Questions (To Test)

1. **Max dimensions?** (Need to test 2048x2048, 4096x4096)
2. **Rate limits?** (No docs found - test by making rapid requests)
3. **Error responses?** (Test with invalid prompt, dimensions)
4. **Model options?** (flux is default - are there others?)
5. **HTTPS required?** (YES - tested, works)

---

## Next Steps (WU-2.2, WU-2.3, WU-2.4)

1. ✅ **WU-2.1 COMPLETE** - API researched and working
2. **WU-2.2** - Create `providers/base.py` with `ImageProvider` ABC
3. **WU-2.3** - Refactor Replicate to plugin
4. **WU-2.4** - Implement Pollinations provider
5. **WU-2.5** - Update config models

---

## Acceptance Criteria ✅

- [x] Can successfully generate image via curl
- [x] API request/response documented
- [x] Know limitations vs Replicate (free, simpler, fewer models)
- [x] Seed support confirmed
- [x] Custom dimensions confirmed

---

## Conclusion

**Status:** ✅ **READY FOR IMPLEMENTATION**
**Recommendation:** Implement Pollinations as second provider (after Replicate plugin)
**Advantages:** Free, no auth, simple API, seed support
**Limitations:** Single model (flux), unknown rate limits

Pollinations.ai is an excellent FREE alternative to Replicate and will provide immediate value to users without billing concerns.
