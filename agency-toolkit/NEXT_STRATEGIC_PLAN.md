# Next Strategic Plan - Roadmap Alignment & Package Integration

**Date:** 2025-11-08
**Status:** Planning Phase

---

## Current State

✅ **Just Completed:**
- Epic 1.3: Error handling framework (COMPLETE)
- Epic 1.3.3: Input validation framework (COMPLETE)
- Infrastructure fixes: Pre-commit, questionary (COMPLETE)
- Test suite: 459/459 passing

✅ **Available Resources:**
- `docs/prompt_registry_/` - Production-ready prompt management system
- `docs/phoenix_config_/` - Production-ready config management system

---

## Decision: Roadmap vs Package Integration

### Option A: Follow Roadmap Strictly
**Path:** Epic 1.4 → Epic 2.1 → Epic 2.2

**Timeline:**
1. **Epic 1.4** (8 hours) - Write tests for undertested modules
   - `core/briefing/interactive.py` (8% → 70%)
   - `core/social/batch.py` (13% → 70%)
   - `core/os_interactive.py` (17% → 70%)

2. **Epic 2.1** (7 hours) - Centralize AI prompts
   - Build custom prompt system from scratch
   - Extract MISTRAL_PROFILES to text files
   - Create loader.py with variable substitution

3. **Epic 2.2** (4 hours) - Improve configuration
   - Move config to TOML
   - Build custom validation
   - Add schema validation

**Total:** ~19 hours
**Pros:** Follows documented roadmap, learning experience
**Cons:** Rebuilds existing functionality (prompts, config)

### Option B: Leverage Existing Packages (RECOMMENDED)
**Path:** Epic 1.4 → Integrate prompt_registry → Integrate phoenix_config

**Timeline:**
1. **Epic 1.4** (8 hours) - Write tests for undertested modules
   - Same as above

2. **Integrate Prompt Registry** (~4 hours)
   - Evaluate `docs/prompt_registry_/` thoroughly
   - Adapt it to agency_toolkit needs
   - Migrate MISTRAL_PROFILES + hardcoded prompts
   - Add tests (10-15 tests)

3. **Integrate Phoenix Config** (~3 hours)
   - Evaluate `docs/phoenix_config_/` thoroughly
   - Adapt it to agency_toolkit needs
   - Migrate config structure
   - Add config validate/show commands
   - Add tests (8-10 tests)

**Total:** ~15 hours
**Pros:** Production-ready code, faster delivery, battle-tested patterns, less code to maintain
**Cons:** Requires evaluation phase, less custom learning

---

## Strategic Recommendation

**Use Option B (Integrate Packages)** for these reasons:

1. **Code Reuse:** Both packages are well-architected, tested prototypes
   - Prompt Registry: 10+ test cases, variable substitution, versioning
   - Phoenix Config: Environment awareness, validation, YAML support

2. **Time Efficiency:** 4 hours saved per epic
   - Epic 2.1: 7h → 4h (use existing system)
   - Epic 2.2: 4h → 3h (use existing system)

3. **Quality:** Both packages have been refined and documented
   - Error handling patterns already implemented
   - Type hints and validation built-in
   - Documentation already complete

4. **Portfolio Value:** Shows ability to evaluate, integrate, and adapt existing solutions
   - Better than rebuilding from scratch
   - Demonstrates architectural thinking

---

## Proposed Execution Plan

### Phase 1: Test Coverage (Epic 1.4) - ~8 hours
**Parallel with package evaluation**

```
Week 1 (2-3 days):
  Day 1: Write tests for briefing/interactive.py (8% → 70%)
  Day 2: Write tests for social/batch.py (13% → 70%)
  Day 3: Write tests for os_interactive.py (17% → 70%)

Result: 459 tests → ~550+ tests (coverage 71% → 80%+)
```

### Phase 2: Prompt System (Epic 2.1) - ~4 hours
**Parallel with Phase 1**

```
Day 1:
  - Deep dive into prompt_registry_ structure
  - Evaluate fit for agency_toolkit
  - Identify needed modifications

Day 2-3:
  - Integrate PromptRegistry into agency_toolkit
  - Migrate MISTRAL_PROFILES from config.py
  - Migrate hardcoded prompts from social/, briefing/
  - Create prompts/ directory structure
  - Add 10-15 integration tests

Result: All prompts externalized, versioning support
```

### Phase 3: Config System (Epic 2.2) - ~3 hours
**After Phase 2**

```
Day 1:
  - Deep dive into phoenix_config_ structure
  - Evaluate fit for agency_toolkit
  - Identify needed modifications

Day 2:
  - Integrate UniversalConfig into agency_toolkit
  - Migrate existing config.toml structure
  - Add environment-aware configs (dev/test/prod)
  - Add schema validation
  - Add `config validate` command
  - Add `config show` command
  - Add 8-10 tests

Result: Structured, validated config with env support
```

---

## Work Breakdown

### Epic 1.4: Test Coverage Baseline

| Module | Current | Target | Effort | Approach |
|--------|---------|--------|--------|----------|
| `core/briefing/interactive.py` | 8% | 70% | 3h | Mock user input, PDF verification |
| `core/social/batch.py` | 13% | 70% | 3h | CSV/JSON parsing, per-row errors |
| `core/os_interactive.py` | 17% | 70% | 2h | Mock questionary, test flows |

**Exit Criteria:**
- All 3 modules ≥70% coverage
- New tests: 30-40 tests
- Total suite: 459 → 520+ tests

### Epic 2.1: Prompt Registry Integration

| Component | File(s) | Effort | Notes |
|-----------|---------|--------|-------|
| Evaluate | `docs/prompt_registry_/` | 1h | Assess completeness, Python version, dependencies |
| Adapt | - | 1h | Customize for agency_toolkit structure |
| Integrate | `agency_toolkit/prompts/` | 1.5h | Create directory, loader, migrate MISTRAL_PROFILES |
| Test | `tests/unit/test_prompts.py` | 0.5h | 10-15 tests for registry operations |

**Exit Criteria:**
- PromptRegistry imported and working
- All MISTRAL_PROFILES loaded from files
- All hardcoded prompts externalized
- Versioning support (e.g., `creative.v2.txt`)
- 15+ new tests

### Epic 2.2: Config Management Integration

| Component | File(s) | Effort | Notes |
|-----------|---------|--------|-------|
| Evaluate | `docs/phoenix_config_/` | 0.5h | Assess completeness, structure |
| Adapt | - | 0.5h | Customize for agency_toolkit |
| Integrate | `agency_toolkit/config/universal.py` | 1h | Create config classes, loaders |
| Commands | `agency_toolkit/commands/config.py` | 0.5h | `config validate` + `config show` |
| Test | `tests/unit/test_universal_config.py` | 0.5h | 8-10 tests for config operations |

**Exit Criteria:**
- UniversalConfig imported and working
- All config in TOML or env vars
- Schema validation functional
- `config validate` command works
- `config show` command works
- 10+ new tests

---

## Success Metrics

### Test Coverage
- [ ] Core modules: 70%+ coverage
- [ ] Total suite: 500+ tests
- [ ] All new tests passing

### Code Quality
- [ ] No new CVEs introduced
- [ ] Type hints on all new code
- [ ] Full docstrings
- [ ] Pre-commit compliant

### Integration Quality
- [ ] PromptRegistry working end-to-end
- [ ] UniversalConfig working end-to-end
- [ ] Both systems play nicely together
- [ ] No performance regressions

---

## Package Evaluation Checklist

### For Prompt Registry
- [ ] Check Python version compatibility
- [ ] Verify dependencies (Jinja2, etc.)
- [ ] Review error handling patterns
- [ ] Check variable substitution approach
- [ ] Assess versioning strategy
- [ ] Review test coverage
- [ ] Check for any hardcoded paths

### For Phoenix Config
- [ ] Check Python version compatibility
- [ ] Verify YAML parsing approach
- [ ] Review validation patterns
- [ ] Check environment variable handling
- [ ] Assess dataclass structure
- [ ] Review test coverage
- [ ] Check type hints completeness

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Packages don't fit | Have Epic 1.4 (tests) as fallback; can still do Epics 2.1/2.2 from scratch |
| Integration complexity | Start with minimal integration, iterate |
| Breaking existing code | Comprehensive test coverage (Phase 1) will catch issues |
| Performance regression | Benchmark before/after config and prompt loading |

---

## Timeline

```
Recommended Sprint: 2-3 weeks

Week 1:
  ✅ Epic 1.4 (tests) + evaluate packages in parallel

Week 2:
  ✅ Epic 2.1 (prompts) integration
  ✅ Epic 2.2 (config) integration + testing

Week 3 (Optional):
  ✅ Epic 3.1 (UX improvements)
  ✅ Polish and documentation
```

---

## Next Immediate Actions

1. **Review this plan** with requirements
2. **Decision:** Option A (roadmap) vs Option B (packages)?
3. **If Option B:**
   - Start Epic 1.4 (tests) immediately
   - Assign package evaluation (1-2 hours)
   - Plan integration in parallel
4. **If Option A:**
   - Start Epic 1.4 as planned
   - Build custom prompt system
   - Build custom config system

---

## Recommendation Summary

**Go with Option B (Package Integration)** because:

1. ✅ Faster delivery (15h vs 19h)
2. ✅ Higher quality (battle-tested code)
3. ✅ Better portfolio (shows integration skills)
4. ✅ Less technical debt (less custom code to maintain)
5. ✅ Scalable foundation (both packages designed for growth)

**Start with:** Epic 1.4 (tests) while evaluating packages

**First Commit Window:** 1-2 weeks to complete all three epics

---

**Ready to proceed?** Let me know which path and I'll start the first epic!
