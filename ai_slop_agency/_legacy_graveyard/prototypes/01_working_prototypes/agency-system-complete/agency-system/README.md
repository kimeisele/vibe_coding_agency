# 🏢 Agency System: Agent-Ready Notebook Orchestrator

Ein **schlankes, für Agents designtes System** zur Orchestrierung von Analyse-Workflows.

- **CLI** für Claude Code (und Menschen)
- **REST API** für automatisierte Agents
- **Jupyter Notebooks** als ausführbare Dokumentation
- **Papermill** für automatische Ausführung mit Parameter-Injection

---

## 🎯 Das Konzept

```
Claude Code Agent
      ↓ (bedient)
agency-cli / REST API
      ↓ (orchestriert)
Jupyter Notizbücher (Papermill)
      ├── Web-Search (Claude API)
      ├── Code-Scan (Tools: eslint, flake8, bandit)
      └── Report-Generation (Synthese)
      ↓ (gibt zurück)
JSON/Markdown Output
      ↓ (Agent interpretiert)
Nächste Steps
```

---

## 📦 Installation

```bash
# 1. Requirements installieren
pip install -r requirements.txt

# 2. Verzeichnisse erstellen
mkdir -p notebooks projects

# 3. Fertig!
```

---

## 🚀 Verwendung

### Option 1: CLI (für Claude Code / Menschen)

```bash
# Neues Projekt starten
python cli/main.py run acme-corp \
  --notebook analysis \
  --request "Unsere Django-App ist langsam" \
  --tech-stack django \
  --code-path ./acme_code

# Status checken
python cli/main.py status acme-corp-20251110_143000

# Verfügbare Notizbücher auflisten
python cli/main.py list-notebooks

# API Server starten
python cli/main.py serve --port 5000
```

### Option 2: REST API (für Agents)

```bash
# Start server
python cli/main.py serve --port 5000
```

**Endpoints:**

```bash
# Health Check
GET /health
→ {"status": "healthy"}

# Run workflow
POST /api/v1/run
{
  "notebook_type": "analysis",
  "project_name": "acme-corp",
  "client_request": "Our Django app is slow",
  "tech_stack": "django",
  "code_path": "/path/to/code"
}
→ {
    "status": "success",
    "project_id": "acme-corp-20251110_143000",
    "executed_notebook": "...",
    "outputs": {...}
  }

# Get status
GET /api/v1/status/acme-corp-20251110_143000
→ {...}

# List notebooks
GET /api/v1/list-notebooks
→ {"notebooks": [...]}
```

### Option 3: Python SDK (für eigene Scripts)

```python
from orchestrator.core import NotebookOrchestrator

orchestrator = NotebookOrchestrator("./notebooks", "./projects")

result = orchestrator.run(
    notebook_type="analysis",
    project_name="acme-corp",
    client_request="Our Django app is slow",
    code_path="/path/to/code",
    tech_stack="django"
)

print(result["status"])  # "success" or "error"
print(result["project_id"])  # "acme-corp-20251110_143000"
print(result["outputs"])  # Extracted outputs from notebook
```

---

## 📚 Notizbuch-Templates

Die Notizbücher sind die **ausführbare Dokumentation** deiner Agentur.

### Verfügbare Templates

```
notebooks/
├── analysis_workflow.ipynb          # Research → Validation → Report
├── code_generation_workflow.ipynb   # Feature → Code → Tests
└── legacy_refactoring_workflow.ipynb # Assessment → Plan → Execution
```

### Struktur eines Notizbuchs

Alle Notizbücher folgen diesem 4-Phasen-Modell:

```
1. Semantic Understanding
   └─ Parse client request → Identify knowledge gaps
   
2. Knowledge Acquisition
   └─ Web search → Research → Document findings
   
3. Data-Driven Validation
   └─ Run tools (eslint, flake8, bandit) → Get raw outputs
   
4. Report Generation
   └─ Synthesize → Create professional deliverable
```

### Beispiel: `analysis_workflow.ipynb`

Phase 1: Semantic Understanding
```python
semantic_analysis = {
    "raw_request": "Django app is slow",
    "identified_problem": "Performance issue",
    "tech_stack": "django",
    "risks": ["Code quality unknown", "Dependencies unknown"]
}
```

Phase 2: Knowledge Acquisition
```python
research_plan = {
    "queries": [
        "Django performance optimization 2024",
        "Django profiling tools",
        "Database optimization"
    ]
    # Würde echte Web-Suchen machen
}
```

Phase 3: Data-Driven Validation
```python
# Führt Tools aus und speichert Outputs
validation_results = {
    "tool": "flake8",
    "metrics": {"code_quality_issues": 12, ...}
}
```

Phase 4: Report Generation
```python
report = """
# Analysis Report

## Findings
1. Problem identified
2. Root causes
3. Recommendations

## Estimated Effort
- Phase 1: 2 days
- Phase 2: 4 days
- Phase 3: 1 day
"""
```

---

## 🔧 Eigene Notizbücher erstellen

1. **Neue Datei**: `notebooks/my_workflow.ipynb`

2. **Parameter-Zelle** (am Anfang):
```python
# Tags: ["parameters"]
project_name = "default"
client_request = ""
code_path = ""
tech_stack = "unknown"
```

3. **Normale Code-Zellen**: Deine Logik

4. **Outputs speichern**: 
```python
# Ergebnisse als JSON/Markdown
output = {"key": "value"}
print(output)  # oder: display(output)
```

5. **Via CLI aufrufen**:
```bash
python cli/main.py run my-project \
  --notebook my_workflow \
  --request "..." \
  --tech-stack django
```

---

## 🤖 Integration mit Claude Code

**Beispiel: Claude Code bedient die CLI**

```python
# In Claude Code:
import subprocess
import json

# Starte Workflow
result = subprocess.run([
    "python", "cli/main.py", "run", "acme-corp",
    "--notebook", "analysis",
    "--request", "Our app is slow",
    "--tech-stack", "django",
    "--output-format", "json"
], capture_output=True, text=True)

output = json.loads(result.stdout)

# Agent kann jetzt die Outputs interpretieren
if output["status"] == "success":
    project_id = output["project_id"]
    findings = output["outputs"]
    
    # Claude Code kann Synthese durchführen
    # und nächste Steps entscheiden
```

**Oder via API:**

```python
import requests

# POST /api/v1/run
response = requests.post("http://localhost:5000/api/v1/run", json={
    "notebook_type": "analysis",
    "project_name": "acme-corp",
    "client_request": "Our app is slow",
    "tech_stack": "django",
    "code_path": "/path/to/code"
})

result = response.json()
# Agent verarbeitet result...
```

---

## 📊 Projekt-Struktur

```
projects/
└── acme-corp-20251110_143000/
    ├── analysis_workflow_executed.ipynb  # Ausgeführtes Notizbuch
    ├── parameters.json                   # Eingabe-Parameter
    ├── report.md                         # Generierter Report
    └── scan_results.json                 # Tool-Outputs (wenn applicable)
```

---

## ⚙️ Konfiguration

### Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-...  # Für Web-Search via Claude API
NOTEBOOKS_DIR=./notebooks
PROJECTS_DIR=./projects
API_PORT=5000
API_HOST=0.0.0.0
```

### Tool-Konfiguration

**Für verschiedene Tech-Stacks:**

```python
# config/tool_config.py
TECH_TOOLS = {
    "django": ["flake8", "bandit", "pylint"],
    "react": ["eslint", "prettier", "npm audit"],
    "node": ["eslint", "npm audit", "snyk"]
}
```

---

## 🚦 Status & Fehlerbehandlung

**Erfolgreiche Ausführung:**
```json
{
  "status": "success",
  "project_id": "acme-corp-20251110_143000",
  "executed_notebook": "...",
  "outputs": {...},
  "metadata": {...}
}
```

**Fehler:**
```json
{
  "status": "error",
  "project_id": "acme-corp-20251110_143000",
  "error": "Notebook execution failed",
  "error_type": "RuntimeError"
}
```

---

## 🎯 Use Cases

### Use Case 1: Performance Analysis
```bash
python cli/main.py run acme-corp \
  --notebook analysis \
  --request "Django app is slow" \
  --tech-stack django \
  --code-path ./acme_code
```

### Use Case 2: Legacy Code Assessment
```bash
python cli/main.py run old-project \
  --notebook legacy_refactoring \
  --request "Need to modernize codebase" \
  --tech-stack django \
  --code-path ./legacy_code
```

### Use Case 3: Feature Planning
```bash
python cli/main.py run new-feature \
  --notebook code_generation \
  --request "Build user authentication" \
  --tech-stack react
```

---

## 📈 Erweiterung

### Neues Notizbuch hinzufügen

1. Erstelle `notebooks/my_workflow.ipynb`
2. Implementiere 4 Phasen
3. Fertig – CLI findet es automatisch

### Neue Tools integrieren

1. Update `config/tool_config.py`
2. Notizbuch führt Tool aus: `subprocess.run([...])`
3. Ergebnisse speichern

### Neue LLM-Integrationen

1. In Notizbuch-Phase 2 (Knowledge Acquisition):
```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4",
    messages=[{"role": "user", "content": "..."}]
)
```

2. Web-Search:
```python
response = client.messages.create(
    model="claude-opus-4",
    messages=[...],
    tools=[{"type": "web_search", ...}]
)
```

---

## 🐛 Debugging

**Notizbuch-Ausführung debuggen:**

```bash
# Verbose Output
papermill --debug notebooks/analysis_workflow.ipynb projects/test/output.ipynb --parameters project_name test

# Oder direkt in Python
import papermill as pm
pm.execute_notebook(
    "notebooks/analysis_workflow.ipynb",
    "projects/test/output.ipynb",
    parameters={...},
    kernel_name="python3"
)
```

**API-Fehler:**

```bash
# API im Debug-Mode starten
python cli/main.py serve --port 5000
# Flask zeigt detaillierte Fehler

# Oder Logs checken
tail -f projects/*/error.log
```

---

## 📝 License

MIT – Frei verwendbar für deine Agentur.

---

## 🤝 Support

**Probleme?**

1. Check das ausgeführte Notizbuch: `projects/*/analysis_workflow_executed.ipynb`
2. API Logs ansehen
3. Parameters prüfen: `projects/*/parameters.json`

**Neue Features?**

Neues Notizbuch erstellen oder `cli/main.py` erweitern.

