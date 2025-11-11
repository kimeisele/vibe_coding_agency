# KDAF Tools

## Overview

This directory contains standalone tools for the KDAF (Knowledge-Driven Agency Framework) system.

---

## Tools

### `kdaf-fix` - Interactive Issue Resolution

**Purpose:** Provides a human-in-the-loop interface for reviewing and applying fixes from KDAF analysis results.

**Philosophy:**
- Analysis is automated (System 1: kdaf_orchestrator)
- **Fixes are manual** (System 2: kdaf-fix) - You decide what gets applied

**Usage:**

```bash
./kdaf-fix <issues.json>
```

**Example:**

```bash
cd /home/user/vibe_coding_agency
./tools/kdaf-fix examples/mock_outputs/security_20251111_100830.json
```

**Input Format:**

JSON file with structure:
```json
{
  "analysis_type": "security",
  "timestamp": "2025-11-11T10:08:30",
  "total_issues": 3,
  "issues": [
    {
      "id": "SEC-001",
      "severity": "critical",
      "category": "Command Injection",
      "description": "Function call with shell=True detected",
      "file_path": "core/phoenix_config/loaders.py",
      "line_number": 42,
      "code_snippet": "subprocess.run(cmd, shell=True)",
      "suggested_fix": "subprocess.run(shlex.split(cmd), shell=False)",
      "rationale": "Using shell=True creates command injection risk..."
    }
  ]
}
```

**Features:**

- ✅ **Colored Output** - Severity-based color coding (red=critical, yellow=high, etc.)
- ✅ **Interactive Prompts** - Review each fix before applying
- ✅ **Statistics** - Summary of applied/skipped issues
- ✅ **Safe** - You control what gets applied (y/n/q)

**Commands:**
- `y` - Apply this fix
- `n` - Skip this fix
- `q` - Quit (stop processing)

**Current Status:**

- ✅ JSON parsing
- ✅ Issue display
- ✅ Interactive prompts
- ✅ Statistics tracking
- ⏳ File modification (currently MOCK - shows "✓ Fix applied (MOCK)")

**Roadmap:**

1. Implement actual file modification logic
2. Add backup creation before modifying files
3. Add `--dry-run` mode (show what would change)
4. Add `--auto-apply` mode for CI/CD
5. Add rollback functionality

---

## Architecture

### Decoupling

`kdaf-fix` is **completely independent** from the orchestrator:

```
┌─────────────────────┐
│  System 1:          │
│  kdaf_orchestrator  │──┐
│                     │  │
│  Generates JSON     │  │  JSON Files
└─────────────────────┘  │  (Contract)
                         │
                         ↓
                    ┌─────────┐
                    │ .json   │
                    └─────────┘
                         │
                         ↓
┌─────────────────────┐  │
│  System 2:          │  │
│  kdaf-fix           │←─┘
│                     │
│  Consumes JSON      │
└─────────────────────┘
```

**Benefits:**
- Each system can be tested independently
- JSON is the clear interface contract
- Tools can be swapped/replaced
- No circular dependencies

---

## Testing

### With Mock Data

```bash
# Test with security issues
./tools/kdaf-fix examples/mock_outputs/security_20251111_100830.json

# Test with AI slop issues
./tools/kdaf-fix examples/mock_outputs/ai_slop_20251111_100831.json
```

### With Real Data (once System 1 is built)

```bash
# Run orchestrator
python ai_slop_agency/shared/kdaf_orchestrator.py

# Fix the issues it found
./tools/kdaf-fix kdaf_projects/my_project/03_validation_results/security_*.json
```

---

## Design Decisions

### Why CLI instead of Jupyter Notebook?

**Advantages:**
- ✅ Works anywhere (no Jupyter dependency)
- ✅ Scriptable (can be automated)
- ✅ Fast to build (~150 lines)
- ✅ Testable (unit tests easy to write)

**The Notebook can come later** as a "premium feature" for bulk operations.

### Why Mock File Modification?

The prototype focuses on:
1. **JSON parsing** ✅
2. **User interaction** ✅
3. **Workflow validation** ✅

File modification is **Phase 2** because it requires:
- Exact line matching logic
- Backup/rollback system
- Error handling for file I/O
- Testing on real codebases

Separating concerns = faster iteration.

---

## Contributing

To add a new tool:

1. Create executable in `tools/`
2. Add documentation here
3. Add example data in `examples/`
4. Update main README

---

**Last Updated:** 2025-11-11
