# Epic 14 Backlog: Real-World Fixes & Registry Population

**Generated from Epic 13 Batch Testing Results**
**Date**: 2025-11-07
**Test Results**: 7/8 scenarios executed, **P0 blocker** discovered

---

## P0: Critical Blockers (BLOCKS ALL USAGE)

### P0-1: Populate Registry with Actual Tool Invocations

**Status**: 🚨 **BLOCKS PRODUCTION USE**

**Problem**:
All modules in `registry/seeds/solutions.json` have empty `tasks` arrays. The orchestrator resolves dependencies correctly but executes 0 tasks because there's nothing defined to execute.

**Evidence**:
```
Batch Test Results:
- Test_Handwerk_CD: 0/0 tasks (PARTIAL)
- Test_Handwerk_Website: 0/0 tasks (PARTIAL)
- Test_Handwerk_Social: 0/0 tasks (PARTIAL)
- All 7 valid scenarios: 0 tasks executed
```

**Root Cause**:
```json
{
  "id": "A1_M1",
  "title": "Fundament (Corporate Design)",
  "tasks": [],  // ❌ EMPTY - should contain tool invocations
  "dependencies": []
}
```

**Fix Specification**:
1. Define actual `tasks` for each module in `registry/seeds/solutions.json`
2. Each task must specify:
   - `tool`: Which CLI tool to invoke (`structure`, `briefing`, `social`, `ai`)
   - `params`: Tool-specific parameters
   - `prompt_template`: (for `ai` tool) Dynamic prompt with context variables

**Example Task Definition**:
```json
{
  "id": "A1_M1",
  "title": "Fundament (Corporate Design)",
  "tasks": [
    {
      "tool": "structure",
      "params": {
        "client": "{{project_name}}",
        "project": "Corporate Design",
        "type": "default"
      }
    },
    {
      "tool": "briefing",
      "params": {
        "type": "branding",
        "interactive": false
      }
    },
    {
      "tool": "ai",
      "params": {
        "prompt_template": "Erstelle ein Corporate Design Konzept für {{project_name}}. Berücksichtige: {{pain_points}}. Ziel: {{goals}}.",
        "provider": "{{ai_provider}}",
        "output_file": "briefings/cd_concept.md"
      }
    }
  ]
}
```

**Acceptance Criteria**:
- [ ] All modules (A1_M1, A1_M2, A1_M3, A1_M4, A2_M1...) have defined tasks
- [ ] Re-run batch test shows `X/X tasks completed` (not 0/0)
- [ ] Generated artifacts appear in `output/` directory
- [ ] Minimal viable set: At least A1_M1, A1_M2, A1_M4 fully defined

**Priority**: **P0** - Nothing works without this

---

## P1: Quality Improvements (Reduces Trust)

### P1-1: Validate AI-Generated Content for "AI Slop"

**Status**: ⏳ **BLOCKED by P0-1** (cannot test until tasks execute)

**Problem**:
Need to verify that AI-generated content (from `ai` tool invocations) does not contain:
- Generic phrases ("As a large language model...")
- Placeholder text ("[INSERT_CLIENT_NAME]")
- Hallucinations (fake statistics, made-up tools)

**Specification**:
1. After P0-1 is complete, re-run batch test
2. Manually review all AI-generated content in `output/*/briefings/`
3. Document every instance of AI Slop
4. If found, refine `prompt_template` in `solutions.json` (NOT "try a different model")

**Acceptance Criteria**:
- [ ] All AI-generated text is professional and specific
- [ ] No generic AI phrases
- [ ] No hallucinations
- [ ] Tone is appropriate for archetype

---

### P1-2: Cross-Contamination Testing

**Status**: ⏳ **BLOCKED by P0-1**

**Problem**:
Need to verify that batch execution doesn't leak context between projects.

**Test**:
- Run batch with 2 projects: "Test_A" and "Test_B"
- Verify "Test_A" artifacts don't mention "Test_B"
- Verify each project has isolated output directory

**Acceptance Criteria**:
- [ ] No cross-project content leakage
- [ ] Each project's artifacts are isolated
- [ ] Context variables are properly scoped per-project

---

### P1-3: Improve Module Descriptions for UX

**Status**: 🟡 **Low Priority**

**Problem**:
Current module descriptions in registry are good but could be more actionable.

**Example**:
```json
// Current (OK)
"description": "Erstellung eines professionellen, einheitlichen visuellen Erscheinungsbilds"

// Better
"description": "Corporate Design: Logo, Farbpalette, Schriftarten, Geschäftsausstattung (Visitenkarten, Briefpapier)"
```

**Specification**:
- Add concrete deliverables to descriptions
- Keep descriptions under 120 characters
- Focus on business value, not technical process

**Priority**: **P1** - Nice to have, not blocking

---

## P2: Nice-to-Have (Future Enhancements)

### P2-1: Add Progress Indicators for Long-Running Tasks

**Problem**:
Batch execution with many tasks can appear "stuck" to users.

**Solution**:
- Add progress bar for each module
- Show estimated time remaining
- Display current task being executed

**Priority**: **P2** - UX improvement, not critical

---

### P2-2: JSON Output for Batch Summary

**Problem**:
Current batch summary is human-readable but not machine-parsable.

**Solution**:
- Add `--json` flag support to `os init --from-csv`
- Output machine-readable summary
- Enable CI/CD integration

**Priority**: **P2** - Automation feature, not urgent

---

## NOT DOING (AI Slop / Buzzword Sparks)

### ❌ "Integrate GPT-4o for better results"
**Reason**: Current providers (Mistral, Google, Ollama) are sufficient. If AI content is bad, we fix the **prompts**, not swap models.

### ❌ "Add blockchain tracking to registry"
**Reason**: Not requested, adds complexity, no business value.

### ❌ "Implement GraphQL API for registry"
**Reason**: Current JSON files work fine. No need for over-engineering.

### ❌ "Add machine learning to predict best archetype"
**Reason**: Current interactive selection works. Don't solve problems that don't exist.

---

## Summary

**Total Items**: 7
**P0 (Blockers)**: 1
**P1 (Quality)**: 3
**P2 (Future)**: 2
**Rejected (AI Slop)**: 4

**Next Action**: **Start Epic 14 with P0-1** - Populate registry with actual tool invocations.

---

## Lessons Learned from Epic 13

### What Worked Well ✅
1. **Batch testing revealed the critical P0 blocker** immediately
2. **Robust error handling** caught validation issues gracefully
3. **Dependency resolution** works correctly
4. **CSV format** makes it easy to define test scenarios

### What We Discovered 🔍
1. **Registry is incomplete** - modules exist but have no tasks
2. **This would NOT have been found** with single HIL testing
3. **Systematic testing > Manual testing** for finding gaps

### What to Do Differently 🔄
1. **Always populate registry with real tasks** from the start
2. **Run batch test earlier** in development cycle
3. **Don't assume structure means functionality**
