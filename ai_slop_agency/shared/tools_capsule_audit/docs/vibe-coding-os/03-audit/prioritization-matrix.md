---
id: prioritization-matrix
type: framework
category: audit
tags: [prioritization, business-value, refactoring]
related:
  - audit-grid-template
  - audit-phase
version: 1.0.0
---

# Prioritization Matrix

## Purpose

Determine **which code to refactor first** based on business impact.

## Three Factors

### 1. Business Criticality
**Question:** How important is this code to business operations?

**Scoring:**
- **CRITICAL:** Revenue-generating, customer-facing
- **HIGH:** Core functionality
- **MEDIUM:** Supporting features
- **LOW:** Internal tools, nice-to-haves

### 2. Change Frequency (Code Churn)
**Question:** How often does this code change?

**Measure:** `git log --numstat <file>`

**Scoring:**
- **HIGH:** Changed >10 times/month
- **MEDIUM:** Changed 3-10 times/month
- **LOW:** Changed <3 times/month

### 3. Risk and Inefficiency
**Question:** What's the cost of NOT refactoring?

**From:** [[audit-grid-template]]

**Consider:**
- God Object Indicator
- Cognitive Load
- AI Slop Indicator
- Technical Debt

## Priority Formula

```
Priority = (Criticality × Churn × Risk) / 100

HIGH:     >50
MEDIUM:   20-50
LOW:      <20
```

## Example

### File: `auth.py`

| Factor | Score | Weight |
|--------|-------|--------|
| Criticality | CRITICAL | 10 |
| Churn | HIGH | 10 |
| Risk | God Object (HIGH) | 8 |

**Priority:** (10 × 10 × 8) / 100 = 80 → **CRITICAL**

**Action:** Refactor immediately

### File: `utils.py`

| Factor | Score | Weight |
|--------|-------|--------|
| Criticality | LOW | 3 |
| Churn | LOW | 2 |
| Risk | Medium | 5 |

**Priority:** (3 × 2 × 5) / 100 = 3 → **LOW**

**Action:** [[boy-scout-rule]] improvements only

## Integration

Use in [[audit-grid-template]] "Priority" column

---

**Last Updated:** 2025-11-10
