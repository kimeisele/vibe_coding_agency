# Meta-Audit

**A comprehensive Python code analysis tool with AI-powered insights.**

Detect security vulnerabilities, complexity issues, AI code smells, and architectural patterns across single projects or entire codebases.

---

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Analyze a single project
meta-audit analyze --path /path/to/project

# Analyze multiple projects (batch processing)
meta-audit analyze \
  --capsule project1.capsule.json \
  --capsule project2.capsule.json \
  --format json

# Create a project snapshot (capsule)
meta-audit capsule create --path /path/to/project
```

---

## 📊 What Does It Analyze?

| Analyzer | What It Detects | Tool Used |
|----------|----------------|-----------|
| **Security** | SQL injection, hardcoded passwords, command injection | Bandit |
| **Complexity** | High cyclomatic complexity, maintainability issues | Radon |
| **AI Slop** | Generic variable names, placeholder comments, vibe-coded patterns | Custom heuristics |
| **God Objects** | Classes with too many responsibilities (SRP violations) | Custom detector |

---

## 📖 Documentation

- **[CLI Examples](docs/CLI_EXAMPLES.md)** - Practical workflows & recipes (START HERE!)
- **[User Guide](docs/USER_GUIDE.md)** - Complete reference documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design & data flow
- **[Test Results](BATCH_PROCESSOR_TEST_RESULTS.md)** - Batch processing verification

---

## 🔥 Common Use Cases

### 1. Audit a Single Project

```bash
meta-audit analyze --path . --format table
```

**Output:** Terminal table with all findings sorted by severity.

### 2. Batch Analysis of Multiple Projects

```bash
# Create capsules (project snapshots)
meta-audit capsule create --path /project1 --output project1.capsule.json
meta-audit capsule create --path /project2 --output project2.capsule.json

# Analyze all capsules together
meta-audit analyze \
  --capsule project1.capsule.json \
  --capsule project2.capsule.json \
  --format json \
  --output-file results.json
```

**Why capsules?**
- Snapshot of project at specific point in time
- Share for offline analysis (no source code needed)
- Compare across versions
- Archive for compliance/auditing

### 3. CI/CD Integration

```yaml
# .github/workflows/audit.yml
- name: Run Meta-Audit
  run: |
    pip install meta-audit
    meta-audit analyze --path . --format json --output-file report.json

- name: Check for CRITICAL issues
  run: |
    CRITICAL=$(jq '.summary.CRITICAL' report.json)
    if [ "$CRITICAL" -gt 0 ]; then
      exit 1
    fi
```

---

## 🧬 Architecture Overview

```
CLI → Collectors (parallel) → Aggregation → Report
       ├─ Radon (complexity)
       ├─ Bandit (security)
       ├─ AI Slop detector
       └─ God Object detector
```

**Key Design Principles:**
- **Phase 1 (Collectors):** 100% data-driven, no LLM (fast, deterministic)
- **Phase 2 (Aggregation):** Generate reports (JSON, terminal table)
- **Phase 3 (Optional):** LLM-powered insights (requires API key)

---

## 🛠️ Development

### Run Tests

```bash
pytest tests/
```

### Install for Development

```bash
pip install -e ".[dev]"
```

### Project Structure

```
src/meta_audit/
├── cli/              # Click-based CLI
├── analyzers/        # Batch processing & collectors
│   └── collectors/   # Parallel static analyzers
├── generators/       # Report generation
├── agents/           # LLM orchestration (Phase 5)
├── providers/        # LLM provider abstraction
└── core/             # Data models (Pydantic)
```

---

## 📈 Example Output

```bash
$ meta-audit analyze --path /my/project

Meta-Audit Report
================================================================================
Critical:   1 | High:   3 | Medium:   8 | Low:  15 | Total:  27
Execution time: 2.45s

Severity  File                       Line  Pattern              Message
────────  ────────────────────────   ────  ───────────────────  ────────────────────
CRITICAL  src/auth.py                 42   hardcoded_password   Use of hardcoded password
HIGH      src/api/models.py          105   high_complexity      Cyclomatic complexity 15
HIGH      src/db/queries.py           88   sql_injection        Potential SQL injection
MEDIUM    src/utils/helpers.py        20   high_complexity      McCabe complexity 11
...
```

---

## 🤝 Contributing

See `docs/USER_GUIDE.md` for development guidelines.

---

## 📄 License

MIT

---

## 🔗 Related Projects

- [Bandit](https://github.com/PyCQA/bandit) - Security linter
- [Radon](https://github.com/rubik/radon) - Complexity analyzer
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

---

## ⚡ Performance

- **Single project** (~50 files): ~1-2 seconds
- **Batch processing** (2 projects, 148 files): ~1.4 seconds
- **Parallel collectors:** 3 workers by default

---

**Need help?** Check `docs/CLI_EXAMPLES.md` for 8 practical examples!
