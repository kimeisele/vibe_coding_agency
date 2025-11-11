# Vibe Coding Agency - Monorepo

Ein professionelles Beratungs-System für strukturierte Software-Analyse ohne Bullshit.

## Struktur

```
vibe_code_agency/
├── simple_motor/              ← DAS KERNPRODUKT
│   ├── demo.py               (Test-Demo)
│   ├── orchestrator.py        (Startet Workflows)
│   ├── workflow.ipynb         (4-Phase Notebook)
│   ├── PHILOSOPHY.md          (Die 3 Regeln)
│   └── README.md              (Dokumentation)
│
├── agency-system-complete/    ← Alternative: Full API System
│   ├── agency-system/
│   │   ├── cli/
│   │   ├── api/
│   │   ├── orchestrator/
│   │   └── notebooks/
│   └── projects/              (Projektdaten)
│
├── vibe_coding_agency/        ← Alternative: Interactive CLI
│   ├── agency.py              (6-Phase CLI)
│   ├── Masterframework/        (Templates)
│   └── projects/              (Projektdaten)
│
├── agency_knowledge_base/     ← Shared Knowledge
│   ├── 00_THE_CORE_PROTOCOL.md
│   ├── 01_PROTOCOLS/
│   └── 02_TEMPLATES/
│
└── [This repo]
    ├── MONOREPO.md           (This file)
    ├── START_HERE.md         (Quick start)
    ├── SYSTEM_ARCHITECTURE.md (Full explanation)
    └── .gitignore
```

## Quick Start

### Option 1: Simple Motor (Recommended - START HERE!)

```bash
cd simple_motor
python3 demo.py
```

Ergebnis: Report mit echten Findings (kein Bullshit)

### Option 2: Interactive CLI

```bash
cd vibe_coding_agency
python3 agency.py
```

Für Projekte die durch alle 6 Phasen gehen sollen.

### Option 3: REST API

```bash
cd agency-system-complete
python3 agency-system/cli/main.py serve --port 5000
```

Für External Agents (Claude Code, GitHub Actions).

## Was das System macht

**4-Phase Workflow:**
1. **VERSTEHEN** - Parse die Anfrage
2. **RECHERCHIEREN** - Hole externe Quellen
3. **VALIDIEREN** - Führe echte Tools aus
4. **BERICHT** - Generiere Report

**Anti-Bullshit Prinzip:**
- Keine Spekulation
- Nur Fakten mit Belegen
- Jeder Claim wird zitiert oder gemessen

## Echtes Beispiel

Das System analysierte `/Users/ss/projects/ai_slop_agency` und fand:

```
✓ 33 Python Dateien
✓ Bandit Sicherheitsscan ausgeführt
✓ 1 echtes Sicherheitsproblem gefunden:

  Issue: [B104:hardcoded_bind_all_interfaces]
  Location: rest.py:108:30
  Problem: host="0.0.0.0" (bindet auf alle Interfaces)
  CWE: CWE-605
  Severity: Medium
```

Das ist KEIN erfundenes Problem. Bandit hat das wirklich gefunden.

## Die 3 Regeln

1. **VERSTEHEN** - Ohne Annahmen
2. **RECHERCHIEREN** - Mit Quellen
3. **VALIDIEREN** - Mit echten Tools

Wenn du nicht kannst 1+2+3 zu machen → Sagen "wir können es nicht"

## Dateigröße / Token-Verbrauch

- `simple_motor/demo.py` - 4.8KB - ~500 tokens
- `simple_motor/workflow.ipynb` - 6.8KB - ~700 tokens
- Reports sind **dynamisch** (je nach Code-Größe)

Minimal. Effizient. Kein Overhead.

## Verwendung im Team

Jede Person:
1. Cloned das Repo
2. `cd simple_motor`
3. `python3 demo.py` (oder orchestrator.py mit Parametern)
4. Bekommt einen Report

Kein Setup. Kein Bullshit.

## Lizenz

MIT - Mach damit was du willst.

## Support

README-Dateien in jedem Ordner erklären Details.

---

**Vibe Coding Agency**
*Strukturiert. Datengestützt. Defensible.*
