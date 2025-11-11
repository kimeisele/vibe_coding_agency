---
id: vibe-phase
type: process
category: processes
tags: [vibe-coding, implementation, ai-assisted]
related:
  - shape-phase
  - audit-phase
  - clear-framework
  - small-cls-rule
version: 1.0.0
---

# Vibe Phase

## Goal

Implement solution **using AI** within shaped boundaries.

## Duration

Matches **Appetite** from [[shape-phase]]

## Responsible

**Developer**

## Process

### 1. Read the Pitch
Understand:
- Boundaries
- Rabbit Holes to avoid
- No-Gos (out of scope)

### 2. Context-Rich Prompts
Use [[08-ai-governance/prompt-catalog-system]]

Include:
- Architecture from Shape Phase
- Constraints and boundaries
- Style guide ([[common-language]])
- [[srp-single-responsibility]] principle

### 3. Implement Incrementally
- Generate **small chunks** ([[small-cls-rule]])
- Review each with [[clear-framework]]
- Commit frequently

### 4. Stay Within Boundaries
**If scope creeps:**
- Stop
- Discuss with architect
- Cut scope OR extend appetite

## Discovery

Team **discovers tasks** during implementation (not prescribed upfront).

## Integration

Between [[shape-phase]] and [[audit-phase]]

---

**Last Updated:** 2025-11-10
