---
id: thematic-analysis-method
type: methodology
category: audit
tags: [audit, analysis, qualitative, systematic]
related:
  - audit-grid-template
  - god-object-pattern
  - heuristic-evaluation
version: 1.0.0
---

# Thematic Analysis Method

## Purpose

Systematic identification of code patterns and anti-patterns using qualitative research methodology.

## Process

### Step 1: Familiarization
**Goal:** Understand the codebase

**Actions:**
- Read code files
- Run the application
- Review documentation
- Understand domain

### Step 2: Initial Coding (Deductive)
**Goal:** Apply known patterns from catalog

**Use:** [[04-anti-patterns/]] catalog

**Look for:**
- [[god-object-pattern|God Objects]]
- [[long-method|Long Methods]]
- [[large-class|Large Classes]]
- [[duplicate-code|Duplicate Code]]

**Tool:** [[audit-grid-template]]

### Step 3: Detailed Coding (Inductive)
**Goal:** Discover new patterns

**Actions:**
- Note recurring issues not in catalog
- Identify team-specific anti-patterns
- Document unique code smells

### Step 4: Generate Themes
**Goal:** Group related codes

**Example:**
- Codes: "Long Method", "Nested Ifs", "Complex Logic"
- **Theme:** "High Cognitive Load"

### Step 5: Review Themes
**Goal:** Find [[srp-single-responsibility|SRP]] violations

**Question:** Do themes indicate multiple responsibilities?

## Output

**Qualitative Codes/Themes column** in [[audit-grid-template]]

Example: `"God Object, Tight Coupling, Bloat"`

## Integration

Part of [[audit-phase]] in [[vibe-shape-up]]

---

**Last Updated:** 2025-11-10
