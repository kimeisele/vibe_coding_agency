# The Simple Motor Philosophy

## The Problem

AI produces bullshit.

Hallucinations. Confident wrong answers. Made-up citations. Speculation presented as fact.

## The Solution

**Three Non-Negotiable Rules**

### Rule 1: VERSTEHEN (Understand)

Parse the input. No assumptions.

- What does the user *actually* ask?
- What are the facts?
- What are the gaps?

**Example:**
- ✓ "User wants security audit of Python code at /app"
- ✗ "User probably wants a complete refactor and deployment guide"

### Rule 2: RECHERCHIEREN (Research)

Fetch external truth.

- Official docs
- Best practices (cited)
- Academic sources
- Industry standards

**Requirement:** Every claim must cite a source.

**Example:**
- ✓ "PEP 8 recommends max line length 79 chars" → https://pep8.org
- ✗ "Python developers prefer 80 char lines"

### Rule 3: VALIDIEREN (Validate)

Run real tools. Get real data.

- Static analysis (flake8, bandit, eslint)
- Dependency audits
- Actual test execution
- Measured metrics

**Requirement:** No speculation. Only observable facts.

**Example:**
- ✓ "flake8 found 12 style violations in app.py"
- ✗ "The code probably has style issues"

---

## How It Works

```
Input
  ↓
Phase 1: VERSTEHEN
  (Parse, no assumptions)
  ↓
Phase 2: RECHERCHIEREN
  (Get external truth)
  ↓
Phase 3: VALIDIEREN
  (Run real tools)
  ↓
Phase 4: BERICHT
  (Synthesize into report)
  ↓
Output (100% fact-based)
```

Each phase has clear inputs and outputs.
Each phase validates before proceeding.
The output is **defensible** because every claim is backed.

---

## Why This Works

1. **No hallucinations** - Can't speculate if you only use facts
2. **Verifiable** - Anyone can check your sources
3. **Scalable** - Works for tiny scripts or massive systems
4. **Auditable** - Full trail of where info came from

---

## The Golden Rule

**If you can't cite it or measure it, don't say it.**

That's it. That's the whole philosophy.

---

## Implementation

The Simple Motor implements these rules:

1. **Notebook** - One notebook, 4 phases
2. **Orchestrator** - Runs the notebook with parameters
3. **Output** - A report you can trust 100%

No complexity. No BS. Just facts.
