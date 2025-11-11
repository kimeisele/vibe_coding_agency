# Protokoll 3: Datengetriebene Validierung

**Ziel:** Behauptungen und Empfehlungen mit harten, messbaren Daten aus echten Tools untermauern. Die Grundregel lautet: **Keine Behauptung ohne Tool-Output oder zitierte Quelle.**

---

### 3.1 Code-Qualitäts-Validierung

*Wenn Code analysiert wird, sind dies die erforderlichen Schritte.*

1.  **Linter ausführen:**
    ```bash
    # Python
    flake8 [files] --max-complexity 10
    # JavaScript
    eslint [files]
    ```
    **Output:** [Tatsächliche Fehler/Warnungen einfügen]

2.  **Security-Scanner ausführen:**
    ```bash
    # Python
    bandit -r [directory]
    # Node
    npm audit
    ```
    **Output:** [Tatsächliche Schwachstellen einfügen]

3.  **Abhängigkeiten prüfen:**
    ```bash
    # Python
    pip-audit
    # Node
    npm outdated
    ```
    **Output:** [Veraltete/verwundbare Pakete einfügen]

4.  **Komplexität messen:**
    ```bash
    # Python
    radon cc [files] -a
    ```
    **Output:** [Komplexitäts-Scores einfügen]

---

### 3.2 Performance-Validierung

*Wenn Performance-Probleme behauptet werden.*

1.  **Anwendungsprofilierung:**
    ```bash
    # Python
    python -m cProfile -o output.prof script.py
    # Node
    node --prof app.js
    ```
    **Output:** [Die langsamsten Funktionen aus dem Profiler-Output einfügen]

2.  **Datenbank-Query-Analyse (Beispiel Django):**
    ```python
    from django.db import connection
    print(connection.queries)
    ```
    **Output:** [Langsame oder übermäßig viele Queries einfügen]

---

### 3.3 Architektur-Validierung

*Wenn eine Architektur empfohlen wird.*

1.  **Finde ähnliche Implementierungen:**
    *   Suche: `"[YOUR_STACK] production architecture"`
    *   Suche: `"[SIMILAR_APP] tech stack case study"`

2.  **Prüfe Skalierbarkeits-Daten:**
    *   Suche: `"[TECH] performance benchmarks"`
    *   Suche: `"[TECH] handles [X] concurrent users"`

3.  **Finde Fehlerfälle/Gegenbeispiele:**
    *   Suche: `"[TECH] limitations"`
    *   Suche: `"when not to use [TECH]"`

---

### 3.4 Zeit- & Kosten-Validierung

*Wenn Schätzungen abgegeben werden.*

1.  **Finde ähnliche Projekte:**
    *   Suche: `"how long to build [FEATURE]"`
    *   Suche: GitHub Repos mit ähnlichem Umfang und prüfe Issues/Commits.

2.  **Finde reale Projektdaten:**
    *   Blog-Posts mit Retrospektiven
    *   Fallstudien mit Zeitangaben

*Regel: Eine Schätzung muss immer auf mindestens 1-2 vergleichbaren Projekten basieren und diese als Quelle nennen.*

---

### Output dieser Phase

Ein **validiertes Set von Befunden**. Jeder Befund ist entweder mit einem Tool-Output oder einer externen Quelle (oder beidem) belegt. Diese Befunde fließen direkt in das finale `research_backed_document` ein.
