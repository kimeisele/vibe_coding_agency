# Protokoll 1: Semantisches Verständnis

**Ziel:** Vor jeglicher Arbeit die Anfrage tiefgehend verstehen, Wissenslücken identifizieren und den Recherchebedarf ermitteln.

---

### Schritt 1: Fakten extrahieren

Analysiere die rohe Nutzeranfrage und extrahiere die harten Fakten.

**Beispiel:**
*   **USER SAGT:** "Meine Django App ist langsam"

*   **EXTRAHIERTE FAKTEN:**
    *   **Technologie:** Django
    *   **Problem-Typ:** Performance
    *   **Schweregrad:** Unbekannt
    *   **Kontext:** Unbekannt (Produktion? Lokal? Welche Version?)

---

### Schritt 2: Wissenslücken identifizieren

Was wissen wir NICHT, was aber kritisch für eine qualifizierte Antwort ist?

*   **KRITISCHE UNBEKANNTE:**
    *   [ ] Tech-Stack Version? (Django 2.x vs. 5.x ist ein Riesenunterschied)
    *   [ ] Umgebung? (Lokal/Staging/Produktion)
    *   [ ] Skalierung? (10 Nutzer vs. 10.000 Nutzer)
    *   [ ] Wo genau ist es langsam? (Datenbank-Queries? Template-Rendering? API-Calls?)
    *   [ ] Zeitrahmen? (ASAP vs. 3 Monate)
    *   [ ] Budget? (Beeinflusst die Lösungsvorschläge)

---

### Schritt 3: Klassifizierung & Recherche-Plan

Ordne das Problem einer Kategorie zu und bestimme die notwendigen Wissensdomänen und Recherchen.

*   **PROBLEM-KATEGORIE:** [Performance-Optimierung]

*   **BENÖTIGTE WISSENSDOMÄNEN:**
    *   [Domäne 1: z.B. "Django ORM Optimierung"]
    *   [Domäne 2: z.B. "PostgreSQL Indexing"]
    *   [Domäne 3: z.B. "Caching-Strategien"]

*   **MUSS RECHERCHIERT WERDEN:**
    *   [ ] Offizielle Doks: [Welche?]
    *   [ ] Aktuelle Best Practices: [Suchanfrage, z.B. "Django performance optimization 2024"]
    *   [ ] Häufige Fallstricke: [Suchanfrage, z.B. "common django performance mistakes"]
    *   [ ] Tool-Empfehlungen: [Suchanfrage, z.B. "django profiling tools"]

---

### Schritt 4: Vor-Recherche-Fragen formulieren

Formuliere die Kernfragen, die die Recherchephase beantworten muss. Trenne zwischen technischen Fragen und Validierungsfragen.

*   **TECHNISCHE FRAGEN:**
    *   "Was ist die aktuelle Best Practice für [X] im Jahr [aktuelles Jahr]?"
    *   "Welche Tools existieren, um [PROBLEM] zu detektieren?"
    *   "Was sind die Performance-Benchmarks für [TECHNOLOGIE]?"

*   **VALIDIERUNGSFRAGEN:**
    *   "Wie können wir MESSEN, ob [X] tatsächlich ein Problem ist?"
    *   "Welche Metriken beweisen, dass Lösung [Y] funktioniert?"
    *   "Welche Tools können die Behauptung [Z] validieren?"

---

**Output dieser Phase:** Ein klar definierter Rechercheplan. Erst jetzt beginnt die nächste Phase: Wissenserwerb.
