# [DOKUMENTENTITEL]

- **Datum:** `YYYY-MM-DD`
- **Anfrage:** "[Kurze Beschreibung der ursprünglichen Anfrage]"
- **Version:** 1.0

---

## 1. Executive Summary (Zusammenfassung für Manager)

*In 2-3 Sätzen: Was ist die Situation, was empfehlen wir und warum?*

> ...

---

## 2. Methodik & Vorgehen

*Dieser Abschnitt schafft Transparenz und Vertrauen. Er zeigt, DASS und WIE recherchiert und validiert wurde.*

- **Recherche durchgeführt:**
    - [X] offizielle Dokumentationsquellen geprüft
    - [Y] Web-Suchen durchgeführt
    - [Z] Code-Analyse-Tools ausgeführt
    - [N] ähnliche Projekte untersucht
- **Tools verwendet:** `[Tool 1, Tool 2, ...]`
- **Recherche-Datum:** `YYYY-MM-DD`

---

## 3. Befunde (Findings)

*Jeder Befund wird separat aufgeführt und mit Beweisen untermauert.*

### Befund 1: [Titel des Befunds, z.B. "N+1 Query-Problem in Produkt-API"]

**Beweis (Evidence):**
- **Tool-Output:**
  ```
  [Relevanten Tool-Output hier einfügen, z.B. von django-debug-toolbar]
  ```
- **Quelle:** `[URL mit relevantem Zitat, z.B. Link zur Django-Doku über prefetch_related]`
- **Metrik:** `[Tatsächlich gemessene Zahl, z.B. "47 Datenbank-Queries pro Request"]`

**Konfidenz:** HOCH
- **Begründung:** "Problem wurde durch Tool X objektiv gemessen. Lösung wird von 3+ unabhängigen Quellen, inkl. offizieller Doku, bestätigt."

**Empfehlung:** `[Was sollte aufgrund dieses Befunds getan werden?]`

---

### Befund 2: [Titel des Befunds]

**Beweis (Evidence):**
- ...

**Konfidenz:** MITTEL
- **Begründung:** "Behauptung wird von 2 Quellen gestützt, konnte aber nicht durch ein Tool verifiziert werden."

**Empfehlung:** `...`

---

## 4. Empfehlungen & Nächste Schritte

*Eine priorisierte Liste von konkreten, umsetzbaren Handlungsempfehlungen.*

### Priorität 1 (Kritisch)
**Empfehlung:** `[Spezifische Aktion, z.B. "N+1 Queries mittels prefetch_related beheben"]`
**Begründung:** `[Basierend auf Befund 1]`
**Geschätzter Aufwand:** `[X Tage/Wochen]`
- **Basis der Schätzung:** `[Verweis auf 1-2 ähnliche Projekte oder GitHub Issues, die als Referenz dienen]`

### Priorität 2 (Wichtig)
**Empfehlung:** `...`
**Begründung:** `...`
**Geschätzter Aufwand:** `...`
- **Basis der Schätzung:** `...`

---

## 5. Konfidenz-Bewertung & Risiken

*Eine ehrliche Einschätzung der Sicherheit der gesamten Analyse.*

- **Bereiche mit hoher Konfidenz:**
    - `"[Bereich 1]": "Weil durch Tool X bestätigt und von 3+ Quellen gestützt."`
- **Bereiche mit mittlerer Konfidenz:**
    - `"[Bereich 2]": "Nur 2 Quellen gefunden, keine direkte Messung möglich."`
- **Bereiche mit niedriger Konfidenz (Experten-Review nötig):**
    - `"[Bereich 3]": "Kein Tool verfügbar, widersprüchliche Quellen gefunden. Benötigt manuelle Prüfung durch einen Experten."`

---

## 6. Quellenverzeichnis

*Lückenlose Auflistung aller verwendeten Quellen.*

### Offizielle Dokumentation
1. [Technologie-Doku] - [URL] - Abgrufen am: `YYYY-MM-DD`
2. ...

### Web-Recherche
1. [Titel des Artikels/Blog-Posts] - [URL] - Veröffentlicht am: `YYYY-MM-DD`
2. ...

### Tools
1. [Tool-Name] - [Version] - [Link zum Tool]
2. ...

### Vergleichsprojekte
1. [Projekt-Name] - [GitHub/Case-Study URL] - Relevant, weil: `[Grund]`
2. ...

---

## 7. Anhang: Rohe Tool-Outputs

*[Hier die vollständigen, ungekürzten Outputs der Analyse-Tools für maximale Transparenz einfügen.]*
