---
id: os-loop
type: workflow
category: workflows
tags: [feedback-loop, continuous-improvement, learning]
related:
  - boy-scout-workflow
  - vibe-shape-up
  - audit-phase
version: 1.0.0
---

# OS Feedback Loop

## The Loop

```
1. Vibe Coding → Feature implemented
         ↓
2. Governance → CLEAR + DOCS applied
         ↓
3. Audit → Formal audit conducted
         ↓
4. Discovery → New anti-pattern found
         ↓
5. Feedback → Fix code AND update wiki
         ↓
    (Loop back to 1)
```

## Key Insight

> **"Every bug or anti-pattern is a wiki improvement opportunity."**

## Process

### When Anti-Pattern Found:

1. **Fix the code** - Apply refactoring
2. **Update the wiki** - Add new rule/example
3. **Update prompt catalog** - Prevent recurrence
4. **Share with team** - Collective learning

## Example

**Discovery:** Auditor finds new AI Slop pattern: "Verbose error messages"

**Actions:**
1. Fix code: Simplify error messages
2. Add to [[ai-slop-anatomy]]: New manifestation
3. Create prompt: "Use concise error messages"
4. Team standup: Share finding

**Result:** Pattern won't repeat

## Success Metrics

- Wiki grows with real findings
- Same mistakes don't repeat
- Team knowledge compounds

---

**Last Updated:** 2025-11-10
