# KDAF Orchestrator - The Brain of Vibe Coding Agency

**Version**: 1.0
**Status**: ✅ Working (Phase 1-3 Complete)
**Last Updated**: 2025-11-11

---

## What Is This?

The **KDAF Orchestrator** is the executable implementation of the Knowledge-Driven Agency Framework (KDAF).

It transforms the KDAF **philosophy** (documented in `/hq/01_playbooks/`) into a **runnable system** that:

```
Client Input (unstructured, ambiguous)
    ↓
PHASE 1: VERSTEHEN (Semantic Understanding)
  - Extract facts, not assumptions
  - Identify knowledge gaps
  - Generate pre-research questions
    ↓
PHASE 2: RECHERCHIEREN (Knowledge Acquisition)
  - Research from external sources (official docs, best practices, case studies)
  - Build ground truth backed by citations
    ↓
PHASE 3: VALIDIEREN (Data-Driven Validation)
  - Call Meta-Audit: Run code quality tools (flake8, bandit, radon, complexity)
  - Call Agency-Toolkit: Generate final report
  - Store raw tool outputs for audit trail
    ↓
Final Report (verified, cited, backed by data)
```

---

## The Three Phases Explained

### Phase 1: VERSTEHEN (Semantic Understanding)

**Goal**: Transform ambiguous input into structured, verifiable scope

**What It Does**:
- Classifies request type (audit/build/refactor/investigation)
- Extracts objective facts (NO assumptions)
- Identifies knowledge gaps
- Generates pre-research questions
- Defines validation method

**Output**: `01_input_analysis.json`

### Phase 2: RECHERCHIEREN (Knowledge Acquisition)

**Goal**: Build ground truth from external sources

**What It Does**:
- Creates research findings with sources
- Requires 3+ citations for best practices
- Links to official documentation
- Defines validation tools

**Output**: `02_research_findings.json`

### Phase 3: VALIDIEREN (Data-Driven Validation)

**Goal**: Prove claims with tool outputs (not opinions)

**What It Does**:
1. **Calls Meta-Audit** (`run_all_collectors()`)
   - Runs: complexity, security, ai_slop, god_object analyzers
   - Generates findings

2. **Calls Agency-Toolkit** (professional report generation)
   - Converts findings to BriefingData model
   - Generates Markdown report (always)
   - Generates PDF report (if fpdf installed)
   - Uses Agency-Toolkit's templates for professional formatting

3. **Stores Everything** (Complete Audit Trail)
   - Raw tool outputs in `tool_outputs/` (unmodified)
   - JSON results in `03_validation_results.json` (structured)
   - Markdown report via Agency-Toolkit
   - PDF report via Agency-Toolkit (if available)

**Output**:
- `02_validation_and_reports/tool_outputs/` (raw Meta-Audit data)
- `03_validation_results.json` (structured Phase 3 results)
- `03_deliverables/briefing_*.md` (Agency-Toolkit Markdown)
- `03_deliverables/briefing_*.pdf` (Agency-Toolkit PDF, if fpdf available)

---

## Usage

### Basic Usage

```python
from kdaf_orchestrator import KDAFOrchestrator

# Initialize
orchestrator = KDAFOrchestrator()

# Run complete workflow
result = orchestrator.run_full_workflow(
    client_input="Our Django app is slow and hard to maintain",
    project_name="django_audit"
)

print(f"Project: {result['project_path']}")
print(f"Phase 1: {len(result['phase_1']['facts'])} facts, {len(result['phase_1']['knowledge_gaps'])} gaps")
print(f"Phase 2: {len(result['phase_2']['research_findings'])} findings")
print(f"Phase 3: {len(result['phase_3']['validation_results'])} validations")
```

### Individual Phase Control

```python
orchestrator = KDAFOrchestrator()

# Create project
orchestrator.create_project("my_project")

# Phase 1
p1 = orchestrator.phase_1_verstehen("Client request here")

# Phase 2
p2 = orchestrator.phase_2_recherchieren()

# Phase 3 (with custom target path)
p3 = orchestrator.phase_3_validieren(
    target_path="/path/to/code"
)
```

---

## Project Structure

When you run a workflow, this is created:

```
kdaf_projects/
├── project_name/
│   ├── 00_scoping_and_research/
│   │   ├── 01_input_analysis.json          (Phase 1 output)
│   │   └── 02_research_findings.json        (Phase 2 output)
│   ├── 01_development/                      (your code goes here)
│   ├── 02_validation_and_reports/
│   │   ├── tool_outputs/                    (raw Meta-Audit data)
│   │   │   ├── complexity_*.json
│   │   │   ├── security_*.json
│   │   │   ├── ai_slop_*.json
│   │   │   └── god_object_*.json
│   │   ├── written_analysis/                (human analysis)
│   │   └── 03_validation_results.json       (Phase 3 output)
│   └── 03_deliverables/
│       └── FINDINGS_REPORT.md               (final report)
```

---

## Example Output

### Phase 1 Output: `01_input_analysis.json`

```json
{
  "project_type": "investigation",
  "facts": [
    {"category": "technology", "statement": "Django framework", "is_assumption": false},
    {"category": "requirement", "statement": "Performance issue reported", "is_assumption": false}
  ],
  "knowledge_gaps": [
    {
      "gap_type": "technical",
      "description": "What is the exact technology stack and versions?",
      "research_questions": ["What versions are in use?", "What are current configurations?"]
    }
  ],
  "validation_method": "Tool outputs (flake8, bandit, radon, cProfile) + External sources",
  "timestamp": "2025-11-11T10:02:11.131886"
}
```

### Phase 3 Output: `03_validation_results.json`

```json
{
  "validation_results": [
    {
      "tool_name": "ai_slop",
      "tool_output_path": "02_validation_and_reports/tool_outputs/ai_slop_*.json",
      "findings": ["Found 282 issue(s)"],
      "confidence": "HIGH"
    },
    {
      "tool_name": "security",
      "tool_output_path": "02_validation_and_reports/tool_outputs/security_*.json",
      "findings": ["Found 3 issue(s)"],
      "confidence": "HIGH"
    }
  ],
  "analysis": {
    "ai_slop": "Found 282 issue(s) via ai_slop",
    "security": "Found 3 issue(s) via security"
  },
  "recommendations": [
    "Review security findings...",
    "Review AI-generated code patterns..."
  ],
  "confidence": "HIGH",
  "final_report_path": "03_deliverables/FINDINGS_REPORT.md"
}
```

### Phase 3 Output: `FINDINGS_REPORT.md`

```markdown
# Project Analysis Report

Generated: 2025-11-11T10:02:11.773900

## Summary

**Total Findings**: 288
**Status**: success

## Findings by Category

- **ai_slop**: 282 issue(s)
- **complexity**: 0 issue(s)
- **god_object**: 3 issue(s)
- **security**: 3 issue(s)

## Next Steps

1. Review detailed findings in `02_validation_and_reports/tool_outputs/`
2. Address high-priority issues first
3. Re-run analysis after fixes to track progress
```

---

## Key Design Principles

### 1. External Validation ONLY
**Rule**: No claims without TOOL OUTPUT or CITED SOURCE

- Phase 1: Facts, not assumptions
- Phase 2: Everything cited + 3+ sources for best practices
- Phase 3: Tool outputs only, no speculation

### 2. Graceful Degradation
- If Meta-Audit not installed → Uses mock data
- If Agency-Toolkit not installed → Uses fallback report
- **Always completes workflow**, never fails silently

### 3. Complete Audit Trail
- Raw tool outputs stored unmodified
- Every finding has source/tool reference
- JSON results for machine parsing
- Markdown for human reading

### 4. Structured Data Flow
- Phase 1 → Phase 2 (gaps become research topics)
- Phase 2 → Phase 3 (research informs validation plan)
- Phase 3 → Report (findings backed by tools)

---

## Integration Points

### Meta-Audit Integration ✅ LIVE
```python
from meta_audit.analyzers.collectors import run_all_collectors

# Called in Phase 3._call_meta_audit()
result = run_all_collectors(target_path)
# Returns: {
#   "collectors_data": {
#     "complexity": [...],
#     "security": [...],
#     "ai_slop": [...],
#     "god_object": [...]
#   },
#   "all_findings": [...],
#   "errors": [...],
#   "status": "success" | "partial_success"
# }
```

**Integration Details**:
- Calls `run_all_collectors(target_path)` with real code path
- Stores raw outputs in `tool_outputs/` directory
- Graceful fallback to mock data if Meta-Audit not installed
- Execution time tracked and reported

### Agency-Toolkit Integration ✅ LIVE
```python
from agency_toolkit.core.briefing.models import BriefingData
from agency_toolkit.core.briefing import generate as generate_briefing

# Called in Phase 3._call_agency_toolkit()
briefing_data = BriefingData(
    client_name="Project Analysis",
    project_name="...",
    deadline=date(...),
    objectives="Comprehensive analysis from Meta-Audit findings",
    # ... more fields
)

# Generate both Markdown and PDF
md_result = generate_briefing(briefing_data, format_type="md", output_dir=...)
pdf_result = generate_briefing(briefing_data, format_type="pdf", output_dir=...)
```

**Integration Details**:
- Converts Meta-Audit findings into BriefingData model
- Generates professional Markdown report (always)
- Generates professional PDF report (if fpdf installed)
- Reports summary → findings by category → recommendations
- Complete findings data preserved in tool_outputs/ for audit trail
- Graceful fallback to basic markdown if Agency-Toolkit not available

---

## Running Tests

### Test 1: Full Workflow with Mock Data
```bash
cd /Users/ss/projects/vibe_coding_agency/ai_slop_agency

python -c "
import sys
sys.path.insert(0, './shared')
from kdaf_orchestrator import KDAFOrchestrator

orchestrator = KDAFOrchestrator()
result = orchestrator.run_full_workflow(
    client_input='Analyze our Django application',
    project_name='test_project'
)
print(f'✓ Project: {result[\"project_path\"]}')
"
```

### Test 2: Full Workflow with Real Code
```bash
python -c "
import sys
sys.path.insert(0, '/meta-audit/src')  # Adjust path
sys.path.insert(0, './shared')
from kdaf_orchestrator import KDAFOrchestrator

orchestrator = KDAFOrchestrator()
orchestrator.create_project('real_audit')
orchestrator.phase_1_verstehen('Audit agency-toolkit')
orchestrator.phase_2_recherchieren()
orchestrator.phase_3_validieren(
    target_path='/Users/ss/projects/vibe_coding_agency/agency-toolkit/agency_toolkit'
)
"
```

---

## Future Enhancements

### Phase 2: Enhanced Research
- [ ] Integrate with web search for current best practices
- [ ] Automatic source validation (is URL still valid?)
- [ ] Confidence scoring based on source quality
- [ ] LLM-powered research suggestion (what to research based on Phase 1)

### Phase 3: Enhanced Validation
- [x] ✅ Call Agency-Toolkit's full report generator (LIVE)
- [ ] Integration with performance profilers (cProfile)
- [ ] Custom tool definitions per project type
- [ ] LLM-powered finding synthesis (Phase 5 of meta-audit)
- [ ] Executive summary generation with confidence levels

### Integration & Operations
- [ ] CLI wrapper for easy usage (`vibe kdaf --help`)
- [ ] Web API endpoint for remote agents
- [ ] Scheduled workflows for continuous analysis
- [ ] Machine-readable summaries for dashboards
- [ ] Project history tracking & comparison
- [ ] Team collaboration features (comments on findings)

---

## Philosophy

**KDAF Orchestrator proves that AI-driven consulting can be**:
- ✅ **Reliable**: Every claim backed by tools or sources
- ✅ **Verifiable**: Full audit trail of where info came from
- ✅ **Scalable**: Automated Phase 1-3 with human oversight
- ✅ **Accountable**: Confidence levels tied to evidence quality

---

## Files

- `kdaf_orchestrator.py` - The main orchestrator class
- `README_KDAF_ORCHESTRATOR.md` - This file
- `../hq/01_playbooks/` - KDAF Philosophy & Protocols
- `../hq/02_knowledge_base/` - Cumulative knowledge base

---

**The KDAF Orchestrator is the executable brain of Vibe Coding Agency. It proves that AI can be both fast AND reliable through systematic methodology, external validation, and complete transparency.**
