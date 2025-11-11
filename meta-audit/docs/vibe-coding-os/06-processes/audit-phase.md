---
id: audit-phase
type: process
category: processes
tags: [audit, quality-assurance, review]
related:
  - vibe-phase
  - clear-framework
  - audit-grid-template
  - thematic-analysis-method
version: 1.0.0
---

# Audit Phase

## Goal

Verify **quality** and **compliance** with standards.

## Duration

**1-2 days**

## Responsible

**Auditor / Code Reviewer**

## Process

### 1. Apply [[clear-framework]]
Review all AI-generated code:
- C: Context
- L: Layered
- E: Explicit
- A: Alternative
- R: Refactoring

### 2. Fill [[audit-grid-template]]
Score each module:
- SRP Violation?
- God Object Indicator?
- Cognitive Load
- Readability
- Testability

### 3. Run [[thematic-analysis-method]]
Identify patterns and themes

### 4. Generate Report
Summary of code health

## Outcomes

### ✅ PASS
- Merge and ship

### ⚠️ NEEDS REVISION
- Create refactoring tasks
- Send back to [[vibe-phase]]
- Re-audit after fixes

### ❌ FAIL
- Major issues found
- Architectural rework needed
- Return to [[shape-phase]]

---

**Last Updated:** 2025-11-10
