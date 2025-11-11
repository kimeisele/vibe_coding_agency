# 🏢 AI Agency - Real Consulting Workspace

Ein schlankes CLI-System für strukturierte Softwareentwicklung, wie eine echte Agentur.

## 🎯 Was ist das?

**Nicht:** Ein AI-Automation System
**Sondern:** Ein Arbeitsplatz, der dich bei strukturierter Kundenberatung unterstützt

Du orchestrierst. Die APIs (Google, Mistral) machen die Denkarbeit.

## 🏗️ Struktur

```
agency/
├── cli/
│   ├── __init__.py
│   └── main.py                    # Dein Einstiegspunkt
├── departments/                   # Die Abteilungen
│   ├── __init__.py
│   ├── intake.py                  # Projekte aufnehmen & validieren
│   ├── architecture.py            # Systeme designen
│   ├── implementation.py          # Code planen & generieren
│   └── reporting.py               # Reports für Kunden
├── tools/                         # Externe Integrationen
│   ├── __init__.py
│   ├── llm_client.py              # Google Gemini + Mistral Wrapper
│   ├── web_research.py            # Google Custom Search
│   ├── code_scanner.py            # Code-Analyse Tools
│   └── context_manager.py         # Kontexte verknüpfen
├── models/
│   ├── __init__.py
│   ├── project.py                 # Project Dataclass
│   └── context.py                 # Context Dataclass
├── storage/
│   ├── __init__.py
│   └── local_storage.py           # JSON-basierte Persistenz
├── config/
│   ├── __init__.py
│   └── settings.py                # API Keys, Config
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

```bash
# 1. Setup
cp .env.example .env
# Füge deine API Keys ein (GOOGLE_API_KEY, MISTRAL_API_KEY)

pip install -r requirements.txt

# 2. Neues Projekt starten
python -m agency.cli new my-project --request "Meine App ist langsam"

# 3. Intake durchführen (Projekt-Brief)
python -m agency.cli intake my-project

# 4. Architektur designen
python -m agency.cli architecture my-project

# 5. Implementation planen
python -m agency.cli implementation my-project

# 6. Report generieren
python -m agency.cli report my-project
```

## 🔄 Workflow

```
CLI-Befehl
    ↓
Department (z.B. Intake)
    ↓
Kontext sammeln (lokal gespeicherte Daten + Nutzer-Input)
    ↓
API-Call (Google Gemini / Mistral für LLM, Google Search für Research)
    ↓
Resultat speichern (JSON-Datei)
    ↓
Output an User
```

## 🛠️ Technologie

- **CLI:** Click (Python)
- **LLM:** Google Gemini + Mistral
- **Web Research:** Google Custom Search API
- **Storage:** JSON (lokal)
- **Code Analysis:** Local (eslint, pylint, etc. über subprocess)

## 📝 Beispiel: Neues Projekt

```bash
$ python -m agency.cli new acme-corp --request "Unsere Django-App ist langsam"

✓ Projekt erstellt: acme-corp (ID: 2025-11-10-001)
✓ Kontext initialisiert

Nächster Schritt:
  python -m agency.cli intake acme-corp
```

Der Intake würde dann:
1. Deine Request analysieren
2. Mit Google Gemini Fragen generieren (für Klarheit)
3. Web-Search durchführen (für Context)
4. Einen strukturierten Brief speichern

## 🤝 Integration mit Claude Code

Claude Code kann dein System aufrufen:

```python
from agency.tools.context_manager import ContextManager
from agency.departments.implementation import ImplementationDepartment

# Claude Code sammelt Kontext
ctx = ContextManager.load("my-project")

# Claude Code startet Implementation
impl = ImplementationDepartment(ctx)
result = impl.execute()

# Resultat weiterverarbeiten
print(result.generated_code)
```

## 🔐 Sicherheit

- API Keys in `.env` (Git-ignoriert)
- Keine sensiblen Daten in Logs
- Kontext wird lokal gespeichert

## 📊 Deine APIs

- **Google Gemini:** LLM für Analysis & Planning
- **Google Custom Search:** Research-Phase
- **Mistral:** Alternative LLM (optional)

Du bestimmst, wann welche API genutzt wird.
