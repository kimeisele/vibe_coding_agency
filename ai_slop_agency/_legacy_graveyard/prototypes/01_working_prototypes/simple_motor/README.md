# Simple Motor - Das Minimale System

Ein einzelner, fokussierter Workflow der nie halluziniert.

## Was du brauchst

1. **Das Notebook** (`workflow.ipynb`) - Das Ein-Notebook-System
2. **Den Motor** (`orchestrator.py`) - Startet das Notebook mit Parametern
3. **Die Philosophie** - 3 Regeln, die alles leiten

## Die 3 Anti-Bullshit-Regeln

1. **VERSTEHEN** - Parse die Anfrage, keine Annahmen
2. **RECHERCHIEREN** - Hole echte Daten von außen (Web Search, API docs)
3. **VALIDIEREN** - Führe echte Tools aus (flake8, bandit, etc.), keine Spekulation

## Wie es funktioniert

```
User ruft Motor auf
    ↓
Motor startet Notebook mit Parametern (papermill)
    ↓
Notebook Phase 1: Parse Request
    ↓
Notebook Phase 2: Web Research
    ↓
Notebook Phase 3: Tool Validation
    ↓
Notebook Phase 4: Report
    ↓
Fertig. Keine Halluzinationen.
```

## Los geht's

```bash
python3 orchestrator.py \
    --project "my-audit" \
    --request "Analyze security issues" \
    --code-path "/path/to/code" \
    --tech-stack "python"
```

Das wars. Ein Kommando. Fertig.
