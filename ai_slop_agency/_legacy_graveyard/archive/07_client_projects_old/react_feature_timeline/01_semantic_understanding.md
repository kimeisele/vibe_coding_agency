# Phase 1: Analyse der Anfrage "React-App Timeline"

**Protokoll:** `../../agency_knowledge_base/01_PROTOCOLS/01_semantic_understanding_protocol.md`
**Datum:** 2025-11-10

---

### 1. Extrahierte Fakten

- **Technologie:** React
- **Anfragetyp:** Neue Features & Zeitschätzung
- **Explizite Constraints:** Keine genannt
- **Impliziter Kontext:** Der Kunde will eine Zahl (die wir aber nicht ohne Weiteres geben können/sollten).

---

### 2. Identifizierte Wissenslücken (Kritische Unbekannte)

Dies ist die Liste der Fragen, die wir dem Kunden stellen müssen, bevor wir überhaupt an eine Schätzung denken können.

**Zum Feature-Umfang:**
- [ ] Welche Features genau werden gewünscht? (User Stories, Mockups, Spezifikationen)
- [ ] Was ist die exakte Definition von "fertig" für jedes Feature?
- [ ] Gibt es eine Priorisierung (Must-have vs. Nice-to-have)?

**Zum technischen Zustand der App:**
- [ ] Haben wir vollen Zugriff auf das GitHub-Repository?
- [ ] Welches React-Framework wird genutzt (Next.js, Remix, Create React App)? Welche Version?
- [ ] Wie ist der Code strukturiert? Gibt es eine Dokumentation?
- [ ] Wie hoch ist die aktuelle Testabdeckung (`test coverage`)?
- [ ] Gibt es einen Linter, und wie viele Fehler/Warnungen zeigt er an?
- [ ] Gibt es einen CI/CD-Prozess?

**Zum Projektkontext:**
- [ ] Wer sind die Stakeholder? Wer trifft Entscheidungen?
- [ ] Was ist der gewünschte Zeitrahmen (realistisches Zieldatum)?
- [ ] Gibt es ein festes Budget?

---

### 3. Klassifizierung & Recherche-Plan

- **Problem-Kategorie:** Projekt-Scoping & Aufwandsschätzung
- **Benötigte Wissensdomänen:**
    - React-Entwicklung
    - Software-Architektur
    - Projektmanagement & agile Schätzmethoden
    - Code-Qualitätsanalyse

- **MUSS RECHERCHIERT WERDEN (vorläufig):**
    - [ ] Tools zur statischen Analyse von React-Code (`eslint`, `prettier`, `jest-coverage`)
    - [ ] Fallstudien zur Entwicklungszeit von vergleichbaren React-Features
    - [ ] Best Practices für Aufwandsschätzungen in agilen Projekten

---

### 4. Vor-Recherche-Fragen

- **Technische Fragen:**
    - "Welche Tools geben schnell einen Überblick über die Code-Qualität einer unbekannten React-Codebasis?"
    - "Wie lange dauert die Implementierung von Feature X (z.B. 'OAuth2-Login') in einer typischen React-App?"
- **Validierungsfragen:**
    - "Welche Metriken (z.B. Code-Komplexität, Testabdeckung) korrelieren am stärksten mit dem zukünftigen Entwicklungsaufwand?"
    - "Wie können wir unsere Zeitschätzung validieren, außer durch 'Bauchgefühl'?"

---

### **Ergebnis dieser Phase:**

Wir können **keine** seriöse Timeline schätzen. Es wäre reines Raten.

**Nächster Schritt:** Dem Kunden eine Liste der offenen Fragen aus Punkt 2 schicken und einen bezahlten **"Technical Assessment Workshop"** vorschlagen, um diese Punkte gemeinsam zu klären und die Codebasis zu analysieren. Erst danach ist eine Schätzung möglich.
