---
id: docs-template
type: template
category: templates
tags: [documentation, docs, ai-interaction-log]
related:
  - ai-governance
  - clear-framework
version: 1.0.0
---

# DOCS Template for AI-Generated Code

## Purpose

Capture design decisions and AI interaction history.

**CRITICAL:** Store prompt history - this is your audit trail.

---

## Template

### D - Design Decisions

**Why this pattern/approach?**

**Alternatives rejected:**
1.
2.

**Trade-offs:**
- Pro:
- Con:

---

### O - Operational Context

**Dependencies:**
- External services:
- Libraries:
- Configuration required:

**Environment:**
- Production requirements:
- Development setup:

---

### C - Code Understanding

**Complex logic explanation:**

[Explain any non-obvious code sections]

**Edge cases handled:**
1.
2.

**Known limitations:**

---

### S - Support / AI Interaction Log

**🚨 CRITICAL SECTION**

**Original Prompt:**
```
[Paste exact prompt given to AI]
```

**Iterations:**
1. First attempt: [What worked/didn't work]
2. Refined prompt: [Changes made]
3. Final version: [What was shipped]

**AI Model Used:** [e.g., Claude Sonnet 4.5]

**Prompt Engineering Notes:**
- What context was crucial?
- What instructions were ignored?
- What needed clarification?

---

**Last Updated:** [YYYY-MM-DD]
