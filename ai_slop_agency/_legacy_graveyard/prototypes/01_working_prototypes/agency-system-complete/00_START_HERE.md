# 🚀 START HERE - Agency System

Du hast ein vollständiges, production-ready System für deine AI-Agentur bekommen.

## ⚡ TL;DR (30 Sekunden)

```bash
# 1. Install
cd agency-system && pip install -r requirements.txt

# 2. Start
python cli/main.py serve --port 5000

# 3. Test (in anderem Terminal)
python -c "
import requests
r = requests.post('http://localhost:5000/api/v1/run', json={
    'notebook_type': 'analysis',
    'project_name': 'test-project',
    'client_request': 'My app is slow'
})
print('Status:', r.json()['status'])
print('Project:', r.json()['project_id'])
"
```

Fertig. Dein System läuft. 🎉

---

## 📚 Was soll ich lesen?

| File | What | Time |
|------|------|------|
| **MANIFEST.md** | Überblick was du bekommen hast | 5 min |
| **EXECUTIVE_SUMMARY.md** | Das System erklären | 10 min |
| **README.md** (in agency-system/) | Wie man es nutzt | 15 min |
| **ARCHITECTURE.md** | Wie es innen funktioniert | 20 min |
| **CLAUDE_CODE_QUICKSTART.md** | Claude Code Integration | 15 min |
| **claude_code_example.py** | Real-world Beispiel | 10 min |

**Minimalist? Nur MANIFEST.md + EXECUTIVE_SUMMARY.md lesen.**

---

## 🎯 Die 3 Wege es zu nutzen

### 1️⃣ **CLI** (für dich als Mensch)
```bash
python cli/main.py run my-project \
  --request "Django app zu langsam" \
  --tech-stack django \
  --code-path ./code
```

### 2️⃣ **REST API** (für Agents / Services)
```bash
curl -X POST http://localhost:5000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 3️⃣ **Python SDK** (für deine Scripts)
```python
from orchestrator.core import NotebookOrchestrator
result = orchestrator.run(...)
```

---

## 💡 Das System im Überblick

```
Dein Kunde: "Meine App ist langsam"
                ↓
Claude Code (Agent) startet Analyse
                ↓
API ruft Notizbuch-Orchestrator auf
                ↓
Papermill injiziert Parameter
                ↓
Jupyter Notizbuch führt 4 Phasen aus:
  1️⃣  Parse Request
  2️⃣  Web Research (Claude API)
  3️⃣  Code Scanning (Tools)
  4️⃣  Report Generieren
                ↓
JSON mit Findings zurück zu Claude Code
                ↓
Claude Code interpretiert + entscheidet nächste Steps
                ↓
Kunde bekommt Proposal + Nächste Steps
```

**Das ist nicht Automation, das ist Augmentation.**
Menschen bleiben im Loop. Deine Expertise ist der Wert.

---

## ✅ Was ist drin?

**Code:**
- `orchestrator/core.py` (252 Lines) - Das Gehirn
- `api/rest.py` (145 Lines) - Die REST API  
- `cli/main.py` (195 Lines) - Die CLI
- **Total: ~600 Lines** (nicht über-engineered!)

**Notebooks:**
- `analysis_workflow.ipynb` - Template für Analysen
  (Und 2 weitere als Vorlage)

**Docs:**
- 4 umfassende Guides
- 1 Working Example
- Full Architecture Documentation

---

## 🔧 Schneller Start (5 Minuten)

```bash
# 1. In den Ordner
cd agency-system

# 2. Dependencies
pip install -r requirements.txt

# 3. Server starten
python cli/main.py serve --port 5000

# 4. In anderem Terminal testen
# a) Health Check
curl http://localhost:5000/health

# b) Workflow starten
python cli/main.py run test-project \
  --request "Django app optimization needed" \
  --tech-stack django

# 5. Status checken
python cli/main.py status test-project-20251110_143000
```

---

## 🎯 Was du damit bauen kannst

**Scenario 1: Auto-Proposal-Generator**
```
Customer schreibt: "Meine App ist langsam"
  ↓
Du (als Agent) startest Analyse
  ↓
30 Minuten später: Professionelle Proposal
  ↓
Customer bekommt Angebot
```

**Scenario 2: Batch Analysis**
```
Du hast 10 Kundenprobleme
  ↓
Du startst 10 Analysen parallel
  ↓
Am nächsten Morgen: 10 fertige Reports
```

**Scenario 3: Smart Routing**
```
Customer Request kommt rein
  ↓
System analysiert Anfrage
  ↓
Routed zu richtigem Expert
  ↓
Expert bekommt strukturierte Findings
```

---

## 🚨 Falls etwas nicht klappt

**API startet nicht:**
```bash
# Alle Dependencies installiert?
pip install -r requirements.txt

# Python 3.9+?
python --version

# Port 5000 frei?
lsof -i :5000
```

**Notizbuch führt nicht aus:**
```bash
# Manuell testen
jupyter notebook notebooks/analysis_workflow.ipynb
```

**JSON Fehler:**
```bash
# Flag vergessen?
python cli/main.py run ... --output-format json
```

---

## 📊 Nächste Schritte

### Heute (nächste Stunde)
- [ ] Installation
- [ ] Test: `curl http://localhost:5000/health`
- [ ] Ein Workflow starten
- [ ] Output anschauen

### Diese Woche
- [ ] Notizbuch editieren
- [ ] Claude Code Integration
- [ ] Erste echte Analyse
- [ ] Production Setup planen

### Nächste Woche  
- [ ] 2-3 weitere Workflows hinzufügen
- [ ] Mit echten Kunden testen
- [ ] Deployment

### Nächster Monat
- [ ] Team Training
- [ ] Webhooks / Integrations
- [ ] Advanced Features

---

## 💬 Key Insights

1. **"Schlank ist besser als komplex"**
   - 600 Lines Production Code
   - Leicht zu verstehen
   - Leicht zu ändern

2. **"Menschen > Automation"**
   - Dein System augmentiert, ersetzt nicht
   - Synthese bleibt menschlich
   - Explainability durch Notizbücher

3. **"Skalierung durch Templates"**
   - Neue Workflows = Neue Notizbücher
   - Kein Code-Schreiben nötig
   - Team kann selbst erweitern

4. **"Audit Trail ist built-in"**
   - Jedes Projekt speichert sein Notizbuch
   - Du kannst später exakt sehen was passiert ist
   - Compliance-freundlich

---

## 📞 Support / Questions?

**Debugging:**
- Check: `agency-system/projects/*/analysis_workflow_executed.ipynb`
- Das ist das echte Notizbuch mit allen Outputs

**Learning:**
1. Lese MANIFEST.md (was du hast)
2. Lese EXECUTIVE_SUMMARY.md (wie es funktioniert)
3. Lese README.md (wie man es nutzt)
4. Lese ARCHITECTURE.md (wie es designed ist)
5. Runne claude_code_example.py (live sehen)

---

## 🎉 TL;DR für die Ungeduld

✅ Du hast ein production-ready System
✅ 5 Minuten bis es läuft
✅ 250 Lines Kerncode (schlank!)
✅ Für Agents (Claude Code) gebaut
✅ Vollständig dokumentiert
✅ Mit Beispielen
✅ Mit REST API
✅ Mit CLI
✅ Erweiterbar

**Los gehts!** 🚀

---

Next file: `MANIFEST.md`
