# Phase 3: Data-Driven Validation Protocol

**Purpose:** Prove claims with tool outputs (not opinions)

**Core Rule:** NO claims without TOOL OUTPUT or CITED SOURCE

---

## Validation Stack by Category

### 1. Code Quality Validation (Python)

**Tools Stack:**
```bash
# Baseline: Style, syntax, basic complexity
flake8 src/ --max-complexity=10

# Security: Static analysis for vulnerabilities
bandit -r src/ -f json

# Maintainability: Deep complexity analysis
radon cc src/ -a
radon mi src/

# Dependencies: Supply chain risk
pip-audit
```

**Output:** Replaces "code quality is bad" with "flake8 found 47 issues (12 critical)"

**Location:** `02_validation_and_reports/tool_outputs/`

---

### 2. Performance Validation

**Application Layer:**
```bash
# Profile Python code
python -m cProfile -o output.prof main.py

# Analyze profile
python -m pstats output.prof
```

**Database Layer:**
```sql
-- PostgreSQL query analysis
EXPLAIN ANALYZE <query>;

-- Django N+1 detection
python manage.py debugsqlshell
```

**Output:** Replaces "it's slow" with "function X takes 2.3s (83% of total time)"

---

### 3. Architecture Validation

**Method:** Data-driven defense against generic advice

**Required Evidence:**
- `similar_systems_found`: Case studies at similar scale
- `scalability_evidence`: Quantitative benchmarks
- `known_limitations`: Disconfirming evidence

**Example:**
```yaml
architecture_recommendation: "Monolith"
similar_systems:
  - name: "Shopify"
    scale: "millions of users"
    architecture: "Modular monolith"
    source: "[engineering blog 2024]"
  - name: "Stack Overflow"
    scale: "200M+ monthly visits"
    architecture: "Monolith"
    source: "[architecture post 2023]"
scalability_evidence:
  - "Monolith handles 10k req/s with proper optimization [benchmark]"
known_limitations:
  - "Deployment coordination harder (all or nothing deploy)"
  - "Team scaling beyond 50 engineers becomes challenging"
confidence: "HIGH"
reasoning: "2 case studies at scale + quantitative benchmarks"
```

---

### 4. Timeline & Cost Validation

**Method:** Evidence-based estimation (not gut feel)

**Techniques:**
1. **Analogous Estimation:** Cite similar projects
2. **Three-Point Estimation:** Optimistic / Realistic / Pessimistic
3. **Historical Data:** Past project velocity

**Example:**
```yaml
estimate: "5 weeks ±1 week"
confidence: "MEDIUM"
reasoning:
  analogous: "Similar Django refactor took 4 weeks [internal project Q3-2024]"
  three_point:
    optimistic: 4 weeks
    realistic: 5 weeks
    pessimistic: 7 weeks
  assumptions:
    - "1 full-time engineer"
    - "No major blockers"
    - "Existing test coverage >60%"
```

---

## Tool Usage via CLI

### Run Full Validation
```bash
vibe validate --project <project_name>
```

This runs:
1. flake8 → `02_validation_and_reports/tool_outputs/flake8/<timestamp>_linting.txt`
2. bandit → `02_validation_and_reports/tool_outputs/bandit/<timestamp>_security.json`
3. radon → `02_validation_and_reports/tool_outputs/radon/<timestamp>_complexity.txt`

### Manual Deep Dive
For capsule audit (comprehensive analysis):
```bash
cd shared/tools_capsule_audit
python -m meta_audit analyze --path <client_code_path>
```

---

## Analysis Protocol

### Step 1: Store Raw Outputs
**Never modify tool outputs.** Store as-is in `tool_outputs/`.

### Step 2: Write Analysis
In `02_validation_and_reports/written_analysis/`, create:

```markdown
# Finding: <Issue Name>
Date: 2025-11-10
Tool: bandit

## Tool Output Summary
bandit identified 3 HIGH severity issues:
- [B201] Flask app runs with debug=True (security risk)
- [B601] Shell injection vulnerability in subprocess call
- [B105] Hardcoded password in config

Full output: `../tool_outputs/bandit/2025-11-10_security.json`

## Analysis
1. **Debug=True in production:**
   - Impact: Exposes stack traces, environment variables
   - Evidence: Line 42 in app.py
   - Source: OWASP Top 10 - Security Misconfiguration

2. **Shell injection:**
   - Impact: Command injection attack vector
   - Evidence: Line 89 in utils.py uses shell=True without sanitization
   - Source: CWE-78

3. **Hardcoded password:**
   - Impact: Credentials in version control
   - Evidence: config.py line 12
   - Source: OWASP A02:2021 - Cryptographic Failures

## Recommendation
1. Remove debug=True (immediate)
2. Replace subprocess.call(shell=True) with subprocess.run(shell=False, args=[...])
3. Move credentials to environment variables

## Confidence: HIGH
**Reason:** Backed by bandit static analysis + OWASP/CWE standards
```

---

## Anti-Bullshit Checklist

- □ Every claim references tool output file
- □ Tool outputs stored RAW (unmodified)
- □ Analysis separates observation (tool said X) from interpretation
- □ Recommendations backed by sources (OWASP, CWE, etc.)
- □ Confidence assessment explains reasoning

---

## Output Structure

```
02_validation_and_reports/
├── tool_outputs/              # Raw, unmodified
│   ├── flake8/
│   ├── bandit/
│   ├── radon/
│   └── cprofile/
└── written_analysis/          # Human analysis of tool outputs
    ├── 2025-11-10_security_issues.md
    ├── 2025-11-10_complexity_hotspots.md
    └── 2025-11-11_performance_bottleneck.md
```

---

## Remember

**Tool outputs = Truth**
**Everything else = Speculation**

If you can't run a tool to prove it, cite a source. If you can't do either, don't say it.
