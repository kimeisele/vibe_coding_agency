---
id: clear-checklist
type: template
category: templates
tags: [checklist, clear-framework, ai-review]
related:
  - clear-framework
  - code-review-practice
version: 1.0.0
---

# CLEAR Checklist Template

## Usage

Copy this template for every AI code review.

---

## CLEAR Review: [Feature Name]

**Reviewer:** [Your Name]
**Date:** [YYYY-MM-DD]
**PR/CL:** [Link]

---

### ✅ C - Context

- [ ] Reviewed original prompt
- [ ] Prompt included necessary business context
- [ ] Requirements were clear and specific
- [ ] Constraints and boundaries specified
- [ ] No vague instructions

**Notes:**

---

### ✅ L - Layered

**Layer 1: Structure**
- [ ] Code is well-organized
- [ ] Follows [[srp-single-responsibility]]
- [ ] No [[god-object-pattern|God Objects]]
- [ ] Clear module boundaries

**Layer 2: Logic**
- [ ] Solves the stated problem
- [ ] Handles edge cases
- [ ] No logical errors
- [ ] Input validation present

**Layer 3: Security**
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Sensitive data protected
- [ ] Authentication/authorization correct

**Layer 4: Performance** (if applicable)
- [ ] No obvious inefficiencies
- [ ] Appropriate data structures
- [ ] No N+1 queries

**Notes:**

---

### ✅ E - Explicit

- [ ] Can explain what every block does
- [ ] Mentally traced execution with example inputs
- [ ] No "magic" or unclear sections
- [ ] Would be comfortable debugging this

**Explanation:** [Write 2-3 sentence explanation of what code does]

---

### ✅ A - Alternative

- [ ] Considered simpler approaches
- [ ] Evaluated different patterns
- [ ] This is the best solution (not just first)
- [ ] Documented why this approach chosen

**Alternatives considered:**
1.
2.

**Why current approach is best:**

---

### ✅ R - Refactoring

- [ ] Follows team [[common-language]] style guide
- [ ] Naming conventions consistent
- [ ] Error handling appropriate
- [ ] Tests included and passing
- [ ] No [[ai-slop-anatomy|AI Slop]] indicators
- [ ] [[boy-scout-rule]] applied

**Refactoring needed:**

---

## Final Verdict

Choose one:

- [ ] ✅ **APPROVED** - Ship it
- [ ] ⚠️ **NEEDS REVISION** - Minor changes required
- [ ] ❌ **REJECTED** - Major issues, needs rework

**Summary:**

---

**Reviewer Signature:** [Name]
**Date:** [YYYY-MM-DD]
