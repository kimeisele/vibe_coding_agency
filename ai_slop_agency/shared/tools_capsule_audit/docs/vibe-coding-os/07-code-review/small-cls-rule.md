---
id: small-cls-rule
type: practice
category: code-review
severity: critical
tags: [code-review, cls, changelist, google-practices]
related:
  - code-review-practice
  - clear-framework
  - vibe-phase
version: 1.0.0
---

# Small CLs Rule

## Definition

**CL = Changelist** (also called: Commit, Pull Request, Merge Request)

**Rule:** One logical change per CL.

## Importance

🚨 **CRITICAL** - This is the **mechanical antidote** to [[ai-slop-anatomy|AI Slop]].

## What "Small" Means

### Good Size
- **100-200 lines** changed
- **1 feature** or **1 bug fix**
- **Can be reviewed in 10-15 minutes**

### Too Large
- **1000+ lines** changed
- **Multiple features** mixed together
- **Requires >1 hour** to review

### Too Small
- **1 line** (typo fix is OK, but batch typos together)
- **Incomplete change** (breaks build)

## Why It Matters

### Benefits of Small CLs

| Benefit | Explanation |
|---------|-------------|
| **Faster Review** | Reviewer can finish in one sitting |
| **Higher Quality** | Easier to spot bugs |
| **Less Context** | Doesn't require deep understanding |
| **Easier Revert** | If bad, revert is clean |
| **Parallel Work** | Team can review multiple CLs simultaneously |

### Problems with Large CLs

| Problem | Explanation |
|---------|-------------|
| **Review Fatigue** | Reviewer gives up, approves without reading |
| **Hidden Bugs** | Issues buried in noise |
| **Merge Conflicts** | Touches too many files |
| **Difficult Revert** | Reverting breaks other features |
| **Bottleneck** | Blocks other work |

## Examples

### ❌ Bad: Large CL

```
Pull Request: "Add user authentication"

Files changed: 47 files
Lines changed: 3,247 lines

Changes:
- User model
- Database migrations
- Authentication API
- Frontend login form
- Password reset flow
- Email service
- Session management
- Unit tests
- Integration tests
- Documentation
```

**Problem:** This is 7 features in one CL. Impossible to review thoroughly.

### ✅ Good: Small CLs

```
PR 1: "Add User model and database migration"
- 3 files, 120 lines
- Review time: 10 min

PR 2: "Add authentication API endpoints"
- 4 files, 180 lines
- Review time: 15 min

PR 3: "Add frontend login form"
- 2 files, 95 lines
- Review time: 8 min

PR 4: "Add password reset flow"
- 3 files, 130 lines
- Review time: 12 min

... etc
```

**Benefit:** Each PR is reviewable, testable, and revertable.

## How to Split Large Changes

### Technique 1: By Layer

```
1. Data layer (models, migrations)
2. Business logic (services)
3. API layer (endpoints)
4. UI layer (frontend)
```

### Technique 2: By Feature Slice

```
1. Happy path only
2. Error handling
3. Edge cases
4. Optimizations
```

### Technique 3: By Dependency

```
1. Shared utilities first
2. Core feature
3. Dependent features
```

## AI + Small CLs

### The Problem

AI generates **entire features** in one go → Large CL trap

### The Solution

**Prompt AI to generate incrementally:**

```
Generate ONLY the User model and database migration.
Do NOT include:
- API endpoints
- Frontend
- Tests (will do separately)

Just the model. ~100 lines max.
```

Then review with [[clear-framework]] before next chunk.

## Integration with Vibe Coding OS

### In [[vibe-phase]]

1. AI generates code chunk
2. Developer reviews with [[clear-framework]]
3. **Commit immediately** (small CL)
4. Repeat for next chunk

### In [[audit-phase]]

Auditor checks:
- Are CLs small enough?
- Are CLs logical?
- Is each CL reviewable?

## Google's Guidance

From **Google Engineering Practices**:

> **"Small CLs are preferred. A change should contain a single logical change."**

**Google's definition:**
- **Small:** 1 self-contained change
- **Exactly one thing:** Fix 1 bug, add 1 feature, refactor 1 class

## Exceptions

### When Large CLs Are OK

1. **Delete code** - Removing 10,000 lines is fine
2. **Generated code** - Auto-generated migrations
3. **Large refactoring** - With team agreement
4. **Moving files** - Git recognizes as move, not change

**Even then:** Consider splitting if possible.

## Measuring Success

### Team Metrics

| Metric | Good | Bad |
|--------|------|-----|
| **Avg CL Size** | <200 lines | >500 lines |
| **Review Time** | <15 min | >1 hour |
| **Revert Rate** | <5% | >20% |
| **Review Quality** | Issues found | Rubber stamp |

## Common Objections

### "It takes too long to split"

**Rebuttal:** Takes 5 min to split. Saves hours in review + debugging.

### "My feature is inherently large"

**Rebuttal:** Every feature can be split. See techniques above.

### "AI generates everything at once"

**Rebuttal:** Prompt AI differently. Request incremental generation.

---

## References

- Google Engineering Practices: Small CLs
- Kent Beck: "Make the change easy, then make the easy change"

**Last Updated:** 2025-11-10
