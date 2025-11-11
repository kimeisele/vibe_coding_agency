# Phase 3: Plan zur datengetriebenen Validierung

**Protokoll:** `../../agency_knowledge_base/01_PROTOCOLS/03_data_driven_validation_protocol.md`
**Datum:** 2025-11-10
**Ziel:** Überprüfung der Annahmen aus Phase 2 durch Ausführung von Analyse-Tools auf der Codebasis des Kunden.

---

### Annahme, die validiert werden muss:
> "Die Implementierung dauert 2-4 Tage, vorausgesetzt die Codebasis hat eine durchschnittliche, professionelle Qualität."

### Validierungs-Schritte:

Um diese Annahme zu prüfen, werden die folgenden Befehle im Hauptverzeichnis des Kundenprojekts ausgeführt. Das Ergebnis jedes Schritts passt unsere ursprüngliche Schätzung an.

**1. Abhängigkeiten prüfen (Veraltungs-Risiko)**
- **Befehl:**
  ```bash
  npm outdated
  ```
- **Was uns das Ergebnis sagt:**
    - **Gutes Zeichen (Schätzung bleibt):** Nur wenige, kleine Versionssprünge bei unkritischen Bibliotheken.
    - **Schlechtes Zeichen (Schätzung erhöht sich):** Wichtige Bibliotheken (wie React, React-Router) sind mehrere Hauptversionen veraltet. Ein Upgrade ist komplex, risikoreich und muss vor der Feature-Implementierung erfolgen.
    - **Impact auf Schätzung:** Ein notwendiges Upgrade einer Kernbibliothek kann die Schätzung um **+1 bis +3 Tage** erhöhen.

**2. Code-Qualität prüfen (Refactoring-Risiko)**
- **Befehl:**
  ```bash
  npx eslint .
  ```
- **Was uns das Ergebnis sagt:**
    - **Gutes Zeichen (Schätzung bleibt):** 0 oder nur eine Handvoll Warnungen.
    - **Schlechtes Zeichen (Schätzung erhöht sich):** Hunderte von Fehlern. Dies deutet auf inkonsistenten Code, mangelnde Standards und wahrscheinlich versteckte Bugs hin. Neuer Code in einer solchen Umgebung zu integrieren ist aufwändig.
    - **Impact auf Schätzung:** Eine hohe Fehlerzahl erfordert initiales Refactoring und erhöht die Schätzung um **+1 bis +2 Tage**.

**3. Testabdeckung prüfen (Regressions-Risiko)**
- **Befehl:**
  ```bash
  npm test -- --coverage
  ```
- **Was uns das Ergebnis sagt:**
    - **Gutes Zeichen (Schätzung bleibt):** Eine Testabdeckung von >70%. Das gibt uns Sicherheit, dass wir beim Hinzufügen neuer Features nicht unbemerkt Altes kaputt machen.
    - **Schlechtes Zeichen (Schätzung erhöht sich):** Eine Abdeckung von <30%. Das bedeutet, fast der gesamte bestehende Code ist ungetestet. Jede Änderung ist hochriskant. Wir müssen nach der Implementierung umfangreiche manuelle Tests durchführen.
    - **Impact auf Schätzung:** Eine niedrige Testabdeckung erhöht den Aufwand für manuelles Testen und die Risikoprävention um **+1 bis +2 Tage**.

---

### Ergebnis dieser Phase:

Nach Ausführung dieser drei Befehle können wir die initiale Schätzung von 2-4 Tagen präzisieren.

**Beispiel-Szenario "Schlechte Qualität":**
- `npm outdated` zeigt, React ist 2 Hauptversionen alt. (+2 Tage)
- `eslint` meldet 500+ Fehler. (+1 Tag)
- `coverage` ist bei 15%. (+1 Tag)

**Neue, validierte Schätzung:** 2-4 Tage (Basis) + 4 Tage (Risikoaufschlag) = **6-8 Tage**.

Dies ist eine Schätzung, die wir gegenüber dem Kunden mit Daten belegen können.
