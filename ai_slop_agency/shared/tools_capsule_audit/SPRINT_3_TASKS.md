# Sprint 3: Capsule System & Multi-Project Management (Säule C)

**Duration:** 1-2 weeks

**Goal:** Implement batch processing and multi-project management via ProjectCapsule system

**Current State:** Single-project analysis (`--path .`); collectors work on live file system

**Desired State:** Batch analysis of project capsules (`--path ./capsules/`); offline project snapshots; corpus-level reporting

---

## Strategic Goal: From Single to Multi-Project

**Why we're doing this:**
- Real-world audits analyze *multiple* projects in parallel
- Offline snapshots enable asynchronous processing and team collaboration
- Corpus-level analysis enables cross-project pattern detection
- Prepares for Phase 5 (Multi-Agent Orchestration)

**Implementation Priority:**
1. **ProjectCapsule Snapshot System** - Create JSON snapshots of projects
2. **Batch Processor** - Load and analyze multiple capsules
3. **CorpusAnalysisReport** - Aggregate findings across projects
4. **Cross-Project Prep** - Structure for Phase 4/5 analysis

---

## Task 3.1: Implement `capsule create` Command

**Files:**
- `src/meta_audit/cli/commands/capsule.py` (NEW)
- `src/meta_audit/core/models.py` (Update ProjectCapsule)

**What:** Create CLI command to snapshot a project into a `ProjectCapsule` JSON file.

**Action:**

```bash
# Usage example:
meta-audit capsule create /path/to/project --output-file my_project.capsule.json
```

**Implementation Details:**

1. **ProjectCapsule Structure** (already exists in models.py):
   - Project name, path, description
   - List of all Python file contents
   - File structure/tree
   - Metadata: timestamp, capsule version

2. **capsule.py command:**
   ```python
   @click.command()
   @click.argument("project_path", type=click.Path(exists=True))
   @click.option("--output-file", default="capsule.json", help="Output capsule filename")
   @click.option("--verbose", is_flag=True, help="Enable verbose logging")
   def create(project_path: str, output_file: str, verbose: bool):
       """
       Create a ProjectCapsule snapshot of a project.

       Scans the project, collects all .py file contents, and exports as JSON.
       Capsule files can be analyzed offline later.
       """
       # 1. Walk project tree
       # 2. Collect Python files with content
       # 3. Create ProjectCapsule object
       # 4. Export to JSON
       # 5. Success message with file size
   ```

3. **Features:**
   - Recursively finds all `.py` files
   - Reads file contents (with encoding error handling)
   - Skips `.venv`, `venv`, `.git`, `__pycache__`, `node_modules`
   - Creates timestamp for capsule
   - Exports as JSON with proper serialization

**Tests:**
- [ ] Capsule creation succeeds for sample project
- [ ] JSON is valid and can be loaded
- [ ] ProjectCapsule Pydantic validation passes
- [ ] File contents are correctly embedded
- [ ] Skips virtual environments and git directories

**Success Criteria:**
- `meta-audit capsule create /my/project --output-file project.capsule.json` creates valid JSON
- File is loadable as ProjectCapsule via Pydantic

---

## Task 3.2: Update `analyze` Command for Corpus Mode

**Files:**
- `src/meta_audit/cli/commands/analyze.py` (Update)
- `src/meta_audit/analyzers/batch_processor.py` (NEW)

**What:** Extend `analyze` command to support both single-project and corpus (batch) modes.

**Current:**
```bash
meta-audit analyze --path /my/project
```

**New Capability:**
```bash
# Single project (as before)
meta-audit analyze --path /my/project

# Corpus mode (new)
meta-audit analyze --path /my/capsules/ --corpus
meta-audit analyze --capsule project1.capsule.json --capsule project2.capsule.json
```

**Implementation Details:**

1. **Mode Detection:**
   - If `--path` points to directory with `*.capsule.json` files AND `--corpus` flag: use batch mode
   - Otherwise: use single-project mode (existing behavior)

2. **Batch Processor** (`batch_processor.py`):
   ```python
   class BatchProcessor:
       """Load and analyze multiple ProjectCapsule files."""

       @staticmethod
       def discover_capsules(path: str) -> List[Path]:
           """Find all *.capsule.json files in directory."""

       @staticmethod
       def load_capsule(capsule_path: str) -> ProjectCapsule:
           """Load ProjectCapsule from JSON."""

       @staticmethod
       def analyze_capsule(capsule: ProjectCapsule) -> Dict[str, Any]:
           """
           Run all collectors on a capsule's file contents.

           Instead of run_all_collectors(path), work with ProjectCapsule data.
           """
   ```

3. **Modified `analyze.py`:**
   ```python
   @click.command()
   @click.option("--path", default=".", help="Project path or capsule directory")
   @click.option("--capsule", multiple=True, help="Specific capsule files to analyze")
   @click.option("--corpus", is_flag=True, help="Treat path as directory of capsules")
   @click.option("--format", type=click.Choice(["json", "table"]), default="table")
   @click.option("--output-file", default=None)
   @click.option("--verbose", is_flag=True)
   def analyze(path, capsule, corpus, format, output_file, verbose):
       if capsule:
           # Explicit capsule list mode
           capsules = [ProjectCapsule.load(c) for c in capsule]
       elif corpus:
           # Corpus directory mode
           capsules = BatchProcessor.discover_capsules(path)
       else:
           # Single project mode (existing)
           run_single_project_analysis(path, ...)
   ```

**Tests:**
- [ ] Single-project mode still works
- [ ] Corpus mode discovers capsules
- [ ] Specific `--capsule` flags load correct files
- [ ] Batch processing maintains file isolation

**Success Criteria:**
- `meta-audit analyze --path ./capsules --corpus` loads and analyzes all capsules
- Results are aggregated without cross-contamination

---

## Task 3.3: Batch Processing & Report Aggregation

**Files:**
- `src/meta_audit/generators/corpus_report.py` (NEW)
- Update `src/meta_audit/generators/report.py` for corpus support

**What:** Create CorpusAnalysisReport to aggregate findings from multiple projects.

**Implementation Details:**

1. **CorpusAnalysisReport Class:**
   ```python
   class CorpusAnalysisReport:
       """Aggregated report for multiple ProjectCapsule analyses."""

       capsule_reports: Dict[str, Report]  # project_name → Report
       summary: Dict[str, int]  # Aggregated severity counts

       def __init__(self, reports: Dict[str, Report], execution_time: float):
           """Aggregate multiple reports."""

       @property
       def all_findings(self) -> List[AnalysisResult]:
           """Flatten all findings from all capsules."""

       def to_json(self) -> str:
           """Export corpus report as JSON."""

       def to_terminal(self) -> str:
           """Export corpus report as Rich table with per-project sections."""
   ```

2. **Aggregation Logic:**
   - For each capsule analyzed, store its Report
   - Flatten all findings from all capsules
   - Calculate corpus-level summary:
     ```python
     {
         "CRITICAL": total_critical,
         "HIGH": total_high,
         "MEDIUM": total_medium,
         "LOW": total_low,
         "TOTAL": total_findings,
         "projects_analyzed": N,
         "project_summaries": {
             "project_name": {"CRITICAL": 0, "HIGH": 2, ...},
             ...
         }
     }
     ```

3. **JSON Export Format:**
   ```json
   {
       "summary": {
           "CRITICAL": 0,
           "HIGH": 5,
           "MEDIUM": 23,
           "LOW": 120,
           "TOTAL": 148,
           "projects_analyzed": 3
       },
       "project_summaries": {
           "project_a": {"CRITICAL": 0, "HIGH": 2, "MEDIUM": 10, "LOW": 50, "TOTAL": 62},
           "project_b": {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 8, "LOW": 40, "TOTAL": 49},
           "project_c": {"CRITICAL": 0, "HIGH": 2, "MEDIUM": 5, "LOW": 30, "TOTAL": 37}
       },
       "findings": [
           {
               "project": "project_a",
               "analyzer": "security_analyzer",
               "file": "main.py",
               "line": 42,
               "severity": "HIGH",
               ...
           },
           ...
       ],
       "execution_time": 12.5,
       "timestamp": "2025-11-10T..."
   }
   ```

4. **Terminal Output Format:**
   ```
   Meta-Audit Corpus Report (3 Projects)
   ====================================================================

   Overall Summary:
   Critical:   0 | High:   5 | Medium:  23 | Low: 120 | Total: 148

   Per-Project Breakdown:

   📦 project_a (62 findings)
   ├─ Critical:  0 | High: 2 | Medium: 10 | Low: 50
   ├─ Execution: 3.5s
   └─ Top Issues:
   │  ├─ HIGH: Hardcoded password in main.py:42
   │  └─ MEDIUM: Complex function process_data at line 88

   📦 project_b (49 findings)
   ├─ Critical:  0 | High: 1 | Medium:  8 | Low: 40
   ├─ Execution: 2.8s
   └─ Top Issues:
   │  └─ HIGH: SQL injection risk in db.py:15

   📦 project_c (37 findings)
   ├─ Critical:  0 | High: 2 | Medium:  5 | Low: 30
   ├─ Execution: 5.2s
   └─ Top Issues:
   │  ├─ HIGH: Insecure random in utils.py:23
   │  └─ MEDIUM: Generic variable names in helpers.py
   ```

**Tests:**
- [ ] CorpusAnalysisReport aggregates correctly
- [ ] Summary counts are accurate
- [ ] JSON export is valid
- [ ] Terminal output shows per-project breakdown
- [ ] Findings are properly attributed to projects

**Success Criteria:**
- 3+ capsules analyzed produce correct corpus summary
- JSON and terminal exports both available
- Per-project metrics preserved

---

## Task 3.4: Cross-Project Pattern Preparation

**Files:**
- `src/meta_audit/core/models.py` (Update CorpusAnalysisReport model)
- `src/meta_audit/generators/corpus_report.py` (Add cross_project_patterns field)

**What:** Prepare data structures for cross-project analysis (Phase 4/5 will implement the logic).

**Implementation Details:**

1. **Add to CorpusAnalysisReport:**
   ```python
   @dataclass
   class CrossProjectPattern:
       """Pattern observed across multiple projects."""
       pattern_type: str  # "duplicate_issue", "similar_vulnerability", etc.
       projects: List[str]  # Which projects have this pattern
       count: int  # How many times across projects
       severity: Severity  # Aggregated severity
       example_findings: List[AnalysisResult]  # Sample from each project

   class CorpusAnalysisReport:
       # ... existing fields ...
       cross_project_patterns: List[CrossProjectPattern] = []  # Empty for now
   ```

2. **Detection Framework** (structure only, no implementation):
   ```python
   class CrossProjectAnalyzer:
       """Detect patterns across multiple projects."""

       @staticmethod
       def detect_duplicate_issues(reports: Dict[str, Report]) -> List[CrossProjectPattern]:
           """
           Find same issue (same message/type) across projects.

           Implementation in Phase 4/5.
           Currently returns empty list.
           """
           return []

       @staticmethod
       def detect_vulnerability_patterns(reports: Dict[str, Report]) -> List[CrossProjectPattern]:
           """
           Find similar vulnerabilities (different code, same root cause).

           Implementation in Phase 4/5.
           Currently returns empty list.
           """
           return []

       @staticmethod
       def detect_code_quality_trends(reports: Dict[str, Report]) -> List[CrossProjectPattern]:
           """
           Analyze code quality metrics across projects.

           Implementation in Phase 4/5.
           Currently returns empty list.
           """
           return []
   ```

3. **JSON Export Includes:**
   ```json
   {
       "summary": {...},
       "project_summaries": {...},
       "findings": [...],
       "cross_project_patterns": [
           {
               "pattern_type": "duplicate_issue",
               "projects": ["project_a", "project_b"],
               "count": 2,
               "severity": "HIGH",
               "description": "Same hardcoded password pattern found in 2 projects"
           }
       ],
       "execution_time": 12.5,
       "timestamp": "2025-11-10T..."
   }
   ```

**Tests:**
- [ ] cross_project_patterns field exists in CorpusAnalysisReport
- [ ] JSON export includes cross_project_patterns (empty list for now)
- [ ] Framework structure is in place for Phase 4/5 implementation

**Success Criteria:**
- CorpusAnalysisReport has cross_project_patterns field
- Framework ready for Phase 4/5 to fill in detection logic
- No errors when exporting corpus reports

---

## Task 3.5: Unit Tests for Capsule System

**File:** `tests/unit/test_capsule_system.py` (NEW)

**What:** Test capsule creation, loading, and batch processing.

**Test Structure:**
```python
class TestCapsuleCreate:
    """Tests for capsule create command."""
    def test_capsule_creation_succeeds()
    def test_capsule_json_is_valid()
    def test_capsule_contains_all_python_files()
    def test_capsule_skips_virtual_environments()

class TestBatchProcessor:
    """Tests for batch processing."""
    def test_discover_capsules_finds_files()
    def test_load_capsule_deserializes_correctly()
    def test_analyze_capsule_returns_findings()

class TestCorpusReport:
    """Tests for corpus reporting."""
    def test_corpus_report_aggregates_correctly()
    def test_corpus_json_export_valid()
    def test_corpus_terminal_output_formatted()
```

**Tests:**
- [ ] 15+ unit tests for capsule system

**Success Criteria:**
- All unit tests pass
- Capsule system is tested end-to-end

---

## Task 3.6: Integration Tests for Batch Workflow

**File:** `tests/integration/test_phase3_corpus.py` (NEW)

**What:** Test complete batch analysis workflow.

**Test Scenarios:**
1. Create 3 sample project capsules
2. Discover capsules in directory
3. Analyze all capsules in batch
4. Generate corpus report
5. Export to JSON and terminal
6. Verify cross-project data structures

**Tests:**
- [ ] 10+ integration tests for batch workflow

**Success Criteria:**
- End-to-end corpus analysis works
- Reports aggregate correctly
- No data loss across batch

---

## Task 3.7: Update CLI Structure

**File:** `src/meta_audit/cli/main.py`

**What:** Add `capsule` command group to CLI.

**New CLI Structure:**
```
meta-audit
├─ analyze (updated for corpus mode)
├─ capsule (NEW)
│  ├─ create   (create snapshot)
│  ├─ list     (list available capsules)
│  └─ show     (inspect capsule contents)
└─ config
   └─ show
```

**Success Criteria:**
- `meta-audit --help` shows capsule commands
- `meta-audit capsule create` works
- `meta-audit analyze --corpus` works

---

## Task 3.8: Commit & Documentation

**What:** Commit all Sprint 3 changes and update roadmaps.

**Actions:**
```bash
git add src/meta_audit/cli/commands/capsule.py \
        src/meta_audit/analyzers/batch_processor.py \
        src/meta_audit/generators/corpus_report.py \
        tests/unit/test_capsule_system.py \
        tests/integration/test_phase3_corpus.py

git commit -m "feat: Implement Capsule System & Multi-Project Management (Sprint 3)

Capsule System:
- New 'capsule create' command to snapshot projects as JSON
- ProjectCapsule model with file contents and metadata
- Batch processor for analyzing multiple capsules

Multi-Project Analysis:
- Updated 'analyze' command with --corpus and --capsule flags
- CorpusAnalysisReport aggregating findings from all projects
- Per-project metrics preserved in corpus report

Cross-Project Framework:
- CrossProjectPattern data structure (detection logic in Phase 4/5)
- JSON and terminal exports with cross-project fields
- Ready for Phase 5 multi-agent orchestration

Testing:
- 15+ unit tests for capsule system
- 10+ integration tests for batch workflow
- All 25+ tests passing

Säule C complete. MVP ready for Phase 4 (Core Hardening).
```

---

## Acceptance Criteria

- [ ] `capsule create` command works
- [ ] `analyze --corpus` mode works
- [ ] CorpusAnalysisReport aggregates correctly
- [ ] JSON export valid
- [ ] Terminal output formatted
- [ ] Cross-project framework in place
- [ ] Unit tests: 15+/15+ PASS
- [ ] Integration tests: 10+/10+ PASS
- [ ] CLI structure updated
- [ ] All changes committed

---

## Success Output (Example)

When you run:
```bash
meta-audit analyze --path ./my_capsules --corpus --format json --output-file corpus_report.json
```

Output:
```
Phase 1: Discovering capsules in ./my_capsules...
  Found 3 capsules:
  ✓ project_a.capsule.json (1000 files)
  ✓ project_b.capsule.json (800 files)
  ✓ project_c.capsule.json (600 files)

Phase 2: Analyzing all capsules (parallel)...
  ✓ project_a analyzed (3.5s, 62 findings)
  ✓ project_b analyzed (2.8s, 49 findings)
  ✓ project_c analyzed (5.2s, 37 findings)

Phase 3: Generating corpus report...
  ✓ Summary aggregated
  ✓ Cross-project patterns prepared
  ✓ Report saved to corpus_report.json

Corpus Report:
============================================================
Critical:   0 | High:   5 | Medium:  23 | Low: 120 | Total: 148
Projects: 3 | Execution: 11.5s
```

And `corpus_report.json` contains structured data with all findings, per-project metrics, and cross-project pattern placeholders.

---

## Next: Phase 4 (Core Hardening)

Once Sprint 3 is complete:
- MVP is **fully functional** ✅
- Phase 4 focus: Token Transparency, Provider Flexibility, SLO Definition
- Phase 5 focus: Multi-Agent Framework, Cross-Project Analysis

See `POST_MVP_ROADMAP.md` for details.
