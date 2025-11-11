# 🤖 Sonnet Integration: Code Quality Measurement & Improvement

**Status:** Ready for external repo analysis
**Updated:** 2025-11-10
**Your Mission:** Analyze external repos using our intelligence frameworks

---

## 📦 What You're Getting

### 1. **Wiki Coding Operating System**
Complete framework for AI code quality (in `docs/vibe-coding-os/`):
- ✅ **33 atomic markdown files** - searchable, reusable, composable
- ✅ **CLEAR Framework** - Structured code review methodology
- ✅ **Vibe-Shape-Up Process** - Shape → Vibe → Audit workflow
- ✅ **Anti-patterns Catalog** - God Objects, Large Classes, Duplicates
- ✅ **Boy Scout Rule** - Leave code cleaner than you found it

### 2. **Integrated PromptRegistry**
Prompts now loaded from Wiki intelligence:
```
src/meta_audit/prompts/
├── expert_personas/
│   ├── security_analyst.json      # Security expert
│   └── refactor_gpt.json          # Code quality expert
├── audit_context/
│   ├── clear_framework.json       # Review methodology
│   └── god_object_detection.json  # Anti-pattern detection
└── workflows/
    └── vibe_shape_up.json         # Development process
```

### 3. **Test Capsule Export**
Sample: `capsule_audit_project.capsule.json`
- 50 Python files from capsule_audit
- Ready for analysis
- Shows how external repos are represented

---

## 🎯 Your Workflow

### Step 1: Understand the Frameworks

**Start here:**
```bash
# Read the Vibe Coding OS
cat docs/vibe-coding-os/README.md
cat docs/vibe-coding-os/01-diagnosis/the-antidote.md

# Understand CLEAR Framework
cat docs/vibe-coding-os/08-ai-governance/clear-framework.md
```

**Key concepts you need:**
- **Vibe Coding Paradox**: Speed (AI) vs Quality (Humans)
- **The Antidote**: Human-centric AI development
- **CLEAR Framework**: C=Context, L=Layered, E=Explicit, A=Alternative, R=Refactoring
- **Small CLs Rule**: One logical change per commit (critical!)
- **Boy Scout Rule**: Leave code cleaner than you found it

### Step 2: Get Test Capsules

For ANY external repo, create a capsule snapshot:

```bash
# Export a repo as capsule (no code left behind, JSON safe)
python3 << 'EOF'
from pathlib import Path
import json
from meta_audit.core.models import ProjectCapsule, CapsuleFile

def discover_python_files(project_path: Path):
    skip_dirs = {".venv", "venv", ".git", "__pycache__", "node_modules"}
    return sorted([
        f for f in project_path.rglob("*.py")
        if not any(part in f.parts for part in skip_dirs)
    ])

def read_file_content(file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None

# Generate capsule
project_root = Path("/path/to/repo")
files = [
    CapsuleFile(
        path=f.relative_to(project_root),
        size_bytes=len(c.encode()) if (c := read_file_content(f)) else 0,
        content=c
    )
    for f in discover_python_files(project_root)
    if (c := read_file_content(f))
]

capsule = ProjectCapsule(
    python_version="3.11",
    project_root=project_root,
    project_name=project_root.name,
    files_count=len(files),
    total_size_bytes=sum(f.size_bytes for f in files),
    files=files
)

with open(f"{project_root.name}.capsule.json", "w") as f:
    json.dump(capsule.model_dump(mode="json"), f)

print(f"✅ Capsule: {len(files)} files, {sum(f.size_bytes for f in files) / 1024 / 1024:.2f} MB")
EOF
```

### Step 3: Analyze Using the Frameworks

When you see code, ask yourself using CLEAR:

**C - Context:**
- What were the original requirements?
- What constraints are there (security, performance)?
- Are business rules documented?

**L - Layered:**
- **Structure**: Is code well-organized? (packages, modules, files)
- **Logic**: Are algorithms correct? Edge cases handled?
- **Security**: OWASP Top 10 compliance? Data protection?

**E - Explicit:**
- Can you trace the execution flow?
- What happens on error paths?
- Are there races, deadlocks, or resource leaks?

**A - Alternative:**
- Is there a better design pattern?
- Could this be simpler?
- Any premature optimization?

**R - Refactoring:**
- SRP violations (god objects)?
- Can this code be more testable?
- Does it follow Boy Scout Rule?

### Step 4: Measure Code Quality

Use the **Audit Grid Template** from wiki:
```
docs/vibe-coding-os/10-templates/audit-grid.md
```

Transform subjective "vibes" into objective metrics:
- SRP Violation? (yes/no)
- God Object Indicator? (yes/no)
- Cognitive Load: 1-7 (how hard to understand)
- Readability: 1-5
- Testability: 1-5

### Step 5: Suggest Improvements

**For each issue found:**
1. **What's wrong**: Be specific (not "bad code")
2. **Why it matters**: Business impact
3. **How to fix**: Step-by-step, using code patches
4. **Alternative approaches**: Multiple solutions
5. **Validation**: How to test the fix

---

## 📋 PromptRegistry Integration

The registry is automatically loaded with wiki prompts:

```python
from meta_audit.prompt_registry.registry import PromptRegistry
from pathlib import Path

# Load prompts (automatically from src/meta_audit/prompts/)
registry = PromptRegistry(prompts_dir=Path("src/meta_audit/prompts"))

# List available prompts
all_prompts = registry.list()  # All prompts
security = registry.list(category="expert_personas", tag="security")

# Render prompt with context
rendered = registry.render(
    "security_analyst",
    variables={"finding": "SQL injection in query builder"}
)
```

**Available Prompts:**

| ID | Category | Purpose | Variables |
|----|----------|---------|-----------|
| `security_analyst` | expert_personas | Security vulnerability analysis | finding |
| `refactor_gpt` | expert_personas | Code quality & structure | finding |
| `audit_context_clear` | audit_context | CLEAR framework context | (none) |
| `audit_context_god_object` | audit_context | God object detection | (none) |
| `workflow_vibe_shape_up` | workflows | Development process | (none) |

---

## 🔥 Critical Rules (From Wiki)

### Small CLs Rule ⭐⭐⭐
One logical change per commit. **This is critical.**
- Each commit solves ONE problem
- Easier to review
- Easier to revert if needed
- Reduces merge conflicts

See: `docs/vibe-coding-os/07-code-review/small-cls-rule.md`

### Boy Scout Rule
Always leave code cleaner than you found it.
- Fix warnings while reviewing
- Improve variable names
- Add missing tests
- Update outdated docs

See: `docs/vibe-coding-os/02-principles/boy-scout-rule.md`

### CLEAR Framework
Every code review should follow CLEAR methodology.
- Don't just check syntax
- Understand the prompt/requirement
- Think through execution
- Consider alternatives

See: `docs/vibe-coding-os/08-ai-governance/clear-framework.md`

---

## 📊 Expected Output Format

When you analyze code:

```markdown
## Code Quality Analysis

### 1. CLEAR Review Results

**C - Context:**
- Original prompt: [what was requested]
- Issues with context: [what was missing]

**L - Layered Analysis:**
- Structure: [organization, packages, cohesion]
- Logic: [correctness, edge cases]
- Security: [OWASP, data protection]

**E - Explicit Execution:**
- Flow trace: [happy path]
- Error handling: [edge cases]
- Issues found: [specific code lines]

**A - Alternatives:**
- Current approach: [what's there]
- Alternative 1: [better option]
- Alternative 2: [simpler option]

**R - Refactoring:**
- Improvements: [concrete suggestions]
- Code patches: [in JSON format]

### 2. Quality Metrics

Using Audit Grid:
- SRP Violation: [yes/no]
- God Object: [yes/no]
- Cognitive Load: [1-7]
- Readability: [1-5]
- Testability: [1-5]

### 3. Recommendations

**Priority 1 (Critical):** [what breaks things]
**Priority 2 (High):** [what causes maintenance issues]
**Priority 3 (Nice-to-have):** [what improves elegance]
```

---

## 🚀 Getting Started

1. **Understand the Wiki**
   ```bash
   cat docs/vibe-coding-os/README.md
   cat HANDOVER.md  # Previous handover from remote agent
   ```

2. **Explore the Prompts**
   ```bash
   ls -la src/meta_audit/prompts/
   cat src/meta_audit/prompts/expert_personas/security_analyst.json
   ```

3. **Test on Sample**
   - Use `capsule_audit_project.capsule.json` as test
   - Run through CLEAR analysis
   - Generate quality report

4. **Ready for External Repos**
   - Capsule any external repo
   - Apply CLEAR framework
   - Measure & suggest improvements

---

## 📚 Quick Wiki Index

| Topic | File |
|-------|------|
| **Overview** | `docs/vibe-coding-os/README.md` |
| **The Problem** | `docs/vibe-coding-os/01-diagnosis/vibe-coding-paradox.md` |
| **The Solution** | `docs/vibe-coding-os/01-diagnosis/the-antidote.md` |
| **Code Review** | `docs/vibe-coding-os/08-ai-governance/clear-framework.md` |
| **Development Process** | `docs/vibe-coding-os/06-processes/vibe-shape-up.md` |
| **Audit** | `docs/vibe-coding-os/10-templates/audit-grid.md` |
| **All Concepts** | `docs/vibe-coding-os/INDEX.md` |

---

## ✨ Success Criteria

You'll know this is working when you can:

1. ✅ Explain CLEAR framework from memory
2. ✅ Analyze code in layers (structure → logic → security)
3. ✅ Identify god objects in any codebase
4. ✅ Suggest specific, testable improvements
5. ✅ Transform qualitative "vibes" into quantitative metrics
6. ✅ Write code analysis that follows Small CL Rule

---

**Ready to measure code quality? Let's go! 🚀**

Questions? → Check `docs/vibe-coding-os/INDEX.md` first!
