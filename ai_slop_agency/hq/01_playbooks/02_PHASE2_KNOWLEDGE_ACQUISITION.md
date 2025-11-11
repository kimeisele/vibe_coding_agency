# Phase 2: Knowledge Acquisition Protocol

**Purpose:** Build verifiable ground truth from external sources

**Core Rule:** NEVER claim without SOURCE. Speculation is forbidden.

---

## Research Stack (In Priority Order)

### 1. Official Documentation (PRIMARY SOURCES)

**What:** Technology's official docs, API references, changelogs

**Why:** Stable, authoritative, maintained by creators

**How:**
- Start with official docs site
- Check version-specific docs (important!)
- Look for migration guides if version change involved
- Review security advisories

**Anti-Bullshit:** Official docs = CAPABILITIES (what tech CAN do)

---

### 2. Current Best Practices (SECONDARY SOURCES)

**What:** Industry consensus on how to USE the technology

**Validation Rules:**
- **3+ Sources:** Consensus required (like intelligence "Three Source Rule")
- **<CURRENT_YEAR:** Currency matters in fast-moving tech

**How:**
- Tech blogs (engineering blogs of companies using it at scale)
- Conference talks / YouTube tech talks
- Academic papers (for algorithmic/theoretical questions)
- Stack Overflow (for common pitfalls)

**Anti-Bullshit:** Best practices = APPLICATION (how to use optimally)

**Distinguish:**
- ✅ "3 sources (Google 2024, Netflix 2024, Shopify 2023) recommend connection pooling"
- ❌ "We should use connection pooling" (no sources)

---

### 3. Real-World Examples (CASE STUDIES)

**What:** Production systems using this technology

**Why:** Ground recommendations in PRACTICE, not theory

**How:**
- GitHub: Search repos, read commit messages, check issues
- Company engineering blogs: Real migration stories
- Postmortems: Learn from failures
- Open source projects at scale

**Anti-Bullshit Check:**
- "Company X (similar scale) uses monolith successfully" → Context-aware
- "Microservices are always better" → Architecture astronautism ❌

---

### 4. Tool & Metrics Research

**What:** Identify tools to VALIDATE claims in Phase 3

**Why:** Links Phase 1 (problem) to Phase 3 (proof)

**How:**
- For Python: flake8, bandit, radon, cProfile
- For JavaScript: eslint, prettier, lighthouse
- For databases: EXPLAIN ANALYZE, query profilers
- For performance: Load testing tools, APM

**Anti-Bullshit:** Define validation plan BEFORE making claims

---

## Research Log Structure

```
00_scoping_and_research/02_research_log/
├── docs/
│   ├── django_4_performance_guide.pdf
│   └── postgresql_query_optimization.md
├── articles/
│   ├── instagram_django_scale_2024.md
│   ├── shopify_db_optimization_2024.md
│   └── netflix_python_profiling_2023.md
├── examples/
│   └── github_repos_using_django_orm.md
└── tools/
    └── validation_tools_identified.md
```

---

## Anti-Bullshit Checklist

Before proceeding to Phase 3:

- □ Every recommendation has SOURCE (linked/cited)
- □ Best practices have 3+ citations
- □ Examples are from REAL projects (not tutorials)
- □ Validation tools are SPECIFIC (not "we should test")
- □ Sources include publication YEAR
- □ Sources are RELEVANT to client's scale/context

---

## Example: BAD vs GOOD

### ❌ BAD
> "For Django performance, you should use caching and optimize queries. Connection pooling is also recommended."

**Problems:**
- No sources
- Generic advice
- No context
- No validation plan

### ✅ GOOD
> **Finding: Query Optimization Priority**
>
> **Sources:**
> 1. Django Official Docs (2024): django-debug-toolbar for query analysis [link]
> 2. Instagram Engineering Blog (2024): Reduced queries by 60% using select_related [link]
> 3. Shopify (2024): Case study on N+1 query elimination [link]
>
> **Consensus:** 3/3 sources prioritize query optimization before caching.
>
> **Validation Plan:** Use django-debug-toolbar + cProfile to identify actual bottlenecks BEFORE optimization.
>
> **Context:** All 3 sources are at scale (millions of users). Applies to client's context.
>
> **Confidence:** HIGH (backed by official docs + 3 production case studies)

---

## Generate Research Checklist

```bash
vibe research --project <project_name>
```

This creates: `00_scoping_and_research/02_research_checklist.md`
