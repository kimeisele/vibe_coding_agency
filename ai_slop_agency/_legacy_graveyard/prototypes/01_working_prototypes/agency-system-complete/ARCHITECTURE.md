# Agency System Architecture

## 🏗️ High-Level Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code Agent                           │
│                  (Orchestriert alles)                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP Request / Python Import
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Agency System                                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  CLI Interface (click)                                │     │
│  │  - run                                                 │     │
│  │  - status                                              │     │
│  │  - list-notebooks                                      │     │
│  │  - serve                                               │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  REST API (Flask)                                    │     │
│  │  - POST   /api/v1/run                               │     │
│  │  - GET    /api/v1/status/<id>                       │     │
│  │  - GET    /api/v1/list-notebooks                    │     │
│  │  - GET    /health                                    │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  NotebookOrchestrator (Core)                         │     │
│  │                                                       │     │
│  │  1. Projektverzeichnis erstellen                     │     │
│  │  2. Template-Notizbuch finden                        │     │
│  │  3. Parameter injizieren (Papermill)                 │     │
│  │  4. Notizbuch ausführen                              │     │
│  │  5. Outputs extrahieren                              │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  Papermill Executor                                  │     │
│  │  (Jupyter Notizbücher mit Parametern)                │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  Notebooks (Templates)                               │     │
│  │                                                       │     │
│  │  analysis_workflow.ipynb                             │     │
│  │  ├─ Phase 1: Semantic Understanding                  │     │
│  │  ├─ Phase 2: Knowledge Acquisition                   │     │
│  │  ├─ Phase 3: Data-Driven Validation                  │     │
│  │  └─ Phase 4: Report Generation                       │     │
│  │                                                       │     │
│  │  code_generation_workflow.ipynb                      │     │
│  │  legacy_refactoring_workflow.ipynb                   │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  External Services (in Notebooks)                    │     │
│  │                                                       │     │
│  │  ├─ Claude API (Web Search, Analysis)                │     │
│  │  ├─ Code Analysis Tools                              │     │
│  │  │  ├─ flake8 (Python)                              │     │
│  │  │  ├─ eslint (JavaScript/React)                    │     │
│  │  │  ├─ bandit (Security)                            │     │
│  │  │  └─ ... (beliebig erweiterbar)                   │     │
│  │  └─ LLM Integration (Synthese, Reporting)            │     │
│  └───────────────┬──────────────────────────────────────┘     │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────┐     │
│  │  Project Persistence                                │     │
│  │                                                       │     │
│  │  projects/                                            │     │
│  │  └─ acme-corp-20251110_143000/                       │     │
│  │     ├─ analysis_workflow_executed.ipynb               │     │
│  │     ├─ parameters.json                                │     │
│  │     ├─ report.md                                      │     │
│  │     └─ scan_results.json                              │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                 ▲
                 │ JSON Response
                 │
        Claude Code Agent
        (Interpretiert & Entscheidet)
```

---

## 📊 Request-Response Flow (detailliert)

```
Claude Code Agent
    │
    ├─ POST /api/v1/run
    │  {
    │    "notebook_type": "analysis",
    │    "project_name": "acme-corp",
    │    "client_request": "App is slow",
    │    "code_path": "/path/to/code",
    │    "tech_stack": "django"
    │  }
    │
    ▼
Flask REST API (api/rest.py)
    │
    ├─ Validiert Input
    ├─ Ruft NotebookOrchestrator.run() auf
    │
    ▼
NotebookOrchestrator.run() (orchestrator/core.py)
    │
    ├─ 1. Erstelle Projektverzeichnis
    │     projects/acme-corp-20251110_143000/
    │
    ├─ 2. Finde Template: notebooks/analysis_workflow.ipynb
    │
    ├─ 3. Bereite Parameter vor
    │     {
    │       "project_name": "acme-corp",
    │       "client_request": "App is slow",
    │       "code_path": "/path/to/code",
    │       "tech_stack": "django",
    │       "execution_time": "2025-11-10T14:30:00Z"
    │     }
    │
    ├─ 4. Rufe Papermill auf
    │     pm.execute_notebook(
    │       input_path="notebooks/analysis_workflow.ipynb",
    │       output_path="projects/acme-corp.../analysis_workflow_executed.ipynb",
    │       parameters={...}
    │     )
    │
    ▼
Papermill + Jupyter Kernel
    │
    ├─ Lade Notizbuch
    ├─ Injiziere Parameter in erste Code-Zelle
    ├─ Führe alle Zellen aus (der Reihe nach)
    │
    ▼
Notizbuch-Ausführung (4 Phasen)
    │
    ├─ Phase 1: Semantic Understanding
    │  ├─ Parse client_request
    │  ├─ Identifiziere Knowledge Gaps
    │  ├─ Speichere als semantic_analysis = {...}
    │  └─ Print/Save für nächste Phase
    │
    ├─ Phase 2: Knowledge Acquisition
    │  ├─ Erstelle research_plan
    │  ├─ Rufe Claude API mit web_search auf
    │  ├─ Sammle Ergebnisse
    │  └─ Speichere findings
    │
    ├─ Phase 3: Data-Driven Validation
    │  ├─ Prüfe ob code_path existiert
    │  ├─ Wähle Tools basierend auf tech_stack
    │  ├─ Führe Tools aus (flake8, eslint, etc.)
    │  ├─ Capture RAW outputs
    │  └─ Speichere validation_results
    │
    ├─ Phase 4: Report Generation
    │  ├─ Synthetisiere alle Findings
    │  ├─ Erstelle professionellen Report (Markdown)
    │  ├─ Schreibe Empfehlungen
    │  └─ Speichere final_report = "..."
    │
    ▼
Notizbuch beendet
    │
    ├─ Alle Outputs sind in Notizbuch-Zellen
    ├─ Notizbuch gespeichert: analysis_workflow_executed.ipynb
    │
    ▼
NotebookOrchestrator._extract_outputs()
    │
    ├─ Lade ausgeführtes Notizbuch
    ├─ Parse Markdown-Zellen als Sektionen
    ├─ Extract Code-Outputs
    ├─ Sammle alles in Dict:
    │  {
    │    "semantic_understanding": {...},
    │    "research_results": [...],
    │    "validation_results": {...},
    │    "final_report": "# Report..."
    │  }
    │
    ▼
NotebookOrchestrator.run() gibt zurück
    │
    ├─ {
    │    "status": "success",
    │    "project_id": "acme-corp-20251110_143000",
    │    "executed_notebook": "projects/.../analysis_workflow_executed.ipynb",
    │    "outputs": {...},
    │    "metadata": {...}
    │  }
    │
    ▼
Flask API serialisiert zu JSON
    │
    ├─ HTTP 200 OK
    │
    ▼
Claude Code empfängt Response
    │
    ├─ Parsed JSON
    ├─ Interpretiert Findings
    ├─ Entscheidet nächste Steps
    │  (z.B. weitere Analysen, Kundenkommunikation, etc.)
    │
    └─ Mögliche nächste Actions:
       ├─ Neuer Workflow (run ein anderes Notizbuch)
       ├─ Kunde kontaktieren
       ├─ Detailierte Planung
       └─ Implementierung starten
```

---

## 🔄 Datenfluss: Was passiert mit Daten

```
INPUTS (von Claude Code)
└─ client_request (String)
└─ tech_stack (django, react, node, ...)
└─ code_path (local folder or URL)
└─ project_name (identifier)

        ▼

IN PAPERMILL PARAMETERS
└─ Injiziert in erste Notebook-Zelle
└─ Als Variablen verfügbar in allen Zellen

        ▼

IN NOTEBOOK PHASE 1
├─ Parse client_request
├─ Identify tech stack
├─ Create knowledge gaps list
└─ Output: semantic_analysis (Dict)

        ▼

IN NOTEBOOK PHASE 2
├─ Generate search queries
├─ Call Claude API with web_search
├─ Collect research findings
└─ Output: research_results (List of findings)

        ▼

IN NOTEBOOK PHASE 3
├─ Load code from code_path
├─ Run analysis tools (flake8, eslint, etc.)
├─ Capture tool outputs
└─ Output: validation_results (Dict)

        ▼

IN NOTEBOOK PHASE 4
├─ Read semantic_analysis, research_results, validation_results
├─ Synthesize into professional report
├─ Generate recommendations
└─ Output: final_report (Markdown string)

        ▼

EXTRACTED OUTPUTS
└─ All phase outputs combined into:
   {
     "semantic_understanding": semantic_analysis,
     "research_results": research_results,
     "validation_results": validation_results,
     "final_report": final_report
   }

        ▼

RETURNED TO CLAUDE CODE
└─ As JSON in HTTP Response
└─ Claude Code can now:
   ├─ Show to customer
   ├─ Use for follow-up analysis
   ├─ Trigger further actions
   └─ Make business decisions
```

---

## 📁 Directory Layout

```
agency-system/
│
├── cli/
│   └── main.py                    # CLI mit Click
│       ├─ run()                   # Start workflow
│       ├─ status()                # Check project
│       ├─ list-notebooks()        # List templates
│       └─ serve()                 # Start API server
│
├── api/
│   ├── rest.py                    # Flask REST API
│   │   ├─ /health
│   │   ├─ /api/v1/run
│   │   ├─ /api/v1/status/<id>
│   │   └─ /api/v1/list-notebooks
│   │
│   └── __init__.py
│
├── orchestrator/
│   ├── core.py                    # NotebookOrchestrator
│   │   ├─ run()                   # Orchestriere Notizbuch
│   │   ├─ _get_template_notebook()
│   │   ├─ _extract_outputs()
│   │   └─ get_project_status()
│   │
│   └── __init__.py
│
├── config/
│   ├── settings.py                # Konfiguration
│   ├── tool_config.py             # Tool-Mapping
│   └── __init__.py
│
├── notebooks/                     # Notizbuch-Templates
│   ├── analysis_workflow.ipynb
│   ├── code_generation_workflow.ipynb
│   └── legacy_refactoring_workflow.ipynb
│
├── projects/                      # Ausgeführte Projekte
│   └── acme-corp-20251110_143000/
│       ├── analysis_workflow_executed.ipynb
│       ├── parameters.json
│       ├── report.md
│       └── scan_results.json
│
├── requirements.txt               # Python Dependencies
├── setup.sh                       # Installation
├── README.md                      # Dokumentation
└── __init__.py
```

---

## 🔌 Integration Points

Wo kannst du noch andere Systeme verbinden?

```
Notizbuch (Phase 2: Knowledge Acquisition)
    │
    ├─ Claude API (web_search) ─── bereits gebaut
    │
    ├─ Gemini API (optional)
    │   └─ Für alternative Research
    │
    ├─ OpenAI API (optional)
    │   └─ Für alternative LLM
    │
    └─ Your Custom APIs
        └─ Z.B. interne Wissensdatenbank

Notizbuch (Phase 3: Data-Driven Validation)
    │
    ├─ Local Tools (bereits gebaut)
    │   ├─ flake8, eslint, bandit
    │   ├─ npm audit, pip audit
    │   └─ Custom scripts
    │
    ├─ Remote Scanning Services
    │   ├─ Snyk (Security)
    │   ├─ SonarQube (Quality)
    │   └─ CodeClimate (Metrics)
    │
    └─ Database Queries
        └─ Z.B. Performance Stats aus Production

Notizbuch (Phase 4: Report Generation)
    │
    ├─ Email Service
    │   └─ Send report to customer
    │
    ├─ PDF/HTML Export
    │   └─ Professional formatting
    │
    ├─ Slack Integration
    │   └─ Notify team
    │
    └─ Project Management
        ├─ Jira
        ├─ Linear
        └─ Asana
```

---

## 🚀 Skalierung

**Von MVP zu Production:**

```
MVP (Current)
└─ Single Machine
└─ No Authentication
└─ Simple File Storage
└─ Direct Python Imports

        ▼

Growing Team
├─ Add Authentication (API Keys)
├─ Add Rate Limiting
├─ Store in Cloud (S3, GCS)
├─ Use Message Queue (Celery, RQ)
├─ Separate Worker Process

        ▼

Enterprise
├─ Multi-Server Setup (Kubernetes)
├─ Database (PostgreSQL for metadata)
├─ Advanced Auth (OAuth2)
├─ Monitoring & Alerting
├─ Audit Logging
├─ Backup & Disaster Recovery
└─ Multi-Tenant Support
```

---

## 💡 Erweiterungsideen

### 1. Webhook Support
```python
# Nach Workflow-Completion
webhook_url = parameters.get("webhook_url")
if webhook_url:
    requests.post(webhook_url, json=result)
```

### 2. Async Execution
```python
# Statt sync run()
celery_task = orchestrator.run_async(...)
task_id = celery_task.id

# Später checken
status = get_task_status(task_id)
```

### 3. Versioning
```python
# Verschiedene Notizbuch-Versionen
notebooks/
├── v1/
├── v2/
└── v3/
```

### 4. Custom Validators
```python
# Nach Ausführung validieren
def validate_output(result):
    if not result["outputs"]["final_report"]:
        raise ValidationError("Missing report")
```

---

Done! 🎉

