# Deployment Checklist & Strategic Execution Plan

**Document**: Production Deployment & Epic 7 Execution
**Date**: 2025-11-10
**Status**: 🟢 READY FOR DEPLOYMENT
**Prepared By**: AI Strategy & Development

---

## PHASE 1: DEPLOY TO PRODUCTION (TODAY)

### Pre-Deployment Verification

**Code Quality**:
- [x] 726 tests passing (verified today)
- [x] CLI fully functional (Typer/Click fixed)
- [x] Performance SLOs validated (112 sec for 30 posts)
- [x] No false "green signals" (real subprocess tests)
- [x] All critical recovery items complete (Epics 2.5 & 4.0)

**Documentation**:
- [x] ROADMAP.md updated with current status
- [x] RECOVERY_STATUS updated (marked RESOLVED)
- [x] STATUS_OVERVIEW updated (GREEN status)
- [x] All changes pushed to origin/master

**Known Blockers**:
- ⚠️ WU-7.1 (PDF Export): Known issue but not deployment blocker
  - Workaround: Users can export to markdown
  - Impact: Briefing feature partially available (md works, pdf has issues)
- ⚠️ Pre-commit Hooks: Developer friction, not user-facing
  - Impact: Dev team uses `--no-verify`, no production impact

### Deployment Readiness Assessment

| Item | Status | Evidence |
|------|--------|----------|
| Core Functionality | ✅ Ready | All 8 CLI commands work end-to-end |
| Performance | ✅ Meets SLOs | 30 posts in 112 seconds (batch mode) |
| Error Handling | ✅ Robust | Graceful failures tested in UAT |
| Data Integrity | ✅ Validated | All workflows produce expected outputs |
| Monitoring | ⚠️ Basic | Error logging in place, no metrics dashboard |
| Rollback Plan | ⚠️ Manual | Git tags + version control, no auto-rollback |

### Pre-Deployment Checklist

```
System & Infrastructure:
  [ ] Deployment environment prepared (containers/venv)
  [ ] Dependencies installed (check pyproject.toml pins)
  [ ] API keys configured (Mistral, image providers)
  [ ] Output directories writable
  [ ] Log rotation configured

Testing:
  [ ] Run full test suite in staging: pytest tests/unit/ tests/integration/ tests/core/ -q
  [ ] Manual smoke test: toolkit social "test" --dry-run
  [ ] Manual smoke test: toolkit briefing "test" --dry-run
  [ ] Manual smoke test: toolkit image "test" --dry-run

Documentation:
  [ ] README updated with deployment instructions
  [ ] DEVELOPMENT.md has troubleshooting section
  [ ] ERROR_HANDLING.md available for ops team
  [ ] Support contact info documented

Monitoring:
  [ ] Error logs being collected
  [ ] Performance metrics baseline established (112 sec for 30 posts)
  [ ] Alert thresholds set (if monitoring available)
  [ ] Rollback plan documented
```

### Deployment Commands

```bash
# Pre-deployment verification
python3 -m pytest tests/unit/ tests/integration/ tests/core/ -q

# Manual smoke tests
python3 -m agency_toolkit.cli_app social "Test post" --dry-run
python3 -m agency_toolkit.cli_app briefing "Test briefing" --dry-run
python3 -m agency_toolkit.cli_app image "test image" --dry-run

# Deploy (example - adjust for your infrastructure)
# git checkout <version-tag>
# pip install -e .
# Run verification suite

# Verify post-deployment
python3 -m agency_toolkit.cli_app --help
python3 -m agency_toolkit.cli_app info --providers
```

### Go/No-Go Decision Criteria

**GO if**:
- ✅ All core tests passing
- ✅ Manual smoke tests pass
- ✅ No regressions from previous version
- ✅ Performance meets SLOs
- ✅ Team is ready for support

**NO-GO if**:
- ❌ Tests failing
- ❌ Critical bugs discovered in staging
- ❌ Performance degraded >10%
- ❌ Deployment infrastructure not ready

---

## PHASE 2: SOLIDIFY QUALITY (TODAY/TOMORROW - 1-2 HOURS)

### WU-7.1: PDF-Export Repair

**Current Status**: ⚠️ KNOWN ISSUE
- PDF generation works but has intermittent hangs
- `test_briefing_integration.py` is skipped
- Root cause: Reportlab font loading

**Investigation Checklist**:
```
[ ] Run test_briefing_integration with verbose output
[ ] Profile PDF generation to identify bottleneck
[ ] Check if font cache is being reused
[ ] Verify reportlab version compatibility
[ ] Test with large briefings (10+ pages)
[ ] Identify exact line causing hang
```

**Quick Fixes to Try** (in order):
1. Cache fonts aggressively
2. Use system fonts instead of embedded
3. Reduce PDF quality/compression
4. Simplify template (fewer graphics)
5. Update reportlab version

**Success Criteria**:
- [ ] PDF generation completes in <2 seconds
- [ ] `test_briefing_integration.py` passes (both md and pdf)
- [ ] No hangs or timeout errors
- [ ] 10 PDFs generated sequentially without issues

**Files to Investigate**:
- `agency_toolkit/core/briefing/pdf_writer.py`
- `tests/integration/test_briefing_integration.py`

**Recommended Approach**:
```python
# Step 1: Enable verbose logging
# Step 2: Add timing instrumentation
# Step 3: Profile each reportlab call
# Step 4: Identify the culprit
# Step 5: Apply fix and verify
```

---

## PHASE 3: REMOVE FRICTION (TOMORROW/THIS WEEK - 1-2 HOURS)

### Pre-commit Hook Issue: Root Cause & Fix

**Root Cause**: pip/requests incompatibility in pre-commit's Python 3.11 environment
- Pre-commit tries to install mypy with vendored dependencies
- pip 21.x conflicts with requests library
- Results in: `ImportError: cannot import name 'JSONDecodeError'`

**Affected Team**: All developers (Linux/macOS)
**Impact**: Must use `git commit --no-verify` (friction, not blocker)

**Solution Approach** (pick one):

**Option A: Disable mypy in pre-commit (FASTEST - 5 min)**
```yaml
# .pre-commit-config.yaml - Remove mypy hook
# Keep: black, ruff, trailing-whitespace
# Run mypy separately: mypy agency_toolkit/ --ignore-missing-imports
```
- **Pro**: Instant fix, minimal changes
- **Con**: mypy still runs but outside pre-commit

**Option B: Use Docker for pre-commit (ROBUST - 15 min)**
```yaml
# Add Docker-based pre-commit environment
- repo: local
  hooks:
    - id: mypy-docker
      name: mypy (docker)
      entry: docker run --rm -v $(pwd):/app mypy:latest
      language: system
```
- **Pro**: Isolated environment, no system conflicts
- **Con**: Requires Docker installed

**Option C: Upgrade Python (BEST - 30 min setup)**
- Use Python 3.12+ (pip is fixed)
- Or use pyenv to switch versions for pre-commit

**Option D: Clear & Reinstall (QUICK - 2 min)**
```bash
rm -rf ~/.cache/pre-commit/
pre-commit install
```
- **Pro**: Simple, sometimes works
- **Con**: Often doesn't solve underlying issue (tried already)

**RECOMMENDED**: Option A (Disable mypy in pre-commit)
- Fastest to implement
- Doesn't remove mypy (still runs manually)
- Unblocks team immediately

**Implementation**:
```bash
# 1. Edit .pre-commit-config.yaml (remove mypy hook)
# 2. Test: git commit --allow-empty -m "test"
# 3. Should NOT ask for --no-verify anymore
# 4. Update CI to run: mypy agency_toolkit/ --ignore-missing-imports
# 5. Commit change and push
```

---

## PHASE 4: BUILD HIGH-IMPACT FEATURES (THIS WEEK - 4-6 HOURS)

### WU-7.3: Interactive Wizards

**Objective**: Make toolkit accessible to non-technical users

**User Personas**:
- **Marketing Manager**: Wants to create social posts without learning CLI flags
- **Designer**: Prefers guided workflow over remembering command syntax
- **Intern**: First-time user, needs hand-holding

**Wizard Structure** (High Priority):
```
toolkit social (no args)
├─ What's your message? [text input]
├─ What style? [choice: modern, bold, minimal]
├─ What color? [choice: auto, warm, cool, neutral]
├─ Add background image? [yes/no]
├─ How many posts? [number: 1-100]
├─ Output directory? [path, default: ./output]
├─ Generate now? [yes/no/dry-run]
```

**Implementation Steps**:
1. Create `interactive_social_wizard()` function
2. Use questionary for prompts
3. Validate inputs
4. Execute underlying `social generate` command
5. Display results with progress bar

**Success Criteria**:
- [ ] Non-technical user can create post without documentation
- [ ] All prompts are clear and have helpful defaults
- [ ] Error messages are actionable
- [ ] User can abort at any point without issues
- [ ] Test with 2-3 real users (feedback loop)

**Files to Create/Modify**:
- `agency_toolkit/commands/interactive_utils.py` (expand)
- `agency_toolkit/commands/social.py` (integrate wizard)

**Timeline**:
- 30 min: Code wizard function
- 30 min: Integrate with social command
- 30 min: Testing & refinement
- 1 hour: User testing & iteration
- **Total: 2.5-3 hours**

---

## EXECUTION SUMMARY

| Phase | Task | Effort | Timeline | Blocker |
|-------|------|--------|----------|---------|
| 1 | Deploy to Production | 30 min | Today | ❌ No |
| 2 | Fix PDF Export (WU-7.1) | 1-2h | Today/Tomorrow | ⚠️ Low (workaround available) |
| 3 | Fix Pre-commit Hooks | 5-15 min | Tomorrow | ❌ No (friction only) |
| 4 | Build Wizards (WU-7.3) | 2.5-3h | This Week | ❌ No |

**Total Effort**: ~4.5-6 hours
**Total Timeline**: Today through end of week
**Critical Path**: Deploy → PDF fix → Hooks → Wizards (sequential)

---

## Success Metrics

**After Deployment**:
- ✅ Production users can run all 8 commands successfully
- ✅ Batch processing works (30 posts in <2 minutes)
- ✅ Error messages are helpful

**After PDF Fix**:
- ✅ `test_briefing_integration.py` passes
- ✅ PDF exports complete <2 seconds
- ✅ All briefing features available

**After Hook Fix**:
- ✅ Team uses `git commit` without `--no-verify`
- ✅ CI/CD runs pre-commit checks successfully
- ✅ mypy still validates type hints

**After Wizards**:
- ✅ Non-technical users can create content
- ✅ Reduced support burden (self-guided)
- ✅ User feedback positive

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| PDF fix takes longer | Medium | Delays hook fix | Have Option B ready (mypy workaround) |
| Deployment discovers issues | Low | Rollback needed | Keep v0.1 tag, maintain git history |
| User testing unavailable | Low | Delay feedback | Proceed with built-in QA if needed |
| Mistral API down | Low | Image/query features fail | Use dry-run, have error message ready |

---

## Next Immediate Actions (TODAY)

1. **Review this checklist** ✓
2. **Execute deployment verification**:
   ```bash
   pytest tests/unit/ tests/integration/ tests/core/ -q
   ```
3. **Run manual smoke tests** (all 3 commands)
4. **Get deployment approval from stakeholders**
5. **Deploy to production** (if approval given)
6. **Schedule PDF fix** (1-2 hours tomorrow)

---

**Document Status**: 🟢 CURRENT & ACTIONABLE
**Last Updated**: 2025-11-10
**Next Review**: After deployment
