# Agency Toolkit Documentation

## Single Source of Truth (SSOT) Principle

This project follows the **SSOT principle**: One authoritative source for each type of documentation.

### Why SSOT?
- Prevents documentation drift (docs getting out of sync with code)
- Enables "Spec-Driven Development" (specs first, code follows)
- Reduces "Wildwuchs" (uncontrolled growth) of conflicting docs
- Makes it easy to find THE correct information

---

## SSOT Documents (Authoritative)

### **BLUEPRINT.yaml**
> Architecture, design decisions, high-level overview

**Use this for:**
- Understanding the overall architecture (core/, providers/, commands/)
- What epic/phase we're in
- Major design decisions and philosophy
- Backward compatibility guarantees

**Audience:** Architects, maintainers, users wanting deep understanding

---

### **IMPLEMENTATION.yaml**
> Module specs, function signatures, testing strategy, detailed implementation

**Use this for:**
- Module-by-module implementation details
- Function signatures and parameters
- Testing strategy and test location
- Error handling patterns
- Configuration options

**Audience:** Developers implementing features, code reviewers

---

### **ROADMAP.md**
> Epic/WU breakdown, timeline, success criteria

**Use this for:**
- Project timeline and progress
- What work is planned (Epics 1-7)
- Success criteria for each epic
- Quick reference test commands
- Work unit (WU) breakdown

**Audience:** Project managers, stakeholders, developers tracking progress

---

### **TRANSITION.md**
> Version changes, what changed, what's coming

**Use this for:**
- What changed in this version (v0.1 → v0.2, etc.)
- Migration guide for upgrading
- Known gaps and limitations
- Next steps (upcoming epics)
- Breaking vs. backward-compatible changes

**Audience:** Users upgrading, developers onboarding, maintainers

---

### **EPIC_7_SPECIFICATION.md**
> Detailed Phase 1 specifications for Epic 7 work units

**Use this for:**
- Detailed spec for WU-7.0 through WU-7.7
- All requirements, function signatures, testing
- Ready-to-implement phase 1 docs for Phase 2 (coding)
- Design patterns and approaches

**Audience:** Developers implementing Epic 7

---

## Non-SSOT Documents (Archive)

Historical documentation is in `docs/archive/` for reference:
- FINAL_HANDOVER.md (previous session)
- PROGRESS_ASSESSMENT.md (previous snapshot)
- HANDOVER_SESSION_2.md (previous handover)

**Important:** These are historical only. Refer to SSOT documents for current information.

---

## Spec-Driven Development Workflow

This project follows a **3-phase approach** to prevent documentation drift:

### Phase 1: Specification
- Update SSOT documents with detailed spec
- Define requirements, function signatures, test cases
- Get spec approved
- Document decision rationale

### Phase 2: Implementation
- Write code following the spec exactly
- Don't deviate from Phase 1 spec
- Reference spec in commit messages

### Phase 3: Verification
- Run tests against spec requirements
- Verify all success criteria met
- Update SSOT docs if unexpected changes needed
- Close work unit

---

## How to Use This Documentation

**Q: I want to understand the architecture**
→ Read `BLUEPRINT.yaml`

**Q: I'm implementing a feature, where do I start?**
→ Read `IMPLEMENTATION.yaml` for your module

**Q: What's planned for the project?**
→ Read `ROADMAP.md` for epics/timeline

**Q: What changed in this version?**
→ Read `TRANSITION.md` for changelog

**Q: I need detailed spec for implementing a WU**
→ Read `EPIC_7_SPECIFICATION.md` for that WU

**Q: I'm upgrading, what do I need to know?**
→ Read `TRANSITION.md` migration section

---

## Philosophy: Why Centralized Docs?

Instead of docs scattered across:
- README.md (API reference)
- DEVELOPER.md (dev setup)
- docs/architecture.md (architecture)
- docs/features.md (features)
- docs/roadmap.txt (roadmap)
- wiki/ (off-repo docs)

→ We maintain **4 focused SSOT documents** that answer specific questions.

**Benefits:**
✅ Single place to update (less drift)
✅ Clear responsibility (which doc covers what)
✅ Easier to keep in sync with code
✅ Spec-driven development possible
✅ New developers onboard faster

---

## Example: Making a Change

Want to add a new feature? Follow the SSOT workflow:

1. **Phase 1 (Spec)**: Update `IMPLEMENTATION.yaml` with:
   - Function signature
   - Parameters and return type
   - Error cases
   - Test strategy

2. **Phase 2 (Code)**: Implement following the spec exactly
   - Reference IMPLEMENTATION.yaml in commits
   - Don't deviate from Phase 1

3. **Phase 3 (Verify)**: Run tests and verify against spec
   - All tests pass
   - All requirements met
   - No unexpected changes needed

Result: Code always matches documentation ✅

---

## Current Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| BLUEPRINT.yaml | ✅ Current | Epic 7 Phase 1 |
| IMPLEMENTATION.yaml | ✅ Current | Epic 7 Phase 1 |
| ROADMAP.md | ✅ Current | Epic 7 detailed |
| TRANSITION.md | ✅ Current | v0.2.0 |
| EPIC_7_SPECIFICATION.md | ✅ Current | Ready for Phase 2 |

---

## Questions?

Refer to the appropriate SSOT document above. If you can't find the answer there, check the archive or open an issue.

Remember: **SSOT documents are the source of truth**. Everything else is derived from them.
