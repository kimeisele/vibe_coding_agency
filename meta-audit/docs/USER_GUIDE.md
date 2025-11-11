# Meta-Audit User Guide

**The complete guide to analyzing Python projects with static collectors, cross-project patterns, and optional LLM enrichment.**

---

## Quick Start

### Single Project Analysis

```bash
# Analyze current directory
meta-audit analyze --path .

# Analyze specific project
meta-audit analyze --path /path/to/project --format json

# Save report to file
meta-audit analyze --path /path/to/project --output-file report.json
```

### Multi-Project (Corpus) Analysis

```bash
# Create ProjectCapsule snapshots first
meta-audit capsule create --path /path/to/project --output capsule.json

# Analyze multiple capsules
meta-audit analyze --capsule proj1.capsule.json --capsule proj2.capsule.json --format table

# Or analyze entire directory of capsules
meta-audit analyze --path ./capsules --corpus --format json
```

---

## Understanding the Analysis Pipeline

### Phase 1: Static Analysis (100% data-driven, no LLM required)

Three parallel collectors extract findings from your code:

```
┌─────────────────────────────────────────┐
│  Your Project                           │
├─────────────────────────────────────────┤
│  ↓ Radon         ↓ Bandit      ↓ AI-Slop
│  Complexity      Security      Patterns
│  Metrics         Vulns         (generic code)
└──────────────────┬──────────────────────┘
                   ↓
         Unified AnalysisResult
         (severity, confidence)
```

**Output:** List of findings with:
- `severity`: CRITICAL | HIGH | MEDIUM | LOW
- `category`: SECURITY | CODE_STRUCTURE | PERFORMANCE | MAINTAINABILITY
- `confidence`: 0.0 to 1.0 (trust level)
- `evidence`: Original data from collector
- `remediation`: Suggested fixes

### Phase 2: Report Generation

Aggregate findings into structured reports:

```
Single Project:        Corpus (Multiple):
  ↓                      ↓
  Report              CorpusReport
  (summary,             (aggregated,
   findings)            cross-project
                        patterns)
```

**Report Formats:**
- JSON: Machine-readable, all details
- Table: Human-readable terminal output
- (CSV, YAML in Phase 5)

### Phase 3: Optional LLM Enhancement (Requires GOOGLE_API_KEY)

Only for single projects (corpus analysis focuses on Phase 1+2):

```
Single Project + Phase 1 Findings
    ↓
Project Steward Agent
    ├── Routes to specialists
    ├── Generates test cases
    └── Suggests refactorings
    ↓
Enhanced Report
```

---

## ProjectCapsule Strategy

### What is a Capsule?

A **ProjectCapsule** is a JSON snapshot of your project containing:
- All Python file paths and sizes
- Selectable content (full source, signatures, or metadata-only)
- Project metadata (name, Python version, creation time)

**Use Cases:**
- Offline analysis (no access to source code)
- Archival (reproducible analysis years later)
- Multi-project comparison (corpus analysis)
- Token-efficient LLM input (smart capsule modes)

### Three Smart Capsule Modes

#### Mode 1: "Hotspot" (Recommended)
```bash
meta-audit capsule create --path /project --mode hotspot --output capsule.json
```

- **Content:** Full source code for HIGH/CRITICAL files only
- **Other files:** Metadata (path, size) only
- **Size:** 10-50% of full capsule
- **Use Case:** LLM analysis focused on problems
- **Token efficiency:** Maximum

#### Mode 2: "Signature"
```bash
meta-audit capsule create --path /project --mode signature --output capsule.json
```

- **Content:** AST-extracted function/class signatures (no implementation)
- **All files:** Included with structure only
- **Size:** 20-60% of full capsule
- **Use Case:** Structural analysis, architecture review
- **Token efficiency:** High

#### Mode 3: "Full"
```bash
meta-audit capsule create --path /project --mode full --output capsule.json
```

- **Content:** Complete source code for all files
- **Size:** 100% baseline
- **Use Case:** Brute-force analysis (not recommended)
- **Token efficiency:** Poor (expensive, noisy)

### Working with Capsules

**Create:**
```bash
meta-audit capsule create --path /path/to/project --mode hotspot

# Output: project_name.capsule.json (2025-11-10T12:30:28.415588)
```

**Inspect:**
```bash
meta-audit capsule show capsule.json

# Shows metadata, file count, size, sample files
```

**Store for later:**
```bash
# Save to archive
gsutil cp *.capsule.json gs://my-bucket/capsules/

# Load and analyze months later
meta-audit analyze --capsule gs://bucket/old_capsule.json
```

---

## Cross-Project Pattern Detection

### What Patterns Are Detected?

When analyzing a corpus (2+ projects), meta-audit automatically detects:

#### 1. Duplicate Issues
```json
{
  "pattern_type": "sql_injection",
  "severity": "HIGH",
  "projects_count": 3,
  "projects": ["auth_service", "api_gateway", "data_loader"],
  "message": "SQL injection vulnerability found in 3 projects"
}
```

**Why it matters:** Indicates systemic security issue, shared vulnerable dependency, or architectural pattern affecting multiple projects simultaneously.

#### 2. Security Vulnerabilities
```json
{
  "pattern_type": "missing_input_validation",
  "severity": "HIGH",
  "category": "security",
  "projects_count": 5,
  "projects": ["web_app", "mobile_api", "worker", "scheduler", "sync_service"],
  "message": "Security vulnerability affecting 5 projects"
}
```

**Why it matters:** Shared security problem across services requires coordinated fix.

#### 3. Code Quality Trends
```json
{
  "pattern_type": "quality_trend_code_structure",
  "severity": "MEDIUM",
  "projects_count": 4,
  "message": "Systemic code_structure quality issue affecting 4 projects"
}
```

**Why it matters:** Systematic maintainability problems suggest architectural or training issues.

### Analyzing Corpus

```bash
# Create capsules for all projects
for project in project_a project_b project_c; do
  meta-audit capsule create --path /path/to/$project \
    --output ${project}.capsule.json
done

# Analyze entire corpus
meta-audit analyze \
  --capsule project_a.capsule.json \
  --capsule project_b.capsule.json \
  --capsule project_c.capsule.json \
  --format json \
  --output-file corpus_report.json

# Review cross-project patterns
cat corpus_report.json | jq '.cross_project_patterns'
```

---

## Output Formats

### JSON Output
```bash
meta-audit analyze --path /project --format json
```

Contains:
```json
{
  "summary": {
    "CRITICAL": 2,
    "HIGH": 5,
    "MEDIUM": 12,
    "LOW": 8,
    "TOTAL": 27
  },
  "findings": [
    {
      "analyzer": "bandit",
      "file": "src/auth/password.py",
      "line": 42,
      "severity": "CRITICAL",
      "category": "security",
      "message": "Use of insecure hashing...",
      "evidence": {...},
      "remediation": [...]
    }
  ],
  "execution_time": 2.34,
  "timestamp": "2025-11-10T12:30:28.415588"
}
```

### Table Output
```bash
meta-audit analyze --path /project --format table
```

```
Meta-Audit Report
================================================================================
Critical:   2 | High:   5 | Medium:  12 | Low:   8 | Total:  27
Execution time: 2.34s
Generated: 2025-11-10T12:30:28.415588

Severity  Category        Analyzer   File                       Line  Message
────────  ──────────────  ─────────  ────────────────────────   ────  ─────────────
CRITICAL  security        bandit     src/auth/password.py         42  Use of insecure...
HIGH      code_structure  radon      src/models/main.py           15  High complexity...
```

### Corpus Report
```bash
meta-audit analyze --path ./capsules --corpus --format json
```

Adds:
```json
{
  "summary": {
    "projects_analyzed": 3,
    "CRITICAL": 5,
    "HIGH": 12,
    ...
  },
  "project_summaries": {
    "project_a": {...},
    "project_b": {...}
  },
  "cross_project_patterns": [
    {...duplicate issues...},
    {...security vulnerabilities...},
    {...quality trends...}
  ]
}
```

---

## Configuration

### Environment Variables

```bash
# Required for LLM-powered analysis (Phase 3)
export GOOGLE_API_KEY=sk_...

# Optional: Enable verbose logging
export META_AUDIT_DEBUG=1
```

### Config File (Coming in Phase 4.5)

```yaml
# config/analysis_strictness.yaml
analysis:
  strictness: "high"  # high | medium | low
  ignore_patterns:
    - "test_*.py"
    - "vendor/"
    - "migrations/"

  severity_threshold: "MEDIUM"  # Only report >= MEDIUM
  confidence_threshold: 0.75

audit:
  fail_on_critical: true
  fail_on_high: false
  max_issues_report: 100

capsule:
  default_mode: "hotspot"  # hotspot | signature | full
  include_content: true
```

---

## Interpreting Results

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Immediate risk, production impact | Fix immediately |
| **HIGH** | Significant issue, should fix | Fix in this sprint |
| **MEDIUM** | Important, address soon | Fix in next sprint |
| **LOW** | Minor improvement | Include in backlog |

### Confidence Scores

- **0.9+**: Very high confidence (trust this finding)
- **0.7-0.9**: Good confidence (likely valid)
- **0.5-0.7**: Medium confidence (review before action)
- **<0.5**: Low confidence (verify manually)

### Analyzer-Specific Hints

**Radon (Code Complexity):**
- Cyclomatic Complexity > 10 = Consider refactoring
- Maintainability Index < 50 = Difficult to maintain

**Bandit (Security):**
- SQL/NoSQL injection = Critical, fix immediately
- Hardcoded passwords = Critical, use secrets management
- Insecure serialization = High, use safe alternatives

**AI-Slop (Generated Code Patterns):**
- Generic variable names (`temp`, `data`, `x`)
- Missing docstrings in complex functions
- Suggests manual review + comments

---

## CLI Reference

```bash
# Single-project mode (default)
meta-audit analyze --path /project

# Corpus mode (multiple projects)
meta-audit analyze --corpus --path ./capsule_dir
meta-audit analyze --capsule file1.json --capsule file2.json

# Output control
meta-audit analyze --format json
meta-audit analyze --format table
meta-audit analyze --output-file report.json

# Logging
meta-audit analyze --verbose

# Capsule commands
meta-audit capsule create --path /project --mode hotspot
meta-audit capsule show capsule.json
```

---

## Troubleshooting

### "No Python files found"
```bash
# Check path exists and has .py files
ls /your/path/**/*.py | head

# Capsule system skips: .venv, .git, __pycache__, node_modules
# Make sure your code isn't in one of these directories
```

### "Collection failed"
```bash
# Check individual collectors
meta-audit analyze --path /project --verbose

# Look for collector-specific errors in logs
# Each collector (radon, bandit, ai_slop) runs independently
# One failure doesn't stop others
```

### "LLM analysis disabled (no GOOGLE_API_KEY)"
```bash
# Optional - only needed for Phase 3 enrichment
# Set if you want AI-powered synthesis
export GOOGLE_API_KEY=your_key_here

# Phase 1 (static analysis) works without it
meta-audit analyze --path /project
```

---

## What's Next?

- **Phase 4.4:** Smart Capsule modes (hotspot, signature, full)
- **Phase 4.5:** Semantic guardrails & configurable strictness
- **Phase 5:** Multi-agent orchestration & specialized personas

See `POST_MVP_ROADMAP.md` for full vision.
