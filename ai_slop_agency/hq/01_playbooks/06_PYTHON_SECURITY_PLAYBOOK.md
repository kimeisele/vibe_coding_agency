# Python Security Audit Playbook

**Purpose:** Formalize Python security knowledge to drive intelligent Phase 4 reporting
**Based on:** OWASP Top 10, PEP 8, CWE, Bandit/flake8 tool outputs
**For:** Autonomous analysis with domain expertise

---

## Part 1: Bandit Security Rules → Severity & Action

### HIGH SEVERITY (Must Fix)

#### B105: Hardcoded SQL String Bindings
- **What:** SQL binding with user-controlled strings (SQL Injection risk)
- **CWE:** CWE-89 (SQL Injection)
- **OWASP:** A03:2021 – Injection
- **Measurable:** Bandit severity = HIGH
- **Fix Priority:** CRITICAL (immediate)
- **Remediation:** Use parameterized queries with `?` or `%s` placeholders
- **Effort:** 30 minutes per query
- **Example Fix:** `db.execute("SELECT * FROM users WHERE id = ?", (user_id,))`

#### B104: Hardcoded Bind to 0.0.0.0
- **What:** Service binds to all interfaces (network exposure)
- **CWE:** CWE-200 (Information Exposure)
- **OWASP:** A01:2021 – Broken Access Control
- **Measurable:** Bandit severity = MEDIUM
- **Fix Priority:** HIGH (expose only on localhost or specific interfaces)
- **Remediation:**
  - Dev: `host="127.0.0.1"`
  - Production: Bind to specific network interface or reverse proxy
- **Effort:** 15 minutes
- **Example Fix:** `app.run(host="127.0.0.1", port=5000)`

#### B101: assert_used (in production)
- **What:** Using `assert` for data validation (removed with `python -O`)
- **CWE:** CWE-703 (Improper Check or Handling of Exceptional Conditions)
- **OWASP:** A09:2021 – Broken Exception Handling
- **Measurable:** Bandit severity = MEDIUM
- **Fix Priority:** MEDIUM (use proper exceptions)
- **Remediation:** Replace `assert condition` with `if not condition: raise ValueError(...)`
- **Effort:** 20 minutes per assert
- **Example Fix:**
  ```python
  # Bad: assert user_id > 0
  # Good:
  if user_id <= 0:
      raise ValueError("user_id must be positive")
  ```

#### B303: Insecure MD5 Hash
- **What:** Using MD5 for cryptographic purposes (cryptographically weak)
- **CWE:** CWE-327 (Use of Broken or Risky Cryptographic Algorithm)
- **OWASP:** A02:2021 – Cryptographic Failures
- **Measurable:** Bandit severity = MEDIUM
- **Fix Priority:** MEDIUM (upgrade to SHA-256)
- **Remediation:** Use `hashlib.sha256()` instead of `hashlib.md5()`
- **Effort:** 10 minutes per hash operation
- **Example Fix:** `hash_obj = hashlib.sha256(data.encode())`

#### B602: shell=True in subprocess
- **What:** Passing `shell=True` to subprocess (command injection risk)
- **CWE:** CWE-78 (OS Command Injection)
- **OWASP:** A03:2021 – Injection
- **Measurable:** Bandit severity = HIGH
- **Fix Priority:** CRITICAL (prevents shell injection)
- **Remediation:** Pass list of args, set `shell=False` (or omit it - it's the default)
- **Effort:** 15 minutes per call
- **Example Fix:**
  ```python
  # Bad: subprocess.run("ls " + user_dir, shell=True)
  # Good:
  subprocess.run(["ls", user_dir], shell=False)
  ```

### MEDIUM SEVERITY (Should Fix)

#### B108: Hardcoded temp directory
- **What:** Using hardcoded `/tmp` or `/var/tmp` (predictable, collision risk)
- **CWE:** CWE-377 (Insecure Temporary File)
- **OWASP:** A01:2021 – Broken Access Control
- **Measurable:** Bandit severity = LOW (but contextual)
- **Fix Priority:** MEDIUM (use `tempfile` module)
- **Remediation:** `import tempfile; tmpdir = tempfile.mkdtemp()`
- **Effort:** 10 minutes per location
- **Example Fix:**
  ```python
  import tempfile
  with tempfile.NamedTemporaryFile(delete=False) as f:
      f.write(data)
  ```

#### B201: flask_debug_true
- **What:** Flask debug mode enabled in production
- **CWE:** CWE-215 (Information Exposure Through Debug Information)
- **OWASP:** A05:2021 – Security Misconfiguration
- **Measurable:** Bandit severity = HIGH (if in production)
- **Fix Priority:** CRITICAL for production
- **Remediation:** Set `DEBUG = False` in production; use env variable
- **Effort:** 5 minutes
- **Example Fix:** `app.config['DEBUG'] = os.getenv('DEBUG', False)`

---

## Part 2: flake8 Style Rules → Code Quality Signals

### PEP 8 Rules That Signal Problems

#### E302: Expected 2 blank lines
- **What:** Missing blank lines between top-level functions/classes
- **Why it matters:** Reduces readability; signals rushed code
- **PEP 8 Ref:** https://pep8.org/#blank-lines
- **Fix:** Add blank line between functions
- **Effort:** 1 minute per violation

#### E501: Line too long
- **What:** Lines exceed 79 characters (or 88 for Black)
- **Why it matters:** Reduces readability; indicates complex logic that should be refactored
- **PEP 8 Ref:** https://pep8.org/#maximum-line-length
- **Fix:** Split into multiple lines or refactor
- **Effort:** 5 minutes per violation
- **Context:** If > 5 violations per file, suggests more fundamental readability issues

#### W503/W504: Line break before/after binary operator
- **What:** Inconsistent operator placement across lines
- **Why it matters:** Readability and consistency
- **Fix:** Choose one style consistently (W503 or W504, not both)
- **Effort:** 10 minutes per file

#### C901: Function too complex
- **What:** Cyclomatic complexity > threshold (usually 10)
- **Why it matters:** Indicates functions that should be broken down
- **Effort:** 30 minutes per function (requires refactoring)
- **Reference:** https://en.wikipedia.org/wiki/Cyclomatic_complexity
- **Industry standard:** Aim for < 10

---

## Part 3: Confidence Scoring Framework

### How to Calculate Confidence Level

```
confidence = (evidence_count / maximum_possible) * 100

Where:
  evidence_count = number of findings with tool data
  maximum_possible = 10 (arbitrary baseline)
```

**MINIMUM (Evidence < 3):**
- Only tool outputs; no sources cited
- Example: 1 flake8 violation

**LOW (Evidence 3-5):**
- Tool outputs + some source references
- Example: 3 security findings + OWASP reference

**MEDIUM (Evidence 5-8):**
- Tool outputs + multiple source types (OWASP, CWE, PEP 8)
- Analysis connects findings to business impact
- Example: 6 security findings + architecture implications

**HIGH (Evidence > 8):**
- Tool outputs + comprehensive source citations
- Clear remediation paths with effort estimates
- Industry best practices cited

### Transparency

Always show the basis:
```markdown
**Confidence: MEDIUM**
- Measured via: bandit (6 findings), flake8 (4 violations)
- Sources cited: OWASP Top 10, CWE, PEP 8
- Analysis depth: Tool output interpretation + domain knowledge
```

---

## Part 4: Report Structure (Phase 4 Template)

### Section 1: Executive Summary
- **What:** High-level overview of findings
- **Length:** 3-5 sentences
- **Tone:** Business-focused, not technical jargon
- **Example:** "Analysis identified 6 security concerns and 4 code quality issues. The primary concern is hardcoded credentials in configuration (HIGH severity). Estimated remediation time: 2-3 hours."

### Section 2: Security Findings
- **Structure:** Group by severity (HIGH → MEDIUM → LOW)
- **Per finding:**
  - Tool that found it (bandit, flake8)
  - Location (file:line)
  - What (description from playbook)
  - Why (CWE/OWASP reference)
  - How to fix (specific action)
  - Effort (time estimate)

### Section 3: Code Quality Issues
- **Structure:** Group by impact (maintainability, readability, complexity)
- **Per issue:**
  - Rule violated (E302, C901, etc.)
  - Location (file:line)
  - Why it matters (PEP 8 reference)
  - How to fix
  - Priority (MUST/SHOULD/NICE-TO-HAVE)

### Section 4: Remediation Roadmap
- **Structure:** Prioritized task list
- **Format:**
  ```
  1. [CRITICAL] Fix hardcoded credentials
     - Effort: 30 min
     - Impact: Blocks production deployment
     - Owner: Security team

  2. [HIGH] Refactor function X (complexity 15)
     - Effort: 2 hours
     - Impact: Improves maintainability
     - Owner: Dev team
  ```

### Section 5: Confidence Assessment
- **What:** Explain why we trust these findings
- **Show:** Evidence count, sources, analysis depth
- **Honest:** Acknowledge gaps (e.g., "no source code review performed")

---

## Part 5: When to Escalate / Flag

**Flag as HIGH PRIORITY if:**
- B105, B602, B104 found (immediate security risk)
- Multiple hardcoded credentials detected
- Debug mode enabled in production config
- Average cyclomatic complexity > 10

**Flag as MEDIUM PRIORITY if:**
- B101, B303 found (platform-specific risk)
- Code quality deteriorating (> 10 flake8 violations per file)
- Functions > 200 lines

**Flag as INFORMATIONAL if:**
- PEP 8 style violations (mostly cosmetic)
- Single complexity violation (can be fixed incrementally)

---

## Part 6: When NOT to Report (Avoid False Positives)

- **B101 in tests:** `assert` is fine in test files. Skip this warning.
- **E501 in comments:** Line length limits don't apply to URLs/documentation. Report but mark as LOW priority.
- **W503 vs W504:** Pick one style; don't report both (they conflict).
- **Commented-out code:** If it's just a few lines, don't escalate. If it's > 10 lines, flag for cleanup.

---

## Appendix: OWASP/CWE Quick Reference

| OWASP | CWE | Example | Bandit Rule |
|-------|-----|---------|-------------|
| A01:2021 - Broken Access Control | CWE-200 | 0.0.0.0 binding | B104 |
| A02:2021 - Cryptographic Failures | CWE-327 | MD5 hash | B303 |
| A03:2021 - Injection | CWE-89, CWE-78 | SQL injection, shell injection | B105, B602 |
| A05:2021 - Security Misconfiguration | CWE-215 | Debug mode on | B201 |
| A09:2021 - Broken Exception Handling | CWE-703 | assert in validation | B101 |

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Authority:** OWASP Top 10 2021, PEP 8, Bandit docs, CWE

This playbook is the "source of truth" for Phase 4 intelligent analysis.
