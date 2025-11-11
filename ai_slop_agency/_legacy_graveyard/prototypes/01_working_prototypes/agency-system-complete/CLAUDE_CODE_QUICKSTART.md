# 🚀 Agency System – Claude Code Quick Start

Du willst, dass **Claude Code einen Workflow orchestriert**? Hier ist wie:

---

## 📋 Scenario: Claude Code bedient die Agency CLI

**Was passiert:**
1. Claude Code (Agent) ruft deine CLI auf
2. CLI orchestriert ein Jupyter Notizbuch
3. Notizbuch führt Analysen durch
4. Claude Code bekommt strukturiertes JSON zurück
5. Claude Code interpretiert und entscheidet nächste Steps

---

## 🎯 Schritt-für-Schritt Setup

### 1. Agency System installieren

```bash
# Im deinem Projekt-Verzeichnis
cd /path/to/your/project

git clone <this-repo> agency-system
cd agency-system

# Dependencies
pip install -r requirements.txt
```

### 2. API Server starten (im Terminal / Background)

```bash
# Option A: CLI serve
python cli/main.py serve --port 5000

# Option B: Python direkt
python -c "from api.rest import create_app; app = create_app(); app.run(port=5000)"

# Option C: Gunicorn (Production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "api.rest:create_app()"
```

**Server läuft:** http://localhost:5000

---

## 🔧 Claude Code Integration

### Szenario 1: Workflow via REST API aufrufen

**Claude Code macht:**

```python
import requests
import json

def run_agency_analysis(project_name, client_request, tech_stack="django", code_path=None):
    """Starte eine Agency-Analyse über REST API."""
    
    api_url = "http://localhost:5000/api/v1/run"
    
    payload = {
        "notebook_type": "analysis",
        "project_name": project_name,
        "client_request": client_request,
        "tech_stack": tech_stack,
        "code_path": code_path
    }
    
    print(f"📊 Starting analysis for: {project_name}")
    print(f"Request: {client_request}")
    
    response = requests.post(api_url, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.json()}")
        return None
    
    result = response.json()
    
    if result["status"] == "error":
        print(f"❌ Workflow error: {result['error']}")
        return None
    
    print(f"✅ Analysis complete: {result['project_id']}")
    print(f"Outputs: {json.dumps(result['outputs'], indent=2)}")
    
    return result


# Claude Code benutzt das:
if __name__ == "__main__":
    analysis = run_agency_analysis(
        project_name="acme-corp",
        client_request="Our Django app is slow. Can you help optimize?",
        tech_stack="django",
        code_path="./acme_code"
    )
    
    # Jetzt kann Claude interpretieren
    if analysis:
        # Nächste Steps basierend auf Findings
        findings = analysis["outputs"]
        
        # Claude könnte z.B. sagen:
        # "Die Notizbuch-Analyse zeigt 3 Probleme:
        #  1. N+1 queries in Django
        #  2. Fehlende Datenbank-Indizes
        #  3. Ineffizientes Caching
        #
        # Ich würde folgende nächste Schritte empfehlen..."
```

### Szenario 2: CLI direkt aufrufen (subprocess)

```python
import subprocess
import json

def run_agency_cli(project_name, request, tech_stack="django", code_path=None):
    """Starte eine Agency-Analyse über CLI."""
    
    cmd = [
        "python", "cli/main.py", "run", project_name,
        "--notebook", "analysis",
        "--request", request,
        "--tech-stack", tech_stack,
        "--output-format", "json"
    ]
    
    if code_path:
        cmd.extend(["--code-path", code_path])
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="./agency-system")
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    
    output = json.loads(result.stdout)
    
    print(f"✅ Complete: {output['project_id']}")
    
    return output


# Claude Code nutzt:
if __name__ == "__main__":
    analysis = run_agency_cli(
        project_name="acme-corp",
        request="Our Django app is slow",
        tech_stack="django",
        code_path="./acme_code"
    )
    
    if analysis["status"] == "success":
        # Claude interpretiert Findings...
        pass
```

### Szenario 3: Python SDK direkt

```python
import sys
sys.path.insert(0, "./agency-system")

from orchestrator.core import NotebookOrchestrator

def run_analysis(project_name, request, tech_stack="django", code_path=None):
    """Direkte Integration ohne API/CLI."""
    
    orchestrator = NotebookOrchestrator(
        notebooks_dir="./agency-system/notebooks",
        projects_dir="./agency-system/projects"
    )
    
    result = orchestrator.run(
        notebook_type="analysis",
        project_name=project_name,
        client_request=request,
        code_path=code_path,
        tech_stack=tech_stack
    )
    
    return result


# Nutzen:
analysis = run_analysis(
    project_name="acme-corp",
    request="Our Django app is slow",
    tech_stack="django",
    code_path="./acme_code"
)

print(analysis["status"])  # "success" or "error"
print(analysis["project_id"])  # "acme-corp-20251110_143000"
print(analysis["outputs"])  # Findings aus dem Notizbuch
```

---

## 📊 Workflow: Wie das zusammenhängt

```
Claude Code
    ↓
1. Ruft API auf: POST /api/v1/run
    ↓
2. Server empfängt Request
    ↓
3. Orchestrator lädt Template: analysis_workflow.ipynb
    ↓
4. Papermill injiziert Parameter
    ↓
5. Notizbuch führt 4 Phasen aus:
   a) Semantic Understanding (Parse request)
   b) Knowledge Acquisition (Web-Search via Claude API)
   c) Data-Driven Validation (Run tools like flake8)
   d) Report Generation (Synthesize findings)
    ↓
6. Notizbuch speichert Outputs
    ↓
7. Orchestrator extrahiert Outputs
    ↓
8. Server sendet JSON zurück
    ↓
Claude Code
    ↓
9. Interpretiert Findings
    ↓
10. Entscheidet nächste Steps (weitere Fragen stellen, Support anbieten, etc.)
```

---

## 🎯 Vollständiges Beispiel: "Kunde fragt um Hilfe"

**Szenario:** 
Dein System bekommt eine neue Kundenafrage: "Unsere Django-App ist langsam"

**Claude Code könnte so vorgehen:**

```python
import requests

# 1. Kunde-Input
customer_request = """
Unsere Django-App ist langsam.
Tech Stack: Django + PostgreSQL
Env: 50k daily users
Code: https://github.com/acme/backend
"""

# 2. Analyse via Agency starten
result = requests.post("http://localhost:5000/api/v1/run", json={
    "notebook_type": "analysis",
    "project_name": "acme-corp",
    "client_request": customer_request,
    "tech_stack": "django",
    "code_path": "/tmp/acme_backend_clone"  # Claude könnte vorher geklont haben
}).json()

# 3. Findings extrahieren
if result["status"] == "success":
    findings = result["outputs"]
    
    # 4. Claude synthetisiert
    synthesis = f"""
    ## Analyse abgeschlossen für: {result['project_id']}
    
    ### Gefundene Probleme:
    - N+1 queries identifiziert
    - Fehlende Datenbank-Indizes
    - Caching nicht optimal konfiguriert
    
    ### Empfohlene Nächste Schritte:
    1. Technical Deep-Dive (2 Stunden)
       → Genaue Root-Cause Analyse
    
    2. Optimization Sprint (3-5 Tage)
       → Implementierung der Fixes
    
    3. Validation & Deployment
       → Testing, Performance Benchmarks
    
    ### Geschätzter Aufwand: 4-9 Tage
    
    Sollen wir mit Phase 1 starten?
    """
    
    print(synthesis)
    
    # 5. Kunde kann antworten & Projekt läuft weiter
```

---

## ✅ Checkliste: Agency System Setup

- [ ] `agency-system/` in dein Projekt
- [ ] `pip install -r requirements.txt`
- [ ] `python cli/main.py serve --port 5000` starten
- [ ] Test: `curl http://localhost:5000/health` → `{"status": "healthy"}`
- [ ] Claude Code Script oben ausprobieren
- [ ] Notizbuch-Output checken: `agency-system/projects/*/analysis_workflow_executed.ipynb`
- [ ] Production: Mit Gunicorn deployen

---

## 🔍 Debugging

**API nicht erreichbar?**
```bash
# Terminal 1: Server starten
python cli/main.py serve --port 5000

# Terminal 2: Test
curl http://localhost:5000/health
```

**Notizbuch führt nicht aus?**
```bash
# Manuell testen
jupyter notebook notebooks/analysis_workflow.ipynb
# Manuelle Tests durchführen
```

**Claude Code sieht keinen Output?**
```python
# JSON dekodieren
import json
print(json.dumps(result, indent=2))

# Oder Response direkt checken
print(response.status_code)
print(response.text)  # Raw text für Errors
```

---

## 🚀 Nächste Steps

1. **Notizbücher verbessern**
   - Integration echter Web-Search (Claude API)
   - Integration echter Code-Scans (eslint, flake8, etc.)
   - Bessere Report-Templates

2. **Claude Code erweitern**
   - Follow-up Fragen stellen basierend auf Findings
   - Automatische weitere Analysen triggern
   - Kundenkommunikation automatisieren

3. **Production-Ready machen**
   - Authentication (API-Keys)
   - Rate Limiting
   - Monitoring & Logging
   - Error Recovery

---

**Bereit? Los gehts! 🎯**

