---
id: boy-scout-workflow
type: workflow
category: workflows
tags: [boy-scout-rule, continuous-improvement, workflow]
related:
  - boy-scout-rule
  - os-loop
version: 1.0.0
---

# Boy Scout Workflow

## Process

**Required workflow, not optional.**

### Every Commit Must:

1. ✅ **Fix/implement** the main task
2. ✅ **PLUS** make one small improvement (Boy Scout)
3. ✅ **Document** the Boy Scout improvement in commit message

## Example Commit Message

```
feat: Add user authentication endpoint

Implemented JWT-based authentication with:
- Email/password login
- Token generation
- Session validation

Boy Scout: Extracted password hashing to separate utility
(was duplicated in 3 places)
```

## Measuring Success

Track "Boy Scout improvements per week":
- Goal: Every commit has one
- Reality check: Weekly retrospective

## Integration

Part of [[os-loop]] - continuous improvement cycle

---

**Last Updated:** 2025-11-10
