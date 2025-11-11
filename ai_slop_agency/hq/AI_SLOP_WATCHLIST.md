# AI Slop Watchlist

**Purpose:** Measurable definition of "Dreck" (AI-generated low-quality code) that can be used by meta-audit.

## Categories

### 1. Hardcoded Values
**Pattern:** Hardcoded credentials, IPs, paths, or configuration values
**Examples:**
- `password = "secret123"`
- `host = "0.0.0.0"`
- `path = "/tmp/hardcoded"`

**Detection:** Bandit security checks (B104, B108)
**Severity:** HIGH

### 2. Empty Exception Handlers
**Pattern:** Try-except with pass or empty handler
**Examples:**
```python
try:
    risky_operation()
except:
    pass  # AI slop
```

**Detection:** Bandit B110
**Severity:** MEDIUM

### 3. Shell=True in Subprocess
**Pattern:** Using shell=True without input validation
**Examples:**
```python
subprocess.run(cmd, shell=True)  # Dangerous
```

**Detection:** Bandit B604
**Severity:** CRITICAL

### 4. Assert in Production Code
**Pattern:** Using assert for validation (removed in optimized bytecode)
**Examples:**
```python
assert user.is_authenticated  # Will be removed with -O
```

**Detection:** Bandit B101
**False Positive:** Acceptable in tests/
**Severity:** MEDIUM

### 5. God Objects
**Pattern:** Classes/modules with excessive complexity
**Metrics:**
- Lines of code > 500
- Cyclomatic complexity > 20
- Methods > 30

**Detection:** Radon complexity + meta-audit god_object
**Severity:** HIGH

## Usage

This watchlist can be used with meta-audit:
```bash
python run_real_audit.py --target agency-toolkit
python triage_smart.py examples/real_audit_output/security_*.json
```

## Evolution

This watchlist will grow as we identify new patterns. Each pattern must be:
1. Measurable (detected by tools)
2. Actionable (can be fixed)
3. Documented (examples provided)

**Last Updated:** 2025-11-11