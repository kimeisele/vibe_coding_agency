# 🏢 Vibe Coding Agency

**Structured Software Project Management System**

A CLI tool that orchestrates the Grand Agency Code Framework phases for professional software development.

---

## What This Does

You describe a project (or upload a chaotic codebase), and the system guides you through:

1. **INTAKE** → Extract requirements & scope
2. **ARCHITECTURE** → Design the system
3. **IMPLEMENTATION** → Plan development tasks
4. **CODE GENERATION** → Implement code
5. **QUALITY ASSURANCE** → Test & validate

For existing projects:
1. **RECOVERY** → Audit & identify issues
2. Then proceed with IMPLEMENTATION, CODE, QA

---

## Quick Start

```bash
cd vibe_coding_agency
python3 agency.py
```

The CLI will ask:
- Is this a NEW or EXISTING project?
- Project name?
- Then guide you through phases

---

## How It Works

Each phase:
- 📋 Loads a template from `Masterframework/`
- 📝 Shows instructions & guidance
- 💾 Saves your inputs to `projects/{project-name}/state.json`
- ✅ Validates before proceeding

---

## Project Structure

```
vibe_coding_agency/
├── agency.py              # Main CLI (you are here)
├── README.md              # This file
├── Masterframework/       # Templates (01-08.md)
│   ├── 01.md              # Master Framework Overview
│   ├── 02.md              # NEW PROJECT INTAKE
│   ├── 03.md              # EXISTING PROJECT RECOVERY
│   ├── 04.md              # ARCHITECTURE DESIGN
│   ├── 05.md              # IMPLEMENTATION PLAN
│   ├── 06.md              # CODE GENERATION
│   ├── 07.md              # QUALITY ASSURANCE
│   └── 08.md              # Quick Start Guide
└── projects/              # All your projects
    └── {project-name}/
        └── state.json     # Project progress & artifacts
```

---

## Example Usage

### New Project: "Task Management App"

```bash
$ python3 agency.py

🏢 VIBE CODING AGENCY
Is this a NEW project or EXISTING project?
A) NEW project
B) EXISTING project

Enter A or B: A
✓ Type: NEW PROJECT
Flow: INTAKE → ARCHITECTURE → IMPLEMENTATION → CODE → QA

Project name? task-app
✓ Project: task-app

PHASE 1: INTAKE
📋 Template: 02.md

[Shows template guidance]

Describe your project: A task management app for teams...
✓ INTAKE input recorded

Proceed to next phase? (y/n): y
```

### Existing Project: "Messy Django App"

```bash
$ python3 agency.py

Enter A or B: B
✓ Type: EXISTING PROJECT
Flow: RECOVERY → (ARCHITECTURE) → IMPLEMENTATION → CODE → QA

Project name? old-django-app
✓ Project: old-django-app

PHASE 6: RECOVERY
📋 Template: 03.md

[Shows template guidance for codebase audit]

Describe current state: We have 50 files, lots of AI-generated code...
✓ RECOVERY input recorded
```

---

## Understanding the Phases

### Phase 1: INTAKE (NEW projects)
- **Input:** Your project description
- **Output:** PROJECT_BRIEF.md, REQUIREMENTS_SPEC.md, SUCCESS_METRICS.md, CONSTRAINTS.md
- **Questions:** What's the problem? Who uses it? What's success?

### Phase 2: ARCHITECTURE
- **Input:** Requirements from Phase 1
- **Output:** SYSTEM_ARCHITECTURE.md, DATA_MODEL.md, API_SPEC.md, TECH_STACK.md
- **Questions:** How should the system be structured?

### Phase 3: IMPLEMENTATION
- **Input:** Architecture from Phase 2
- **Output:** USER_STORIES.md, TECHNICAL_TASKS.md, PROJECT_STRUCTURE.md, DEPENDENCIES.md
- **Questions:** What tasks need to be done? In what order?

### Phase 4: CODE GENERATION
- **Input:** Technical tasks from Phase 3
- **Output:** Actual code files, tests, CODE_STANDARDS.md, IMPLEMENTATION_NOTES.md
- **Questions:** Write the code following standards

### Phase 5: QUALITY ASSURANCE
- **Input:** Completed code from Phase 4
- **Output:** TEST_REPORT.md, CODE_REVIEW.md, REQUIREMENTS_VALIDATION.md, DEPLOYMENT_CHECKLIST.md, MAINTENANCE_GUIDE.md
- **Questions:** Does it work? Is it maintainable? Is it ready for production?

### Phase 6: RECOVERY (EXISTING projects only)
- **Input:** Your existing codebase
- **Output:** CODEBASE_AUDIT.md, ISSUES_INVENTORY.md, RECOVERY_PLAN.md, REFACTOR_PRIORITY.md
- **Questions:** What's wrong? What's the recovery strategy?

---

## Project State & Progress

Each project maintains a `state.json` file:

```json
{
  "project_name": "task-app",
  "project_type": "new_project",
  "created_at": "2025-11-10T22:58:00",
  "current_phase": "INTAKE",
  "completed_phases": ["INTAKE"],
  "artifacts": {
    "INTAKE": {
      "input": "A task management app for teams..."
    }
  }
}
```

This allows you to:
- Resume projects later
- Track progress
- Reference previous phase outputs

---

## Using Templates

Each phase shows the relevant template from `Masterframework/`:

- **02.md** - NEW PROJECT INTAKE - How to structure initial requirements
- **03.md** - EXISTING PROJECT RECOVERY - How to audit a chaotic codebase
- **04.md** - ARCHITECTURE DESIGN - How to design systems
- **05.md** - IMPLEMENTATION PLAN - How to break down into tasks
- **06.md** - CODE GENERATION - Code standards & patterns
- **07.md** - QUALITY ASSURANCE - Testing & validation checklists
- **08.md** - QUICK START GUIDE - How to use this all

The templates are **not** read-only prescriptions - they're **guidance documents** showing:
- What sections to fill
- What outputs to generate
- What validation criteria to check
- What questions to ask

---

## Key Features

✅ **Structured workflow** - Prevents "AI slop" and chaos
✅ **Phase-based** - Complete one phase fully before proceeding
✅ **Persistent state** - Resume projects anytime
✅ **Template guidance** - Shows what to do at each step
✅ **Flexible** - Works for NEW or EXISTING projects
✅ **Human-in-the-loop** - You control when to proceed
✅ **Artifact management** - All outputs stored together

---

## Design Principles

1. **Structure prevents chaos** - Clear phases prevent "wildwuchs"
2. **Documentation is mandatory** - Each phase produces artifacts
3. **Validation catches errors early** - Don't compound mistakes
4. **Humans decide** - AI guides, but you approve
5. **Continuity** - Each phase builds on previous work

---

## Next Steps After Creating a Project

Once you complete Phase 1 (INTAKE) or Phase 6 (RECOVERY), the system will guide you through:

1. Refine the scope with stakeholder input
2. Design the architecture based on requirements
3. Break architecture into actionable tasks
4. Generate code following standards
5. Validate everything before "shipping"

---

## Tips

- **Take your time in INTAKE/RECOVERY** - The better your initial analysis, the smoother later phases
- **Don't skip phases** - Each one builds on the previous
- **Reference templates** - They contain checklists and examples
- **Pause and think** - It's okay to pause between phases
- **Iterate** - If you discover new requirements, go back and update

---

## For Developers

The CLI is built in Python 3.7+:
- Uses only stdlib (no external dependencies)
- Phase sequence is configurable
- Templates are separate Markdown files
- Project state is JSON (portable, readable)

To extend:
- Add phases to the `Phase` enum
- Add templates to `Masterframework/`
- Modify phase logic in `execute_phase()`

---

## Questions?

Refer to the templates:
- Want to understand a phase? → Read `Masterframework/XX.md`
- Want to see what's expected? → Check the templates
- Stuck on a requirement? → Templates have examples

---

**Ready to build something structured?**

```bash
python3 agency.py
```

Let's go! 🚀
