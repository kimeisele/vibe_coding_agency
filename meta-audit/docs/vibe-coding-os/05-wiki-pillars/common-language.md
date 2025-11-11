---
id: common-language
type: wiki-pillar
category: wiki-pillars
tags: [style-guide, conventions, standards]
related:
  - clean-code
  - code-as-communication
  - the-antidote
version: 1.0.0
---

# Common Language (Style Guide)

## Purpose

Codify [[the-antidote|philosophy]] into hard, auditable rules.

## Guiding Principles

1. **Optimize for the Reader** - Code is read >10x more than written
2. **Be Consistent** - Same patterns everywhere
3. **Avoid Error-Prone Constructs** - Use safe patterns

## Style Guidelines

### Names

**DO:**
- Use intention-revealing names
- Use pronounceable names
- Use searchable names
- Use domain language

**AVOID:**
- Disinformation (misleading names)
- Hungarian notation (`strName`, `iCount`)
- Single-letter variables (except loop indices)
- Abbreviations

### Functions

**DO:**
- Do one thing
- Keep functions short (<20 lines)
- Use descriptive names (verbs)
- Limit parameters (≤3)

**AVOID:**
- Side effects
- Output parameters
- Flag arguments (`bool` parameters)

### Comments

**DO:**
- Explain WHY, not WHAT
- Document intent
- Clarify complex algorithms
- Warn of consequences

**DO NOT:**
- Comment out code (delete it)
- Write obvious comments
- Use comments to mark sections (use functions)

## Structure

Use prescriptive terms:
- **Do:** Required
- **Consider:** Recommended
- **Avoid:** Discouraged
- **Do Not:** Forbidden

---

**Last Updated:** 2025-11-10
