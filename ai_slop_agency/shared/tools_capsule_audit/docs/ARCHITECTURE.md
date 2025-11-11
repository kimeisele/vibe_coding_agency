# Meta-Audit Architecture

**High-level overview of the system design and data flow.**

---

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│  - Project path: /my/project or capsule files              │
│  - Mode: single | corpus                                    │
│  - Format: json | table                                     │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ↓
         ┌─────────────────────┐
         │   Phase 1: Collect  │  (100% data-driven, no LLM)
         └──────────┬──────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ↓             ↓             ↓
   Radon        Bandit        AI-Slop
   (Metrics)  (Security)    (Patterns)
      │             │             │
      └─────────────┼─────────────┘
                    │
                    ↓
     ┌──────────────────────────────┐
     │   AnalysisResult Objects     │
     │  (severity, category, conf)  │
     └──────────────┬───────────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
       ↓                         ↓
  Single Project           Multiple Projects
  (1 project)             (Corpus, 2+ projects)
       │                         │
       └────┬────────────────────┘
            │
            ↓
 ┌──────────────────────────────┐
 │     Phase 2: Aggregate       │
 │  - Report (single project)   │
 │  - CorpusReport (multi)      │
 │  - CrossProjectPatterns      │
 └──────────────┬───────────────┘
                │
       ┌────────┴────────┐
       │                 │
       ↓                 ↓
    JSON            Terminal
   Output           Output
       │                 │
       └────────┬────────┘
                │
    ┌───────────┴─────────────┐
    │   Optional Phase 3:     │
    │   LLM Enhancement      │
    │ (Single project only)  │
    └───────────┬─────────────┘
                │
                ↓
         ┌─────────────────┐
         │  Final Report   │
         │   + LLM Insights│
         └─────────────────┘
```

---

## Data Model

### AnalysisResult (Core Finding)
```python
class AnalysisResult(BaseModel):
    analyzer_name: str          # "bandit", "radon", "ai_slop"
    file_path: Path             # Where the issue is
    line_start: Optional[int]   # Start line number
    line_end: Optional[int]     # End line number
    pattern_type: str           # "sql_injection", "high_complexity"
    severity: Severity          # CRITICAL | HIGH | MEDIUM | LOW
    category: AnalysisCategory  # SECURITY | CODE_STRUCTURE | PERFORMANCE
    confidence: float           # 0.0 to 1.0 (trust level)
    message: str                # Human-readable description
    evidence: Dict[str, Any]    # Original data from collector
    remediation: List[str]      # Suggested fixes
    project_name: Optional[str] # For corpus analysis
```

### Report (Single Project)
```python
class Report(BaseModel):
    findings: List[AnalysisResult]
    summary: {                  # Aggregated counts
        "CRITICAL": int,
        "HIGH": int,
        "MEDIUM": int,
        "LOW": int,
        "TOTAL": int
    }
    execution_time: float
    timestamp: str
```

### CorpusAnalysisReport (Multiple Projects)
```python
class CorpusAnalysisReport(BaseModel):
    project_reports: Dict[str, Report]      # Report per project
    all_findings: List[AnalysisResult]      # Flattened findings
    cross_project_patterns: List[CrossProjectPattern]
    summary: {
        "projects_analyzed": int,
        "CRITICAL": int,
        "HIGH": int,
        ...
        "project_summaries": {
            "project_a": {...},
            "project_b": {...}
        }
    }
    execution_time: float
    timestamp: str
```

### CrossProjectPattern
```python
class CrossProjectPattern(BaseModel):
    pattern_type: str               # "duplicate_issue", "sql_injection", etc
    severity: Severity
    category: AnalysisCategory
    projects_count: int             # How many projects affected
    projects: List[str]             # Which projects
    message: str                    # Description
    projects_confidence: float      # Average confidence
    evidence: Dict[str, Any]        # Aggregated data
```

### ProjectCapsule (Snapshot)
```python
class ProjectCapsule(BaseModel):
    version: int                    # Version 2 (current)
    created_at: datetime
    python_version: str             # e.g., "3.11"
    project_root: Path
    project_name: str
    files_count: int
    total_size_bytes: int
    files: List[CapsuleFile]        # Actual file contents
    capsule_mode: str               # "hotspot" | "signature" | "full"
```

---

## Module Structure

```
src/meta_audit/
├── core/
│   └── models.py                    # Pydantic models (data contracts)
│
├── analyzers/
│   ├── collectors/                  # Phase 1 (static analysis)
│   │   ├── complexity.py            # Radon integration
│   │   ├── security.py              # Bandit integration
│   │   ├── ai_slop.py               # Pattern detection
│   │   └── __init__.py              # Collector registry
│   │
│   ├── batch_processor.py           # Parallel corpus processing
│   └── cross_project_analyzer.py    # Cross-project patterns (Phase 4)
│
├── generators/
│   ├── report.py                    # Single project reports
│   ├── corpus_report.py             # Multi-project reports
│   └── __init__.py
│
├── agents/                          # Phase 3 (optional LLM)
│   ├── audit_agent.py               # Orchestrator
│   └── planning.py                  # Prompt planning
│
├── providers/                       # LLM providers
│   ├── base.py                      # Abstract base
│   ├── google_provider.py
│   └── provider_loader.py
│
├── phoenix_config/                  # Configuration system
├── prompt_registry/                 # Persona prompts
│
└── cli/
    └── commands/
        ├── analyze.py               # Main analysis command
        ├── capsule.py               # Capsule management
        └── main.py                  # CLI entry point
```

---

## Data Flow: Single Project

```
1. USER INPUT
   └─ meta-audit analyze --path /project

2. DISCOVERY
   ├─ Discover Python files
   └─ Filter: skip .venv, .git, __pycache__

3. PHASE 1: COLLECTION (Parallel)
   ├─ Radon
   │  └─ Extract complexity metrics
   ├─ Bandit (parallel)
   │  └─ Find security vulnerabilities
   └─ AI-Slop (parallel)
      └─ Detect generated code patterns

4. AGGREGATION
   ├─ Combine all findings → List[AnalysisResult]
   └─ Normalize enums, validate

5. PHASE 2: REPORT GENERATION
   ├─ Create Report object
   ├─ Calculate summary (count by severity)
   ├─ Sort findings (by severity, then file)
   └─ Format output (JSON or Table)

6. PHASE 3 (Optional): LLM ENRICHMENT
   ├─ Check GOOGLE_API_KEY
   ├─ Create AuditAgent
   ├─ Route findings to specialists
   └─ Generate enhanced insights

7. OUTPUT
   └─ Display to console or save to file
```

---

## Data Flow: Corpus Analysis

```
1. USER INPUT
   └─ meta-audit analyze --capsule proj1.json --capsule proj2.json

2. CAPSULE LOADING
   ├─ Discover capsule files
   ├─ Load & deserialize (ProjectCapsule objects)
   ├─ Validate structure
   └─ Extract to temporary directories

3. PHASE 1: PARALLEL COLLECTION
   ├─ For each capsule (max 3 parallel workers):
   │  ├─ Run Radon, Bandit, AI-Slop
   │  ├─ Collect findings
   │  └─ Store with project attribution
   └─ Aggregate all findings across projects

4. PHASE 2: CORPUS AGGREGATION
   ├─ Group findings by project
   ├─ Create individual Report per project
   ├─ Create CorpusAnalysisReport
   ├─ Calculate aggregate summary
   └─ Run CrossProjectAnalyzer:
      ├─ detect_duplicate_issues()
      ├─ detect_vulnerability_patterns()
      └─ detect_code_quality_trends()

5. OUTPUT
   ├─ JSON: All data (findings + patterns)
   └─ Table: Summary + per-project breakdown
```

---

## Phase 1: Collector Architecture

### Parallel Execution
```python
# In run_all_collectors()
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(get_complexity_metrics, path): "complexity",
        executor.submit(get_security_vulnerabilities, path): "security",
        executor.submit(get_ai_slop_findings, path): "ai_slop",
    }
    results = {}
    for future in as_completed(futures):
        name = futures[future]
        results[name] = future.result()  # Blocks on exception
```

### Output Normalization
```
Radon output (raw) → AnalysisResult
  complexity_data → pattern_type: "high_complexity"
                → severity: MEDIUM
                → evidence: {complexity: 15, ...}

Bandit output (raw) → AnalysisResult
  security_issue → pattern_type: "sql_injection"
              → severity: CRITICAL
              → evidence: {test_id: "B608", ...}

AI-Slop output (raw) → AnalysisResult
  pattern_match → pattern_type: "generic_naming"
             → severity: LOW
             → evidence: {indicators: [...], ...}
```

---

## Phase 2: Report Generation

### Single Project Flow
```python
# Step 1: Organize findings
findings_by_severity = group_by(findings, severity)

# Step 2: Create summary
summary = {
    "CRITICAL": len(findings_by_severity[CRITICAL]),
    "HIGH": len(findings_by_severity[HIGH]),
    ...
    "TOTAL": len(findings)
}

# Step 3: Sort for presentation
sorted_findings = sort_by(findings, [severity, file_path])

# Step 4: Export
if format == "json":
    return json.dumps({findings, summary, execution_time})
else:
    return render_table({findings, summary, execution_time})
```

### Corpus Flow
```python
# Step 1: Create individual reports
project_reports = {}
for project_name, findings in group_by_project(all_findings):
    project_reports[project_name] = Report(findings)

# Step 2: Aggregate
corpus_summary = sum all project summaries

# Step 3: Cross-project analysis
patterns = CrossProjectAnalyzer.analyze(group_by_project(all_findings))

# Step 4: Corpus report
return CorpusAnalysisReport(
    project_reports=project_reports,
    cross_project_patterns=patterns,
    summary=corpus_summary
)
```

---

## Phase 3: LLM Enhancement (Optional)

```
Phase 1 Findings (AnalysisResult objects)
    ↓
Serialize to JSON
    ↓
Create system prompt + context
    ↓
Call LLM Provider (Google Gemini, Mistral, Ollama)
    ↓
Parse response
    ↓
Create enriched findings (with LLM insights)
    ↓
Optional: Multi-agent routing to specialists
```

---

## Error Handling

### Collector Failures
```
if Bandit fails:
  └─ Log warning
  └─ Continue with Radon + AI-Slop
  └─ Mark as "partial_success" in status
  └─ User sees 2/3 analyzers succeeded
```

### Capsule Loading Failures
```
if ProjectCapsule.load() fails:
  └─ Log error
  └─ Skip this capsule
  └─ Continue with other capsules
  └─ Report progress
```

### LLM Failures
```
if GOOGLE_API_KEY missing:
  └─ Skip Phase 3 gracefully
  └─ Complete analysis with Phase 1+2
  └─ Inform user

if LLM call fails:
  └─ Log error
  └─ Return Phase 1+2 results only
  └─ No Phase 3 insights
```

---

## Extensibility

### Adding a New Collector

1. Create `src/meta_audit/analyzers/collectors/new_analyzer.py`:
```python
def get_new_findings(project_path: str) -> List[AnalysisResult]:
    """
    New collector implementation
    """
    findings = []
    # ... analyze code ...
    findings.append(AnalysisResult(...))
    return findings
```

2. Register in `__init__.py`:
```python
def run_all_collectors(project_path):
    results = {...}
    # Add new collector
    results['new_analyzer'] = get_new_findings(project_path)
    return results
```

### Adding a New Report Format

1. Create method in `Report` class:
```python
def to_yaml(self) -> str:
    """Export as YAML"""
    data = {...}
    return yaml.dump(data)
```

2. Update CLI:
```python
@click.option('--format', type=click.Choice(['json', 'table', 'yaml']))
def analyze(format):
    if format == 'yaml':
        output = report.to_yaml()
```

---

## Performance Characteristics

| Operation | Time | Depends On |
|-----------|------|-----------|
| Discover files | O(n) | # of files in project |
| Radon analysis | O(n*c) | # files × avg complexity |
| Bandit analysis | O(n) | # of files |
| AI-Slop analysis | O(n*l) | # files × lines per file |
| Report generation | O(m log m) | # of findings (sorted) |
| Corpus discovery | O(k) | # of capsule files |
| Cross-project analysis | O(m²) | # of findings (grouping) |

---

## Security Considerations

- **No external network calls** in Phase 1 (collectors are local)
- **Optional API calls** in Phase 3 (LLM provider, requires explicit API key)
- **Read-only** analysis (never modifies source code)
- **ProjectCapsule** contains no secrets (snapshots of code only)
- **Sensitive data**: Use private buckets for capsule storage

---

## Future Extensibility (Phase 4/5)

- **Smart Capsule modes** (hotspot, signature, full)
- **Semantic guardrails** (traceability, strictness config)
- **Multi-agent orchestration** (specialist personas)
- **Custom analyzers** (user-defined collectors)
- **Plugin system** (third-party integrations)

See `POST_MVP_ROADMAP.md` for details.
