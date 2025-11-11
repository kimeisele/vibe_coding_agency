# Post-MVP Roadmap (Phase 4 & 5)

**Status:** Phase 4 STARTED - Cross-Project Pattern Detection COMPLETE ✅

**Säule C (Corpus Analysis):** 100% Complete (Sprint 3)
- ProjectCapsule snapshot system ✅
- Batch processing with ThreadPoolExecutor ✅
- Corpus aggregation & reporting ✅
- Cross-project pattern detection ✅ (Phase 4.4 DONE)

**Timeline:** Phase 4 (In Progress) → Phase 5 (3+ Wochen)

---

## Phase 4: "Core Hardening" (Production-Ready)

**Ziel:** Das MVP wird robust, measurable und flexible

### Task 4.0: Architectural Refactoring & Quality Enhancement (NEU & HÖCHSTE PRIORITÄT)

**Was:** Behebung der architektonischen und qualitativen Mängel, die in der kritischen Analyse identifiziert wurden. Dies ist eine Voraussetzung für Phase 5.

**Implementation:**

1.  **Planner/Provider-Verantwortung korrigieren:**
    *   **Entferne die Logik aus dem Provider:** Die `get_audit_analysis` Methode in `google_provider.py` (und anderen) muss entfernt werden. Der `system_prompt` gehört hier nicht hin.
    *   **Stärke den Planner:** Der `Planner` in `planning.py` muss die Verantwortung für die Prompterstellung übernehmen. Er sollte den `system_prompt` (potenziell aus der `prompt_registry`) mit dem User-Kontext (den JSON-Daten) kombinieren.
    *   **Neuer Flow:** `Agent` → `Planner` (baut Prompt) → `Provider` (führt nur API-Call aus).

2.  **Datenvertrag (`AnalysisResult`) härten:**
    *   **`evidence`-Feld typisieren:** Ersetze `Dict[str, Any]` durch spezifische Pydantic-Modelle (z.B. `ComplexityEvidence`, `SecurityEvidence`) unter Verwendung von `Union`. Dies erzwingt einen strikten Vertrag.
    *   **Redundanz entfernen:** Lösche die ungenutzte `PatternEvidence`-Klasse aus `models.py`.
    *   **JSON-Serialisierung konsolidieren:** Stelle sicher, dass alle Modelle, die `Path`-Objekte enthalten, eine konsistente Serialisierungslogik haben.

3.  **Analyzer-Intelligenz verfeinern:**
    *   **`ai_slop` Detector:**
        *   Entferne das fälschliche Flagging von `args` und `kwargs`.
        *   Mache die Regeln (z.B. Liste generischer Variablennamen) über die `pyproject.toml` konfigurierbar.
    *   **`security` Collector:**
        *   Implementiere ein Mapping von Bandit `test_id` zu spezifischem, nützlichem Sanierungshinweis.
        *   Propagiere den `confidence`-Score von Bandit korrekt in das Hauptfeld des `AnalysisResult`.

4.  **Code-Konsistenz verbessern:**
    *   **Collector-Registrierung:** Refaktoriere die `collectors/__init__.py`, um konsequent den `@register_collector`-Decorator zu verwenden, anstatt der manuellen Registrierung.

**Success Criteria:**
- [ ] Die Provider-Klassen enthalten keine anwendungsspezifische Prompt-Logik mehr.
- [ ] Der Planner nutzt die `prompt_registry`, um Personas zu laden und Prompts zu erstellen.
- [ ] Das `evidence`-Feld in `AnalysisResult` ist streng typisiert.
- [ ] Die `ai_slop`-Analyse produziert keine offensichtlichen False Positives mehr.
- [ ] Die `security`-Analyse liefert spezifische, nützliche Remmediation-Texte.

---

### Task 4.1: Token-Transparenz & Cost-Tracking

**Was:** Implementiere vollständige Token- und Kosten-Verfolgung

**Implementation:**

1. **Extend TextProvider Base Class** (`src/meta_audit/providers/base.py`)
   ```python
   class TextProvider(ABC):
       def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
           """
           Estimates the cost of an API call.
           Returns: float (cost in USD)
           """
           pass

       def log_usage(self, usage_data: dict) -> None:
           """
           Log token usage and cost for this call.
           """
           pass
   ```

2. **Implement in all providers** (`src/meta_audit/providers/google_provider.py`, etc.)
   ```python
   def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
       # Google Gemini pricing: $0.0000375 per 1K input, $0.00015 per 1K output
       input_cost = (input_tokens / 1000) * 0.0000375
       output_cost = (output_tokens / 1000) * 0.00015
       return input_cost + output_cost
   ```

3. **AuditAgent tracks all calls** (`src/meta_audit/agents/audit_agent.py`)
   - Maintain a list of all LLM calls with {input_tokens, output_tokens, cost}
   - Aggregate at end: total_cost, total_tokens, cost_by_provider

4. **Report includes Cost Summary** (`src/meta_audit/generators/report.py`)
   ```python
   @dataclass
   class Report:
       summary: dict  # {critical: 3, high: 8, ...}
       findings: List[AnalysisResult]
       execution_time: float
       cost_tracking: CostSummary  # NEW
           total_tokens: int
           total_cost_usd: float
           calls: List[CallRecord]
   ```

**Success Criteria:**
- [ ] `estimate_cost()` works for Google, Mistral, Ollama
- [ ] Every LLM call is logged with token count + cost
- [ ] Report shows `Total Cost: $0.0042 USD` at the end
- [ ] User can estimate costs before running `--advise`

---

### Task 4.2: Provider-Flexibilität validieren

**Was:** Beweise, dass Provider-Wechsel ohne Code-Änderungen funktioniert

**Implementation:**

1. **Integration Test: Same Result, Different Providers**
   ```python
   # tests/integration/test_provider_flexibility.py

   def test_audit_same_result_all_providers():
       """Run the same audit with google, mistral, ollama. Structure must be identical."""

       test_project = create_test_capsule()

       for provider_name in ["google", "mistral", "ollama"]:
           config = load_config()
           config.provider = provider_name

           result = run_analyze(test_project, config, advise=False)

           # Structure should be identical (same findings, same AnalysisResults)
           assert len(result.findings) == expected_count
           assert result.summary["critical"] == expected_critical
   ```

2. **Config-Driven Provider Selection**
   - `src/meta_audit/phoenix_config/` must support: `provider: google | mistral | ollama`
   - CLI: `meta-audit analyze --provider mistral`
   - Config: `providers.yaml` mit provider-spezifischen settings

3. **Provider Loader** (`src/meta_audit/providers/provider_loader.py`)
   - Implement registry pattern: `@register_provider("google")`
   - Loader: `get_provider(config.provider) → TextProvider instance`

**Success Criteria:**
- [ ] Same audit run with `--provider=google` and `--provider=mistral` produces identical AnalysisResults
- [ ] Provider can be switched via config, no code changes
- [ ] Ollama (local) works without API keys
- [ ] Integration test validates this

---

### Task 4.3: Skalierbarkeit & SLO Definition

**Was:** Define Service Level Objectives und optimize for scale

**Implementation:**

1. **Define SLO** (Dokumentation in `SLO.md`)
   ```
   Phase 1 (Collectors, statisch):
   - 1,000 Dateien muss in < 60 Sekunden scanned werden (ohne LLM)
   - Radon, Bandit, AI-Slop parallel

   Phase 2 (LLM, optional):
   - Ein HIGH/CRITICAL Finding darf maximal 2 Sekunden dauern (API latency)
   - Max 10 LLM-Calls pro Audit (zu schützen vor Wildwuchs)

   End-to-End:
   - Ein 100-Datei Projekt: < 30 Sekunden (ohne --advise)
   - Ein 100-Datei Projekt mit --advise (10 calls): < 60 Sekunden
   ```

2. **Parallelize Collectors** (`src/meta_audit/analyzers/collectors/__init__.py`)
   - Current: `ThreadPoolExecutor` (bereits implementiert in MVP)
   - Measure: Wie lange dauert radon + bandit + ai_slop für 1000 Dateien?
   - Optimiere: Batch-processing, lazy loading, caching

3. **Performance Test** (`tests/performance/test_slo.py`)
   ```python
   def test_phase1_performance_1000_files():
       """Phase 1 must process 1000 files in < 60 seconds."""
       result = run_collectors(large_project, timeout=60)
       assert result.execution_time < 60
   ```

**Success Criteria:**
- [ ] SLO dokumentiert und klar
- [ ] Performance benchmark existiert
- [ ] Phase 1 erfüllt < 60 Sekunden für 1000 Dateien
- [ ] Phase 2 (LLM) mit Limits: max 10 calls pro audit

---

### Task 4.4: Smart Capsule Strategy (Token Efficiency & Signal-Noise Ratio)

**Was:** Intelligente Kapselerzeugung mit konfigurierbaren Modi für optimales Signal-zu-Rausch-Verhältnis

**Problem:** Eine naive "Full Capsule" mit allen Quellcode wäre riesig, voller Rauschen und würde zu Token-Explosionen führen.

**Solution:** Drei konfigurierbare Modi mit unterschiedlichen Trade-offs

**Implementation:**

1. **Mode 1: "Hotspot" Capsule (Standard & Empfohlen)**
   ```yaml
   Inhalt: Quellcode nur für HIGH/CRITICAL Severity Dateien
           Alle anderen als Metadaten (Pfad, Größe)
   Signal/Rauschen: MAXIMAL
   Token-Effizienz: Extrem hoch
   Use Case: LLM-fokussierte Analyse auf Problemzonen
   ```

2. **Mode 2: "Signature" Capsule**
   ```yaml
   Inhalt: AST-basierte Funktions-/Klassensignaturen aller Dateien
           Keine Implementierungsdetails
   Signal/Rauschen: HOCH
   Token-Effizienz: Hoch
   Use Case: Struktureller Überblick ohne Implementation-Noise
   ```

3. **Mode 3: "Full" Capsule**
   ```yaml
   Inhalt: Kompletter Quellcode aller Dateien (Brute-Force)
   Signal/Rauschen: SEHR NIEDRIG
   Token-Effizienz: Sehr schlecht
   Empfehlung: Nicht verwendet (hohe Kosten + Rauschen)
   ```

**Implementation Details:**

1. **Update CapsuleFile & ProjectCapsule** (`src/meta_audit/core/models.py`)
   - Add `capsule_mode: str` field ("hotspot" | "signature" | "full")
   - Add `metadata_only: bool` for files not included in content

2. **Implement Mode Builders** (`src/meta_audit/cli/commands/capsule.py`)
   ```python
   def create_hotspot_capsule(project_path, findings_by_severity):
       """Include full content for HIGH/CRITICAL, metadata-only for others"""

   def create_signature_capsule(project_path):
       """AST parse all files, extract signatures only"""

   def create_full_capsule(project_path):
       """All source code (not recommended)"""
   ```

3. **CLI Integration** (`src/meta_audit/cli/commands/capsule.py`)
   ```bash
   meta-audit capsule create --path /project --mode hotspot
   meta-audit capsule create --path /project --mode signature
   meta-audit capsule create --path /project --mode full
   ```

**Success Criteria:**
- [ ] Three capsule modes work correctly
- [ ] Hotspot mode: 10-50% of full capsule size
- [ ] Signature mode: 20-60% of full capsule size
- [ ] Token estimation shown in CLI output
- [ ] Production config defaults to "hotspot"

---

### Task 4.5: Semantic Guardrails (Data-Driven Accuracy Framework)

**Was:** Technische Guardrails zur Gewährleistung von Genauigkeit, Nachverfolgbarkeit und Umsetzbarkeit ohne Spekulationen

**Problem:** LLM-Agent darf NICHT spekulieren. Jede Schlussfolgerung muss auf Schicht 1 (Static Collector) Daten rückverfolgbar sein.

**Solution:** Drei technische Guardrails (nicht philosophisch, sondern technisch)

**Implementation:**

1. **Guardrail 1: Prinzip der Rückverfolgbarkeit (Traceability)**

   **Problem:** Eine Analyse ist nur vertrauenswürdig, wenn sie überprüfbar ist.

   **Lösung:** LLM muss Quellen nennen
   ```python
   # In AuditAgent.run(), für jede LLM-Schlussfolgerung:
   finding_references = {
       "finding_id": "SECURITY-001",  # Aus Schicht 1
       "analyzer": "bandit",
       "line": 42,
       "original_message": "SQL injection..."
   }

   llm_conclusion = {
       "enrichment": "This is a... ",
       "source_findings": [finding_references],  # MANDATORY
       "confidence": 0.92
   }
   ```

2. **Guardrail 2: Prinzip der konfigurierbaren Strenge (Configurable Strictness)**

   **Problem:** "Knallhart" ist subjektiv und teamabhängig.

   **Lösung:** Konfigurierbare Strenge in `phoenix_config`
   ```yaml
   # config/analysis_strictness.yaml
   analysis:
     strictness: "high"  # high | medium | low
     ignore_patterns:
       - "test_*.py"
       - "vendor/"
     severity_threshold: "MEDIUM"  # Only report >= MEDIUM
     confidence_threshold: 0.75

   audit:
     fail_on_critical: true
     fail_on_high: false
     max_issues_report: 100
   ```

3. **Guardrail 3: Prinzip der umsetzbaren Artefakte (Actionable Artifacts)**

   **Problem:** Ein reiner Text-Report ist oft nicht der letzte Schritt.

   **Lösung:** Strukturierte, maschinenlesbare Artefakte pro Persona
   ```python
   # Task 5.2 (Phase 5) wird Personas definieren
   # Task 4.5 (Phase 4) erstellt Framework für diese Artefakte

   class ActionableArtifact(BaseModel):
       """Output für spezifische Personas - nicht Text!"""
       persona: str  # "refactor", "qa_analyst", "security_expert"
       artifact_type: str  # "git_diff", "pytest_function", "mitigation_plan"
       content: str  # Actual code/patch/plan
       source_findings: List[str]  # Rückverfolgbar zu Schicht 1
       validation_steps: List[str]  # Wie man das validiert
   ```

**Implementation Details:**

1. **Update AuditAgent** (`src/meta_audit/agents/audit_agent.py`)
   - Enforce traceability: Jede LLM-Ausgabe muss `source_findings` enthalten
   - Laden config.analysis_strictness und anwenden

2. **Create Config Validator** (`src/meta_audit/phoenix_config/validators.py`)
   - Validate strictness levels
   - Validate threshold values
   - Warn wenn config zu lax/streng

3. **Artifact Types** (Platzhalter für Phase 5)
   ```python
   ARTIFACT_TYPES = {
       "refactor": "git_diff_patch",
       "qa_analyst": "pytest_function",
       "security_expert": "mitigation_plan",
       "performance": "profiling_suggestion"
   }
   ```

4. **Test: Traceability Enforcement** (`tests/unit/test_guardrails.py`)
   ```python
   def test_llm_output_has_source_findings():
       """Every LLM conclusion must reference original findings"""
       output = agent.run(findings)
       for conclusion in output.llm_conclusions:
           assert conclusion.source_findings, "Must reference Schicht 1 data"
   ```

**Success Criteria:**
- [ ] Traceability: Jede LLM-Ausgabe hat `source_findings`
- [ ] Config: `analysis_strictness` konfigurierbar
- [ ] Artifacts: Framework für actionable artifacts existiert
- [ ] Tests: Traceability & Strictness erzwungen
- [ ] Documentation: Guardrails für Nutzer erklärt

---

## Phase 5: "Framework Vision" (Multi-Agent Orchestration)

**Ziel:** Realisiere die "Project Steward" Vision mit spezialisierten Personas

### Task 5.1: Project Steward (Erweiterte Agent-Logik)

**Was:** Der AuditAgent wird zum "Orchestrator", der mehrere spezialisierte Agents koordiniert

**Implementation:**

1. **Extend AuditAgent** (`src/meta_audit/agents/audit_agent.py`)
   ```python
   class AuditAgent:
       def run(self, results: List[AnalysisResult]) -> Report:
           """
           Orchestrate multiple specialist personas.
           """
           # Step 1: Group findings by severity
           high_critical = filter(results, severity >= "HIGH")

           # Step 2: For each HIGH/CRITICAL finding, call specialist
           refined_results = []
           for finding in high_critical:
               specialist_output = self.call_specialist(finding)
               refined_results.append(specialist_output)

           return Report(findings=refined_results)

       def call_specialist(self, finding: AnalysisResult, persona: str = "auto") -> AnalysisResult:
           """
           Route to specialist persona based on finding category.
           """
           if finding.category == "CODE_STRUCTURE":
               persona = "refactor_gpt"
           elif finding.category == "SECURITY":
               persona = "security_analyst"

           prompt = self.prompt_registry.get(persona)
           response = self.provider.generate(prompt, context=finding)
           return self.parse_response(response, finding)
   ```

2. **Planner erweitern** (`src/meta_audit/agents/planning.py`)
   - Current: Single prompt execution
   - New: Chain of prompts (Plan → Analyze → Refactor → Validate)
   - Conditional branching: Wenn finding.severity == CRITICAL, rufe 2 Personas auf

---

### Task 5.2: Specialist Persona Library

**Was:** Baue die `prompt_registry` mit konkreten Personas (aus Ihrem Dokument)

**Implementation:**

1. **Prompt Registry Structure** (`src/meta_audit/prompt_registry/`)
   ```
   personas/
   ├── qa_analyst.json
   ├── security_analyst.json
   ├── refactor_gpt.json
   ├── logic_debugger.json
   └── performance_analyst.json
   ```

2. **Each Persona** (Beispiel: `qa_analyst.json`)
   ```json
   {
     "name": "QA Analyst",
     "description": "Generates test cases to validate findings",
     "system_prompt": "You are a QA expert. Your job is to create pytest test cases that validate code issues.",
     "input_schema": {
       "finding": "AnalysisResult",
       "code_snippet": "Optional[str]"
     },
     "output_schema": {
       "test_code": "str",
       "test_description": "str"
     }
   }
   ```

3. **Available Personas:**
   - **QA Analyst**: Generiere Testfälle für gefundene Fehler
   - **Security Analyst**: Tiefere Security-Analyse + Remediation für HIGH/CRITICAL
   - **RefactorGPT**: Code-Verbesserungsvorschläge für Komplexität/Wartbarkeit
   - **Logic Debugger**: Erklärung komplexer Code-Patterns
   - **Performance Analyst**: Profiling-Vorschläge für langsame Funktionen

---

### Task 5.3: Multi-Agent QA-Refactor Loop

**Was:** Neue CLI-Features für iterative Verbesserung

**Implementation:**

1. **New Command: `meta-audit advise`** (`src/meta_audit/cli/commands/advise.py`)
   ```bash
   meta-audit advise --finding-id god_module_main <project_path>
   ```

2. **QA-Refactor Loop**
   ```python
   def qa_refactor_loop(finding: AnalysisResult):
       # Step 1: QA Analyst generates test
       qa_specialist = load_specialist("qa_analyst")
       test_code = qa_specialist.execute(finding)

       # Step 2: RefactorGPT fixes the code
       refactor_specialist = load_specialist("refactor_gpt")
       fixed_code = refactor_specialist.execute(finding, test_code)

       # Step 3: Output both
       return {
           "test": test_code,
           "fix": fixed_code,
           "explanation": "..."
       }
   ```

3. **Integration in Report**
   - Wenn `--mode=advise`, dann für jeden HIGH/CRITICAL Finding:
     - Speichere generierte Tests in `/reports/tests/`
     - Speichere Code-Fixes in `/reports/fixes/`
     - Nutzer kann direkt übernehmen oder anpassen

**Success Criteria:**
- [ ] `meta-audit advise` command existiert
- [ ] Für ein HIGH finding generiert es Test + Fix
- [ ] Output ist in `/reports/` strukturiert
- [ ] Nutzer kann direkt "copy-paste" verwenden

---

### Task 5.4: Recursive Criticism & Improvement (RCI)

**Was:** Agent reviewt seinen eigenen Report und verfeinert ihn

**Implementation:**

1. **New Flag: `--refine`**
   ```bash
   meta-audit analyze --refine <project_path>
   ```

2. **RCI Loop** (`src/meta_audit/agents/planning.py`)
   ```python
   def recursive_criticism_improvement(report: Report) -> Report:
       """
       Agent reviews its own report and refines it.
       """
       criticism_prompt = f"""
       Here is an audit report:
       {json.dumps(report.to_dict())}

       What's wrong or missing? Where can we improve clarity?
       """

       criticism = self.provider.generate(criticism_prompt)

       # Now fix based on criticism
       refinement_prompt = f"""
       Based on this criticism:
       {criticism}

       Refine and improve the audit report.
       """

       refined_report = self.provider.generate(refinement_prompt)
       return parse_report(refined_report)
   ```

3. **Cost Tracking for RCI**
   - RCI sollte optional sein (kostet extra LLM-Calls)
   - Muss im Cost-Report sichtbar sein: "Original: 5 calls + Refine: 2 calls"

**Success Criteria:**
- [ ] `--refine` flag funktioniert
- [ ] Agent kritisiert seinen eigenen Report
- [ ] Refinement wird angewendet
- [ ] Extra-Kosten sind sichtbar

---

## Implementation Timeline (Post-MVP)

| Phase | Task | Duration | Depends On |
|---|---|---|---|
| Phase 4.1 | Token-Transparenz | 1 Woche | MVP stable |
| Phase 4.2 | Provider-Flexibilität | 1 Woche | Phase 4.1 |
| Phase 4.3 | SLO & Performance | 1 Woche | MVP stable |
| Phase 5.1 | Project Steward | 1 Woche | Phase 4.x |
| Phase 5.2 | Persona Library | 2 Wochen | Phase 5.1 |
| Phase 5.3 | Multi-Agent Loop | 2 Wochen | Phase 5.2 |
| Phase 5.4 | RCI | 1 Woche | Phase 5.3 |

**Total:** ~10 Wochen (nach MVP)

---

## Guard Rails for Post-MVP

### 1. Token-Kosten Explosion Verhindern
- [ ] Max 10 LLM-Calls pro Audit (definiert in SLO)
- [ ] Jeder Call muss protokolliert werden (Token + Cost)
- [ ] Warnung wenn geschätzter Cost > Budget (z.B. $1.00)

### 2. Provider-Neutralität sichern
- [ ] Kein Provider-spezifischer Code außerhalb von `providers/`
- [ ] Test: Gleicher Audit mit 3 verschiedenen Providern = Gleiche Struktur
- [ ] Falls Provider nicht verfügbar → Graceful Fallback (z.B. zu Ollama)

### 3. Skalierbarkeit & Performance
- [ ] Alle Performance-Benchmarks in `tests/performance/`
- [ ] SLO-Verletzungen triggern Alert/Fehler
- [ ] Caching wo sinnvoll (z.B. Radon-Ergebnisse für gleiche Datei)

---

## Vision: Das "Ultimate Meta Audit Tool"

Nach Phase 5 haben wir:

1. **Phase 1 (Collectors):** Schnell, kostenlos, parallel
   - Radon (Komplexität), Bandit (Security), AI-Slop (Pattern)

2. **Phase 2 (Agent Orchestration):** Token-effizient, spezialisiert
   - Project Steward leitet Findings an Personas weiter
   - QA Analyst generiert Tests
   - RefactorGPT generiert Code-Fixes
   - Security Analyst tiefere Analyse

3. **Phase 3 (Reporting):** Strukturiert, actionable
   - Strukturierte Reports (JSON, CSV, YAML)
   - Generierte Tests + Fixes sind ready-to-use
   - Cost-Tracking vollständig sichtbar

4. **Phase 4 (Hardening):** Production-ready
   - Skalierbar (1000 Dateien < 60s)
   - Provider-flexibel (Google, Mistral, Ollama)
   - Measurable (SLO, Performance)

5. **Phase 5 (Framework):** Multiplex-intelligent
   - Recursive Criticism & Improvement
   - Multi-Persona Orchestration
   - Fully Automated Code Remediation (optional)

---

## Success = Convergence

Das Projekt konvergiert zu einer **einfachen, stabilen, skalierbaren Architektur**:

```
User Input (Project Path)
    ↓
Phase 1: Collectors (0 Tokens, < 60s)
    ├── Radon (Complexity)
    ├── Bandit (Security)
    └── AI-Slop (Patterns)
    ↓
Phase 2: Agent Orchestration (Optional, < 10 LLM calls)
    ├── Project Steward (Router)
    ├── Persona Library (Specialists)
    └── RCI Loop (Self-Refinement)
    ↓
Phase 3: Structured Reports
    ├── JSON/CSV/YAML
    ├── Generated Tests
    ├── Code Fixes
    └── Cost Summary
    ↓
Output: Ready-to-use Improvements
```

Dies ist die vollständige Vision. Los geht's! 🚀

