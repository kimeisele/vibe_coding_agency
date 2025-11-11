# Registry System: Curated Templates & Prompts

## Overview

A lightweight, extensible registry system for Agency Toolkit to manage reusable prompts, templates, and best practices. **Not a full wiki** - focused, minimal, and practical.

## Architecture

### Directory Structure

```
registry/
├── prompts/              # Mistral prompt templates
│   ├── email-subjects.json
│   ├── instagram-captions.json
│   ├── code-review.json
│   ├── content-strategy.json
│   └── ...
├── templates/            # Design & briefing templates
│   ├── social/
│   │   ├── tiktok-vertical.json
│   │   ├── linkedin-professional.json
│   │   └── instagram-stories.json
│   └── briefing/
│       ├── saas-launch.json
│       ├── ecommerce-site.json
│       └── nonprofit-campaign.json
├── checklists/           # Project checklists (markdown)
│   ├── pre-launch-qa.md
│   ├── design-review.md
│   ├── content-audit.md
│   └── ...
└── best-practices/       # Guidelines (1-2 page markdown files)
    ├── social-media-strategy.md
    ├── design-principles.md
    ├── project-kickoff-template.md
    └── accessibility-guidelines.md
```

## Registry Entry Types

### 1. Prompts (`prompts/*.json`)

**Purpose:** Curated Mistral AI prompts for specific use cases

**Format:**
```json
{
  "metadata": {
    "id": "instagram-captions",
    "name": "Instagram Caption Generator",
    "description": "Generate engaging Instagram captions with emojis and hashtags",
    "version": "1.0",
    "tags": ["social", "instagram", "copywriting"],
    "author": "Agency Toolkit"
  },
  "prompts": [
    {
      "name": "engagement-focused",
      "system_prompt": "You are an Instagram copywriter specializing in engagement...",
      "temperature": 0.8,
      "max_tokens": 300
    },
    {
      "name": "hashtag-optimized",
      "system_prompt": "Generate Instagram captions with 20-30 relevant hashtags...",
      "temperature": 0.7,
      "max_tokens": 500
    }
  ]
}
```

### 2. Templates (`templates/**/*.json`)

**Purpose:** Pre-configured design and briefing templates

**Format:**
```json
{
  "metadata": {
    "id": "tiktok-vertical",
    "type": "social",
    "name": "TikTok Vertical (1080x1920)",
    "description": "Optimized for TikTok's vertical format",
    "version": "1.0"
  },
  "template": {
    "font_face": "Roboto-Bold",
    "font_size": 60,
    "format": "story",
    "text_position_xy": [540, 1000],
    "background_type": "gradient",
    "gradient_colors": ["#FF0050", "#FF1744"]
  }
}
```

### 3. Checklists (`checklists/*.md`)

**Purpose:** Project workflow checklists

**Format:** Simple markdown with checkboxes

```markdown
# Pre-Launch QA Checklist

## Design & Layout
- [ ] Test on mobile devices
- [ ] Verify color contrast (WCAG AA)
- [ ] Check responsive breakpoints
- [ ] Review typography hierarchy

## Content
- [ ] Proofread all copy
- [ ] Verify links work
- [ ] Check image alt text
- [ ] Validate form fields
```

### 4. Best Practices (`best-practices/*.md`)

**Purpose:** Guidelines and recommendations (1-2 pages each)

**Format:** Markdown with sections

```markdown
# Social Media Strategy Guide

## Platform-Specific Best Practices

### Instagram
- Post frequency: 4-7 times/week
- Best posting times: 9-11 AM, 7-9 PM
- Optimal caption length: 125-150 characters
- Use 20-30 hashtags for discovery

### TikTok
- Video length: 15-60 seconds
- Trending sounds increase reach by 2-5x
- Post frequency: Daily recommended
- Hashtag strategy: Mix trending + niche
```

## CLI Commands (Planned)

### Query Registry
```bash
toolkit registry list                    # List all entries
toolkit registry search "instagram"      # Search by keyword
toolkit registry show prompt:instagram-captions
toolkit registry show template:tiktok-vertical
toolkit registry show checklist:pre-launch-qa
```

### Use Registry Items
```bash
# Copy template to local override
toolkit registry copy template:tiktok-vertical ~/my-templates/

# Use prompt from registry
toolkit mistral --prompt-from-registry "instagram-captions:engagement-focused"

# Display checklist in terminal
toolkit registry show checklist:pre-launch-qa --print
```

### Extend Registry
```bash
# Add custom prompt to local registry
toolkit registry add prompt my-custom-prompt.json --local

# Update existing entry
toolkit registry update prompt:instagram-captions new-version.json
```

## Implementation Phases

### Phase 1: Foundation (MVP)
- [x] Define registry structure
- [ ] Create 10-15 core prompts
- [ ] Create 5-8 social templates
- [ ] Create 3-5 briefing templates
- [ ] Implement `registry list` & `registry search`
- [ ] Add `--from-registry` flag to `mistral` command

### Phase 2: Enhancement
- [ ] Add checklist management
- [ ] Add best practices library
- [ ] Implement local overrides (user can extend)
- [ ] Add `registry copy` functionality

### Phase 3: Distribution
- [ ] Package registry as separate JSON files
- [ ] Allow remote registry sync (GitHub raw)
- [ ] Version management for registry entries
- [ ] Community contributions workflow

## Local Registry Override

Users can extend the registry locally:

```
~/.config/agency-toolkit/registry/
├── prompts/my-custom-prompts.json
├── templates/social/my-templates.json
└── checklists/my-workflows.md
```

Local entries override built-in ones with same ID.

## Search Implementation

Simple, no heavy indexing needed:

```python
# Grep-based search
grep -r "keyword" registry/ | jq '.metadata.tags'

# Python implementation
import json
from pathlib import Path

def search(keyword: str):
    results = []
    for json_file in Path("registry").rglob("*.json"):
        data = json.loads(json_file.read_text())
        if keyword.lower() in str(data).lower():
            results.append(data['metadata'])
    return results
```

## Benefits

✅ **Lightweight:** Just JSON files + markdown
✅ **Version Control:** Easy to track in Git
✅ **Extensible:** Users can add custom entries
✅ **Discoverable:** Search across all entries
✅ **Practical:** Directly integrated into commands
✅ **Low Maintenance:** No database, no server
✅ **Shareable:** Registry can be version controlled

## What's NOT Included

❌ Rich HTML rendering
❌ Version control/rollback
❌ User comments/discussions
❌ Full-text search engine
❌ Access control/permissions
❌ Collaboration features

## Success Criteria

1. Users can discover relevant templates/prompts within 30 seconds
2. Registry adds < 5MB to toolkit size
3. Search performance: < 100ms
4. Local extensions work seamlessly
5. Documentation is self-explanatory

## Future Enhancements

- [ ] Remote registry sync (GitHub raw content)
- [ ] Rating system for community entries
- [ ] Analytics on registry usage
- [ ] AI-powered prompt suggestions
- [ ] Template preview with `--preview` flag
