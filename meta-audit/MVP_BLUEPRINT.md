# Capsule Audit - MVP Blueprint (Pragmatic Implementation)

**Status:** Prototype (v0.2.0) → Working MVP (v0.3.0)

**Goal:** Ein funktionierendes Analyse-Tool, das:
1. Ein Python-Projekt einliest (Phase 1: Collectors)
2. Es statisch analysiert (Phase 2: Agent mit echten Findings)
3. Strukturierte Reports ausgibt (CSV, JSON, YAML)
4. Konfigurierbar ist für mehrere Projekte (Capsule System)

**Timeline:** 3 Wochen (wenn alle 3 Säulen parallel gebaut werden)

---

## Status Quo (Nach Sprint 1 - v0.3.0-beta)

| Komponente | Status | Details |
|---|---|---|
| Collectors (Complexity, Security, AI-Slop) | ✅ COMPLETE | Echte Radon, Bandit, Pattern-Matching. 30 Tests GREEN |
| Collector Registry & Parallel Execution | ✅ COMPLETE | ThreadPoolExecutor, 0.8s für alle 3 Collector |
| CLI Integration Phase 1 | ✅ COMPLETE | `meta-audit analyze --path` orchestriert echte Analysen |
| Unit Tests | ✅ 19/19 PASS | Alle Collectors einzeln getestet |
| Integration Tests | ✅ 11/11 PASS | End-to-End Phase 1 validiert |
| Data Models (ProjectCapsule, AnalysisResult) | ✅ Definiert | Werden BALD genutzt (Sprint 2) |
| Report Generator | ❌ TODO | Sprint 2 |
| Reports (JSON, CSV, YAML, Terminal) | ❌ TODO | Sprint 2 |
| Capsule System | ❌ TODO | Sprint 3 |
| Tests | ✅ 30/30 PASS | Unit + Integration Tests für Phase 1 |

**Kurz:** Säule A DONE. Säule B & C ready to build.

---

## MVP-Definition: Die 3 Säulen

### Säule A: **Data Collection Layer (Phase 1 - echte Analyzer)**

**Ziel:** Von Mock-Daten zu echten statischen Analysen

**Zu implementieren:**

1. **Complexity Analyzer** (`src/meta_audit/analyzers/collectors/complexity.py`)
   - Nutze `radon` Library (bereits in Dependencies geplant)
   - Implementiere `get_complexity_metrics(path: str) -> dict` mit echten Daten:
     ```python
     {
       "cyclomatic_complexity": 8.5,  # Durchschnitt
       "maintainability_index": 82.3,
       "lines_of_code": 1234,
       "functions": [
         {"name": "foo", "cc": 3, "loc": 45},
         {"name": "bar", "cc": 12, "loc": 120}  # HIGH CC!
       ]
     }
     ```
   - Threshold-Config: HIGH wenn CC > 10

2. **Security Analyzer** (`src/meta_audit/analyzers/collectors/security.py`)
   - Nutze `bandit` Library
   - Implementiere `get_security_vulnerabilities(path: str) -> dict`:
     ```python
     {
       "vulnerabilities": [
         {
           "file": "main.py",
           "line": 42,
           "severity": "HIGH",
           "issue_type": "hardcoded_password",
           "message": "Possible hardcoded password"
         }
       ]
     }
     ```

3. **AI-Slop Analyzer** (`src/meta_audit/analyzers/collectors/ai_slop.py`)
   - Statische Pattern-Matching (keine LLM!)
   - Patterns aus `reference/AI_SLOP-V1.5.yaml` nutzen:
     - "Verbose docstrings with no real info"
     - "Placeholder comments"
     - "Dead code"
   - Output: `{"slop_findings": [...]}`

4. **Collector Registry & Parallel Execution** (`src/meta_audit/analyzers/collectors/__init__.py`)
   - Loader-Pattern: Alle Collector-Funktionen registrieren
   - Parallel-Ausführung mit `concurrent.futures.ThreadPoolExecutor`
   - Error-Handling: Wenn ein Collector fehlt, nicht abbrechen (graceful degradation)

**Deliverable:**
- Phase 1 liefert aggregierte `{complexity, security, ai_slop}` JSON-Struktur
- Kostet KEINE LLM-Tokens
- Kann parallel ausgeführt werden

---

### Säule B: **Analysis & Reporting (Phase 2 & 3 - strukturierte Outputs)**

**Ziel:** Von "LLM printet Text" zu "Strukturierte Analysis-Ergebnisse"

**WICHTIGE DECISION: Option A ("Data Model First")**

> Collectors müssen von Anfang an Pydantic `AnalysisResult` Objekte zurückgeben.
> Ein nachträglicher "dict → AnalysisResult" Converter würde unsere Guardrails untergraben.
> Die Pydantic-Modelle sind der strikte Datenvertrag zwischen allen Schichten.

**Zu implementieren:**

1. **AnalysisResult Model nutzen - COLLECTORS REFACTOR** (`src/meta_audit/core/models.py` + Collectors)
   - Die Pydantic-Modelle sind bereits definiert!
   - **Collectors müssen umgeschrieben werden**, um `AnalysisResult` Objekte zu erzeugen (statt dicts)
   - Collectors geben `List[AnalysisResult]` zurück:
     ```python
     @dataclass
     class AnalysisResult:
       analyzer_name: str  # "complexity_analyzer"
       file_path: str
       pattern_type: str  # "god_module" | "high_cc" | "hardcoded_password"
       severity: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
       category: str  # "CODE_STRUCTURE" | "SECURITY" | "MAINTAINABILITY"
       confidence: float  # 0.0 - 1.0
       message: str
       evidence: dict  # {"cc": 12, "loc": 120}
       remediation: list[str]  # ["Refactor into smaller functions"]
     ```

2. **AuditAgent - strukturiert mit Phase-1-Daten arbeiten** (`src/meta_audit/agents/audit_agent.py`)
   - **Input:** Liste von `AnalysisResult` Objekten
   - **Logik:**
     - Gruppiere nach `severity` und `category`
     - Für HIGH/CRITICAL Findings: Optional LLM-Aufruf (z.B. via `--advise` Flag)
     - LLM erhält nur: `{"finding": "god_module", "file": "main.py", "loc": 500, "remediation_suggestions": ...}`
     - **Nicht:** Den ganzen Code als Context
   - **Output:** Strukturierte JSON-Ergebnisse

3. **Report Generator** (`src/meta_audit/generators/report.py`)
   - Funktion: `generate_report(results: List[AnalysisResult]) -> Report`
   - `Report` Dataclass mit:
     ```python
     @dataclass
     class Report:
       summary: dict  # {critical: 3, high: 8, medium: 12}
       findings: List[AnalysisResult]
       execution_time: float
       token_cost_estimate: Optional[float]  # Aus LLM-Calls (später in Phase 4)
     ```
   - **OUTPUT FORMAT PRIORITÄT (Sprint 2):**
     - **Priorität 1:** JSON (Basis-Wahrheit, strukturiert, maschinenlesbar)
     - **Priorität 1:** Terminal/Rich Table (User-Interface für CLI-Feedback)
     - **Priorität 2:** YAML (Human-readable, später)
     - **Priorität 2:** CSV (Excel-freundlich, später)

   - Implementation:
     - `to_json()` → vollständige AnalysisResult-Liste
     - `to_terminal()` → Rich Table mit Farben und Formatierung
     - `to_yaml()` → (Sprint 3)
     - `to_csv()` → (Sprint 3)

4. **CLI Integration** (`src/meta_audit/cli/commands/analyze.py` - überarbeiten)
   - Alter Flow: `collectors → agent.run() → print(text)`
   - Neuer Flow: `collectors → [AnalysisResult] → report_gen → output files`
   - Flags:
     - `--format csv|json|yaml|table` (default: table)
     - `--output-file report.csv` (optional)
     - `--advise` (optional: LLM-Aufrufe für HIGH/CRITICAL)

**Deliverable:**
- Structured AnalysisResults statt LLM-Text
- Reports in 4 Formaten
- Optional LLM-Beratung (aber nicht obligatorisch)

---

### Säule C: **Capsule System (Multi-Projekt-Unterstützung)**

**Ziel:** "Mehrere Projekte konfigurieren, alle analysieren"

**Zu implementieren:**

1. **Capsule Model erweitern** (`src/meta_audit/core/models.py`)
   - ProjectCapsule ist schon definiert, nutzen!
   - Felder müssen gefüllt werden:
     - `project_name`: Aus CLI oder Config
     - `project_root`: Path zum Projekt
     - `python_version`: Aus `sys.version`
     - `files`: List[CapsuleFile] mit Inhalt
     - `metadata`: {created_at, analyzer_versions, ...}

2. **Config System aktivieren** (`src/meta_audit/phoenix_config/` - nutzen!)
   - Config-Format:
     ```yaml
     projects:
       - name: "project_a"
         path: "/path/to/project_a"
         enabled: true
         analyzers: ["complexity", "security", "ai_slop"]
       - name: "project_b"
         path: "/path/to/project_b"
         enabled: true

     analyzer_config:
       complexity:
         high_cc_threshold: 10
       security:
         enabled: true

     output:
       format: "json"
       directory: "./reports"
       include_token_estimate: true
     ```
   - CLI-Flag: `meta-audit analyze --config myconfig.yaml`

3. **Capsule Creation Command** (`src/meta_audit/cli/commands/capsule.py`)
   - Kommando: `meta-audit capsule create --path /project --name my_project`
   - Speichert ProjectCapsule als JSON/YAML
   - Damit: Projekte sind persistent + versioniert

4. **Batch-Analyse** (`src/meta_audit/cli/commands/analyze.py` - erweitern)
   - Kommando: `meta-audit analyze --config myconfig.yaml`
   - Logik:
     - Lade alle Projekte aus Config
     - Für jedes Projekt: Phase 1 + Phase 2 + Report
     - Parallel-Ausführung (mit limits) möglich
   - Output:
     - Pro Projekt ein Report-File
     - Summary-Report über alle Projekte

5. **Cross-Project Pattern Detection** (optional für MVP, aber vorbereitet)
   - Später: "God Module Pattern in 3 von 4 Projekten gefunden"
   - Data Structure ist schon im Model: `CrossProjectPattern`

**Deliverable:**
- Mehrere Projekte über Config definieren
- Batch-Analyse aller Projekte
- Ein Report pro Projekt + Summary

---

## Implementation Order (Dependency Graph)

### Sprint 1: Data Collection Layer ✅ COMPLETE
1. ✅ **Säule A:** Complexity & Security Analyzer mit echten Libs (radon, bandit, ai-slop pattern)
   - 8/8 Tasks complete
   - 30/30 Tests GREEN
   - Collectors laufen parallel (0.8s)
   - CLI orchestriert Phase 1

### Sprint 2: Structured Reporting (Aktuell)
2. **Säule B - Collectors Refactor:** Collectors geben AnalysisResult (Option A)
   - Refactor complexity.py, security.py, ai_slop.py
   - Update collector registry
   - 19 Unit + 11 Integration Tests neu schreiben
3. **Säule B - Report Generator:** JSON + Terminal/Rich (Priorität 1)
   - `Report` Model
   - `to_json()` method
   - `to_terminal()` mit Rich Table
   - CLI Flags: `--format`, `--output-file`
4. **Säule B - Testing:** Unit + Integration Tests für Reports
   - 15+ neue Tests

### Sprint 3: Capsule System + Polish (Woche 3)
5. **Säule C:** Config System aktivieren, Batch-Analyse
   - Multi-Project Support
   - ProjectCapsule Model
6. **Säule B - Extend:** YAML + CSV Formate (Priorität 2)
7. **Testing:** Integration Tests für alle 3 Säulen

---

## Guard Rails (Warum dieser Approach funktioniert)

### 1. **Token-Effizienz (Ihre Kernforderung)**
- Phase 1 kostet 0 Tokens
- Phase 2 (LLM) nur für HIGH/CRITICAL (optional via `--advise`)
- LLM erhält aggregierte Daten, nicht Rohcode
- **Result:** Ein 100-Datei Projekt = ~100-200 Tokens, nicht 100.000

### 2. **Provider-Flexibilität**
- Config entscheidet, welcher Provider
- Code nutzt nur `TextProvider` Base Class
- Mistral, Ollama, Google alle möglich
- **Implementation:** `phoenix_config` → `provider_loader.py` nutzen

### 3. **Regression Control**
- Jede Säule isoliert testbar
- Pydantic-Modelle sind strikt
- Test-Kapseln können mock collectors nutzen
- **Implementation:** Unit Tests für Collectors, Integration Tests für CLI

### 4. **Skalierbarkeit**
- Collectors laufen parallel (ThreadPoolExecutor)
- Batch-Analyse: Projekte können auch parallel (mit Limits)
- **Performance Target:** 100-Datei Projekt < 10 Sekunden (ohne LLM)

---

## Success Criteria (für MVP)

- [ ] Phase 1 liefert echte Analyzer-Daten (nicht Mock)
- [ ] Phase 2 erstellt strukturierte AnalysisResults (nicht nur LLM-Text)
- [ ] Phase 3 exportiert Reports in 4 Formaten
- [ ] Config-System funktioniert (mehrere Projekte definierbar)
- [ ] Batch-Analyse funktioniert
- [ ] Integration Tests decken den kompletten Flow ab
- [ ] Keine Token-Überraschungen (cost estimates akurat)

---

## Implementation Checklist

### Säule A: Data Collection
- [ ] Complexity Analyzer mit radon
- [ ] Security Analyzer mit bandit
- [ ] AI-Slop Analyzer (Pattern Matching)
- [ ] Collector Registry & Parallel Execution
- [ ] Error Handling (graceful degradation)

### Säule B: Analysis & Reporting
- [ ] AnalysisResult Pydantic Model korrekt nutzen
- [ ] AuditAgent mit echten Phase-1-Daten testen
- [ ] Report Generator (CSV, JSON, YAML)
- [ ] CLI Integration (--format, --output-file, --advise Flags)
- [ ] Token Cost Estimation

### Säule C: Capsule System
- [ ] ProjectCapsule Model korrekt füllen
- [ ] Config-System (phoenix_config) aktivieren
- [ ] Capsule Creation Command
- [ ] Batch-Analysis Command
- [ ] Cross-Project (vorbereitet, nicht implementiert)

### Testing & Polish
- [ ] Unit Tests für Collectors
- [ ] Unit Tests für Report Generator
- [ ] Integration Tests (CLI end-to-end)
- [ ] Performance Tests (100-Datei Projekt)
- [ ] Documentation Update

---

## Not in MVP (aber vorbereitet)

- Cross-Project Pattern Detection
- LLM-basierte "Actionable Steps" Generation
- HTML Report Export
- Web Dashboard
- CI/CD Integration

Diese kommen in v0.4+, wenn MVP stabil ist.

---

## Glossary (für Konsistenz)

| Term | Definition |
|---|---|
| **Collector** | Statischer Analyzer (radon, bandit, pattern-matching). Kostet 0 Tokens. |
| **AnalysisResult** | Strukturiertes Pydantic-Modell eines Findings. |
| **Report** | Aggregierte Liste von AnalysisResults + Metadaten. |
| **Capsule** | ProjectCapsule-Snapshot eines Projekts (mit Metadaten). |
| **Phase 1** | Collectors laufen, AnalysisResults werden erzeugt. |
| **Phase 2** | Optional LLM-Synthese (nur für HIGH/CRITICAL, nur mit `--advise`). |
| **Guardrail** | Mechanismus, um Wildwuchs zu verhindern (Token-Effizienz, Config-Driven, etc.). |

---

## Next Steps (nach diesem Blueprint)

1. **Review:** Stimmt dieser Blueprint mit Ihrem Use Case überein?
2. **Adjust:** Welche Säule ist am wichtigsten zuerst? (Meine Empfehlung: Säule A zuerst)
3. **Start:** Sprint 1 = Komplexität + Security Analyzer mit echten Libs
4. **Build:** Task-by-task (ich baue, du reviewst)

