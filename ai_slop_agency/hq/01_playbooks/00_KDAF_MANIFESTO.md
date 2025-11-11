# KDAF: Knowledge-Driven Agency Framework
## The Anti-Bullshit Manifesto

**Version:** 2.0
**Last Updated:** 2025-11-10

---

## The Problem

AI agents produce **confident, untrue statements**. LLM self-verification results in:
- Performance collapse through compounding error loops
- Circular reasoning (model validates its own output)
- Fake confidence metrics (imitating confidence, not introspecting)

**Reality:** AI is FAST but UNRELIABLE.

---

## The Solution: External Validation ONLY

### Core Principle
**NO claims without TOOL OUTPUT or CITED SOURCE**

This eliminates:
- Circular reasoning
- Unverifiable assertions
- Hallucinated "facts"

### The Three Phases

```
INPUT → VERSTEHEN → RECHERCHIEREN → VALIDIEREN → OUTPUT
```

#### Phase 1: VERSTEHEN (Semantic Understanding)
**Goal:** Transform ambiguous request into verifiable scope

**Protocol:**
1. Extract facts ONLY (no interpretation)
2. Identify knowledge gaps (CRITICAL UNKNOWNS)
3. Generate pre-research questions
4. **Validation questions:** "How can we MEASURE this?"

**Anti-Bullshit Check:**
- □ No assumptions made
- □ Knowledge gaps explicitly listed
- □ Validation method identified

#### Phase 2: RECHERCHIEREN (Knowledge Acquisition)
**Goal:** Build verifiable ground truth from external sources

**Protocol:**
1. **Official Docs** (Primary) → Technology capabilities
2. **Best Practices** (Secondary) → 3+ sources + <CURRENT_YEAR>
3. **Real Examples** (Case Studies) → GitHub, production systems
4. **Tool Research** → Define validation plan

**Anti-Bullshit Check:**
- □ Every claim has SOURCE
- □ Best practices have 3+ citations
- □ Examples from REAL projects
- □ Validation tools SPECIFIC

#### Phase 3: VALIDIEREN (Data-Driven Validation)
**Goal:** Prove claims with tool outputs

**Protocol:**
1. **Code Quality:** flake8, bandit, radon, pip-audit
2. **Performance:** cProfile, N+1 detection
3. **Architecture:** Similar systems, benchmarks, limitations
4. **Timelines:** Analogous estimation, 3-point, historical data

**Anti-Bullshit Check:**
- □ Claims backed by tool output
- □ No subjective assessments
- □ Tool outputs stored raw + analyzed

---

## Strategic Value

### Project Failure Modes MITIGATED

| Failure Mode | Industry Rate | KDAF Antidote |
|--------------|---------------|---------------|
| Inaccurate requirements | 37% | Phase 1: Formal requirements engineering |
| Unrealistic deadlines | Top 3 | Phase 3.4: Evidence-based estimation |
| Poor communication | 56% | Rigid output format (Executive Summary + Confidence) |
| Skills gap | Common | Phase 1: Proactive unknown identification |

### Output Format (Data Storytelling)

Every deliverable includes:
1. **Executive Summary** → Non-technical, actionable
2. **Findings** → Technical details with tool outputs
3. **Confidence Assessment** → "HIGH because [tool X confirmed]"
4. **Sources/Appendix** → Full verifiability

---

## Positioning

**We are:** A premium "anti-bullshit" consulting framework
**We prove:** Reliability through objective data
**We trade:** Increased overhead for cheaper cost of failure

---

## Golden Rules

1. **If you can't cite it or measure it, don't say it**
2. **Tool outputs are truth; everything else is speculation**
3. **External validation ONLY (no circular reasoning)**
4. **Cumulative intelligence (every project grows the knowledge base)**
5. **Confidence is transparent (backed by data points)**

---

## Monorepo Structure

```
/hq/        → Knowledge base, playbooks, protocols (THE MOAT)
/clients/   → Standardized KDAF project structure
/shared/    → CLI automation, validation tools, configs
/archive/   → Experiments, working prototypes (for reference)
```

---

## Usage

```bash
# Create new project
vibe new-project --client acme_corp --name django_audit

# Generate research checklist
vibe research --project django_audit

# Run validation tools
vibe validate --project django_audit

# Compile final report
vibe report --project django_audit
```

---

## Philosophy in Action

**Before KDAF:**
> "This codebase has poor performance and should use microservices."

**After KDAF:**
> "Profiling shows function X consumes 2.3s (cProfile output: 02_validation_and_reports/tool_outputs/cprofile/2025-11-10_profile.prof).
>
> Architecture validation: Found 3 similar systems [sources], 2/3 use monolith at this scale. Microservices introduce complexity (Source: Martin Fowler 2024).
>
> **Recommendation:** Optimize hot spots first. Consider microservices only if monolith optimization fails.
>
> **Confidence:** HIGH (based on profiling data + 3 case studies)"

---

**Remember:** Your job is to make AI FAST **and** RELIABLE through engineering discipline + automation.

AI writes code. You ensure it's CORRECT, MAINTAINABLE, and PRODUCTION-READY.
