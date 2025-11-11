---
id: vibe-shape-up
type: process
category: processes
tags: [methodology, workflow, shape-up, vibe-coding, sdlc]
related:
  - shape-phase
  - vibe-phase
  - audit-phase
  - the-antidote
version: 1.0.0
---

# Vibe-Shape-Up Process

## Overview

**Vibe-Shape-Up** is a development methodology that combines:
- **Shape Up** (Basecamp) - Fixed time, variable scope
- **Vibe Coding** - AI-assisted rapid development
- **The Antidote** - Structured quality assurance

## The Three Phases

```
┌──────────────┐
│ 1. SHAPE     │  Architect defines boundaries
└──────┬───────┘
       ↓
┌──────────────┐
│ 2. VIBE      │  Developer implements with AI
└──────┬───────┘
       ↓
┌──────────────┐
│ 3. AUDIT     │  Auditor verifies quality
└──────────────┘
```

## Philosophy

### Problem with Pure Vibe Coding
```
❌ Developer + AI → Code (no structure)
   ↓
   Chaos, God Objects, Technical Debt
```

### Problem with Traditional Development
```
❌ Detailed Specs → Slow Implementation
   ↓
   Loss of speed advantage
```

### Vibe-Shape-Up Solution
```
✅ Shape (Boundaries) → Vibe (AI Speed) → Audit (Quality)
   ↓
   Fast + High Quality
```

---

## Phase 1: SHAPE

See: [[shape-phase]]

### Goal
Define **boundaries and risks** WITHOUT implementation details.

### Responsible
**Architect / Tech Lead**

### Duration
**1-2 days** (not weeks)

### Outputs

#### 1. Appetite
**Fixed time budget**

Example: "6 days, not 6 weeks"

#### 2. Pitch
Structured proposal containing:

- **Problem:** What are we solving?
- **Appetite:** How much time?
- **Solution:** High-level approach (not code)
- **Rabbit Holes:** Known risks to avoid
- **No-Gos:** Out of scope

See: [[pitch-template]] in [[10-templates/]]

#### 3. Architecture Diagram
Visual representation of:
- Key components
- Data flow
- External dependencies

#### 4. Boundaries
Clear scope:
- ✅ In scope
- ❌ Out of scope

### Example: Authentication Feature

```markdown
## Pitch: User Authentication

### Problem
Users can't log in. No security.

### Appetite
6 days

### Solution (High-Level)
- JWT-based authentication
- Email/password login
- Session management
- Password reset via email

### Architecture
```
┌─────────┐     ┌──────────┐     ┌─────────┐
│ Frontend│────→│ Auth API │────→│ Database│
└─────────┘     └──────────┘     └─────────┘
                     ↓
                 ┌────────┐
                 │ Email  │
                 │ Service│
                 └────────┘
```

### Rabbit Holes (Avoid)
- ❌ Don't build custom crypto (use bcrypt)
- ❌ Don't implement OAuth (email/password only)
- ❌ Don't build admin panel (out of scope)

### No-Gos
- No social login (future feature)
- No 2FA (future feature)
- No password strength meter (nice-to-have)
```

---

## Phase 2: VIBE

See: [[vibe-phase]]

### Goal
Implement the solution **using AI** within shaped boundaries.

### Responsible
**Developer**

### Duration
Matches **Appetite** from Shape phase

### Process

#### 1. Read the Pitch
Understand boundaries and risks.

#### 2. Use Context-Rich Prompts
From [[prompt-catalog-system]]:

```
You are implementing [Feature] within these constraints:
- Appetite: [X days]
- Architecture: [diagram]
- Must avoid: [Rabbit Holes]
- Out of scope: [No-Gos]

Generate code following:
- [[common-language]] style guide
- [[srp-single-responsibility]] principle
- Include tests for edge cases
```

#### 3. Implement Iteratively
- Generate small chunks ([[small-cls-rule]])
- Review each chunk with [[clear-framework]]
- Commit frequently

#### 4. Stay Within Boundaries
**If scope creeps:**
- Stop
- Discuss with architect
- Either: Cut scope OR extend appetite

### Discovery During Vibe Phase
Team **discovers tasks** during implementation (Shape Up principle).

**Not prescribed:** "Write function X, then Y, then Z"
**Discovered:** "We need X to make Y work, so implement X first"

---

## Phase 3: AUDIT

See: [[audit-phase]]

### Goal
Verify **quality** and **compliance** with standards.

### Responsible
**Auditor / Code Reviewer**

### Duration
**1-2 days**

### Process

#### 1. Apply [[clear-framework]]
Review all AI-generated code:
- Context
- Layered
- Explicit
- Alternative
- Refactoring

#### 2. Fill [[audit-grid-template]]
Measure:
- SRP Violation?
- God Object Indicator?
- Cognitive Load
- Readability
- Testability

#### 3. Run [[thematic-analysis-method]]
Identify patterns:
- Code smells
- Anti-patterns
- Architectural issues

#### 4. Generate Report
See: [[audit-grid-template]]

**If PASS:**
- Merge and ship ✅

**If FAIL:**
- Create refactoring tasks
- Send back to Vibe Phase
- Re-audit after fixes

---

## Example: Full Cycle

### Week 1: Authentication Feature

**Monday-Tuesday: SHAPE**
- Architect creates pitch
- Defines boundaries
- Identifies rabbit holes
- **Output:** Architecture diagram + pitch document

**Wednesday-Friday: VIBE**
- Developer implements with AI
- Uses context-rich prompts
- Reviews with CLEAR
- Commits in small CLs
- **Output:** Working feature

**Monday (Week 2): AUDIT**
- Auditor reviews code
- Applies CLEAR framework
- Fills audit grid
- **Finding:** 1 God Object detected (auth.py)

**Tuesday (Week 2): REFACTOR**
- Developer extracts AuthService
- Re-applies SRP
- Re-audit: PASS ✅

**Result:** Ship on Tuesday

---

## Benefits

| Aspect | Traditional | Vibe Coding | Vibe-Shape-Up |
|--------|-------------|-------------|---------------|
| **Speed** | Slow | Very Fast | Fast |
| **Quality** | High | Low | High |
| **Architecture** | Planned | Emergent (chaos) | Shaped |
| **Technical Debt** | Low | High | Low |
| **Scalability** | Good | Poor | Good |

## Integration with [[the-antidote]]

Vibe-Shape-Up operationalizes The Antidote:

1. **Shape Phase** → Systems thinking (human)
2. **Vibe Phase** → AI acceleration (supervised)
3. **Audit Phase** → Quality assurance (human)

## Common Pitfalls

### ❌ Pitfall 1: Over-Shaping
**Problem:** Shape phase takes 2 weeks (too detailed)
**Solution:** Shape is NOT a detailed spec. High-level only.

### ❌ Pitfall 2: Under-Shaping
**Problem:** "Just build authentication" (no boundaries)
**Solution:** Always define Rabbit Holes and No-Gos.

### ❌ Pitfall 3: Skipping Audit
**Problem:** Ship after Vibe phase (no review)
**Solution:** Audit is NON-NEGOTIABLE.

### ❌ Pitfall 4: Scope Creep
**Problem:** Appetite was 6 days, took 12 days
**Solution:** Cut scope to fit appetite. Ship smaller version.

---

## Metrics

### Success Indicators
- ✅ Features ship within appetite
- ✅ <10% of code needs refactoring in audit
- ✅ No critical issues found in production
- ✅ Code passes [[audit-grid-template]] with good scores

### Failure Indicators
- ❌ Constant scope creep
- ❌ >30% of code needs refactoring
- ❌ Production bugs related to AI-generated code
- ❌ God Objects proliferate

---

## References

- Basecamp: "Shape Up" (Ryan Singer, 2019)
- [[the-antidote]]
- [[clear-framework]]

**Last Updated:** 2025-11-10
**Maintainer:** Vibe Coding OS Project
