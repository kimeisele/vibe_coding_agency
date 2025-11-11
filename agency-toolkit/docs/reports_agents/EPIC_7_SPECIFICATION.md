# EPIC 7: Polish & Usability - Specification Document

**Epic Owner**: AI-Driven Development
**Status**: 🟢 PLANNED (Ready to start)
**Total Effort**: ~15-18 hours
**Start Date**: 2025-11-10
**Target Completion**: 2025-11-14
**Philosophy**: Spec-Driven Development (SSOT First, Code Second)

---

## Executive Summary

Epic 7 focuses on **production-grade polish and usability** to make the toolkit suitable for real agency workflows. This epic builds on the stable foundation established in Epics 2.5 & 4.0, adding user-facing features and improvements that increase adoption and value.

### Key Objectives
1. **Reliability**: Fix remaining PDF export issues (Story 7.1)
2. **Quality**: Make output professional-grade with responsive templates (Story 7.2)
3. **Usability**: Interactive wizards for non-technical users (Story 7.3)
4. **Integration**: Chain AI → Image → Social in one command (Story 7.4)
5. **Discovery**: Seed templates registry for advanced users (Story 7.5)
6. **Maintainability**: Clean up documentation (Story 7.6)
7. **Intelligence**: Semantic queries for self-help (Story 7.7)

---

## STORY 7.1: PDF-Export Repair

**Goal**: Fix PDF generation hangs/crashes and ensure reliable briefing PDFs

**Acceptance Criteria**:
- [ ] PDF generation completes in <2 seconds for typical briefing
- [ ] No font loading errors or warnings
- [ ] `test_briefing_integration.py` passes (both md and pdf outputs)
- [ ] Stress test: Generate 10 PDFs sequentially without issues

**Effort**: 1-2 hours
**Priority**: High (blocks complete briefing functionality)

---

## STORY 7.2: Social Template Engine (Responsive Layouts)

**Goal**: Make social post templates responsive for any image size

**Acceptance Criteria**:
- [ ] All templates use relative sizing (font_size_ratio, padding_ratio)
- [ ] Templates render correctly at 256×256, 512×512, 1080×1080, 2048×2048
- [ ] Professional quality comparable to Figma templates

**Effort**: 2-3 hours
**Priority**: Medium

---

## STORY 7.3: Interactive Wizards

**Goal**: Add interactive CLI prompts for non-technical users

**Acceptance Criteria**:
- [ ] `toolkit social` (no args) → Interactive wizard with 8+ questions
- [ ] `toolkit briefing` (no args) → Similar wizard
- [ ] `toolkit image` (no args) → Image generation wizard
- [ ] User-tested with 2-3 people

**Effort**: 2-3 hours
**Priority**: High (increases adoption)

---

## STORY 7.4: Image with Text Orchestration

**Goal**: Chain Mistral → Image Generation → Social Text Overlay in one command

**Acceptance Criteria**:
- [ ] New flag: `--bg-concept "concept"` on social command
- [ ] Workflow: Enhance text → Generate image → Overlay text
- [ ] Works with all 3 social styles
- [ ] Cost displayed transparently
- [ ] Error fallback: solid color if image fails

**Effort**: 2-3 hours
**Priority**: Medium

---

## STORY 7.5: Seed Templates Registry

**Goal**: Allow users to save and reuse seed templates

**Acceptance Criteria**:
- [ ] Create registry/seeds/ with 4 templates (moody, corporate, playful, minimal)
- [ ] New command: `toolkit image "cat" --seed-template moody`
- [ ] List templates: `toolkit info --seed-templates`

**Effort**: 1-2 hours
**Priority**: Low

---

## STORY 7.6: Documentation Cleanup

**Goal**: Consolidate documentation and establish SSOT

**Acceptance Criteria**:
- [ ] Archive non-essential docs to docs/archive/
- [ ] Keep only: BLUEPRINT.yaml, IMPLEMENTATION.yaml, ROADMAP.md, README.md, DEVELOPMENT.md
- [ ] Create docs/README.md explaining SSOT principle
- [ ] No broken links

**Effort**: 30 minutes - 1 hour
**Priority**: Low

---

## STORY 7.7: Semantic Toolkit Query

**Goal**: Add intelligent self-help with `toolkit ask`

**Acceptance Criteria**:
- [ ] New command: `toolkit ask "How do I create a social post with background?"`
- [ ] Reads README.md and DEVELOPMENT.md
- [ ] Returns answer via Mistral
- [ ] Answers include relevant command examples

**Effort**: 1-2 hours
**Priority**: Low

---

## Implementation Order

**Phase 1 (High Priority - Essential)**:
- 7.1 PDF-Export Repair (1-2h)
- 7.3 Interactive Wizards (2-3h)

**Phase 2 (Medium Priority - Quality)**:
- 7.2 Responsive Templates (2-3h)
- 7.4 Image with Text Orchestration (2-3h)

**Phase 3 (Low Priority - Polish)**:
- 7.5 Seed Templates Registry (1-2h)
- 7.6 Documentation Cleanup (30m-1h)
- 7.7 Semantic Toolkit Query (1-2h)

**Total Time**: ~15-18 hours

---

## Timeline & Milestones

| Milestone | Target Date | Stories |
|-----------|-------------|---------|
| Phase 1 Done | 2025-11-11 | 7.1, 7.3 |
| Phase 2 Done | 2025-11-12 | 7.2, 7.4 |
| Phase 3 Done | 2025-11-14 | 7.5, 7.6, 7.7 |
| Epic 7 Complete | 2025-11-14 | All stories |

---

## Definition of Done (Per Story)

Each story is COMPLETE when:
1. Code written (all acceptance criteria)
2. Tests added & passing (>80% coverage)
3. Documentation updated
4. Manual testing complete
5. Changes committed and pushed

---

## Sign-Off

**Epic 7 is COMPLETE when**:
- [ ] All 7 stories marked DONE
- [ ] 726+ tests still passing (no regressions)
- [ ] All acceptance criteria met
- [ ] Documentation updated
- [ ] Code committed and pushed

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Author**: AI-Driven Development
