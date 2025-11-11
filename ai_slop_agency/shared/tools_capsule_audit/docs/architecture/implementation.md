## Blueprint → Implementierungs-Tasks

Dieser Plan ist in Phasen unterteilt, um die Komplexität zu managen. Jede Phase baut auf der vorherigen auf.

### Phase 1: Das Fundament (Kernsysteme & Modelle)

**Ziel:** Aufbau der Infrastruktur und der zentralen Datenstrukturen, bevor irgendeine Logik implementiert wird.

1.  **Projektstruktur aufsetzen:**
    * Erstellen Sie die gesamte Verzeichnisstruktur wie in `project_structure` definiert (alle `src/meta_audit/*`, `tests/*`, `config/*`).
    * Erstellen Sie `pyproject.toml` mit den `stdlib` und `external_required` Abhängigkeiten (typer, pydantic, pyyaml, rich).
    * Erstellen Sie die `config/defaults.yaml`-Datei mit der in `improved_config_system.schema_example` gezeigten Struktur.

2.  **Pydantic-Modelle implementieren (`src/meta_audit/core/models.py`):**
    * Implementieren Sie das `ProjectCapsule`-Modell (Version 2) gemäß `behavior_specifications.capsule_versioning`.
    * Implementieren Sie das `AnalysisResult`-Modell gemäß `improved_analyzer_model.result_model`.
    * Definieren Sie die Enums für `Category` und `Severity` (oder verwenden Sie `str` wie im Blueprint).

3.  **Hierarchisches Config-System bauen (`src/meta_audit/core/config.py`):**
    * Implementieren Sie die Lade-Logik, die die in `improved_config_system.hierarchy` definierte Auflösungsreihenfolge (Defaults, System, User, Project, Env, CLI) respektiert.
    * Die Funktion (z.B. `load_config()`) sollte ein validiertes Pydantic-Config-Objekt zurückgeben (basierend auf dem Schema).

4.  **Logging-System einrichten (`src/meta_audit/logging/instrumentation.py`):**
    * Erstellen Sie eine `setup_logging`-Funktion, die globale Flags (`--verbose`, `--debug`) aus dem CLI-Kontext (z.B. einem `typer.Context`) entgegennimmt und den globalen Logger entsprechend konfiguriert (Level, Format).

---

### Phase 2: Die Kernfunktionalität (Kapseln & Analyzer-Registrierung)

**Ziel:** Die Basisfunktionen des Tools (Daten rein, Plug-ins laden) implementieren.

1.  **Kapsel-Erstellung (`src/meta_audit/core/capsule.py`):**
    * Implementieren Sie die `create_capsule`-Logik.
    * Stellen Sie sicher, dass die Kapsel-Version (`current_version: 2`) in die Metadaten geschrieben wird.
    * Implementieren Sie die `--content-mode full|signature` Logik.
    * Implementieren Sie die Fehlerbehandlung für Encoding, Symlinks und Dateigrößen-Limits (aus dem Config-Objekt).

2.  **Analyzer-Registrierung (`src/meta_audit/analyzers/registry.py`):**
    * Erstellen Sie den `@register_analyzer` Decorator.
    * Erstellen Sie eine globale Registry (z.B. ein Dictionary), in der der Decorator die Analyzer-Klassen ablegt.
    * Erstellen Sie eine Funktion `get_analyzers(config)`, die alle registrierten Analyzer zurückgibt, die im Config-Objekt als "enabled" markiert sind.

3.  **Analyzer-Basisklassen (`src/meta_audit/analyzers/base.py`):**
    * Erstellen Sie die `PatternAnalyzer` ABC (Abstract Base Class).
    * Stellen Sie sicher, dass sie die in `improved_analyzer_model.base_class_enhancement` definierten Felder (name, category, description) erzwingt.
    * Definieren Sie die `analyze(self, capsule: ProjectCapsule) -> list[AnalysisResult]` als abstrakte Methode.

4.  **Basis-CLI implementieren (`src/meta_audit/cli/main.py`):**
    * Richten Sie die Haupt-`typer.Typer`-App ein.
    * Fügen Sie die globalen Flags (`--config-path`, `--verbose`, `--debug`) hinzu und übergeben Sie deren Werte an die Config- und Logging-Systeme.
    * Fügen Sie die Sub-Commands aus `cli/commands/*.py` hinzu.

---

### Phase 3: Die Anwendungslogik (Analysieren & Berichten)

**Ziel:** Das Tool "lebendig" machen, indem die Analyzer und Berichte implementiert werden.

1.  **Erste Analyzer implementieren (`src/meta_audit/analyzers/implementations/`):**
    * Erstellen Sie `god_modules.py`, `magic_numbers.py` und `error_handling.py`.
    * Jede Klasse muss von `PatternAnalyzer` erben, den `@register_analyzer` Decorator verwenden und die `analyze`-Methode implementieren.
    * Die `analyze`-Methode muss eine Liste von `AnalysisResult`-Pydantic-Modellen zurückgeben.

2.  **Single Project Analyse (`src/meta_audit/cli/commands/analyze.py`):**
    * Implementieren Sie den `analyze project` Befehl.
    * Logik: 1. `create_capsule()` aufrufen. 2. `get_analyzers()` aufrufen. 3. Kapsel durch alle aktivierten Analyzer laufen lassen. 4. Ergebnisse sammeln. 5. Ergebnisse an `generators/report.py` übergeben.

3.  **Berichtsgenerierung (Single) (`src/meta_audit/generators/report.py`):**
    * Erstellen Sie eine Funktion `generate_report(results: list[AnalysisResult])`.
    * Diese Funktion aggregiert die Ergebnisse (z.B. Zählung nach Severity, Kategorie).
    * Implementieren Sie die Ausgabe als `rich.Table` für die Konsole und als YAML/JSON-Export.

4.  **Corpus-Analyse & Cross-Project (`src/meta_audit/cli/commands/analyze.py` & `generators/report.py`):**
    * Implementieren Sie den `analyze corpus` Befehl.
    * Logik: 1. Lade alle Kapseln aus dem Verzeichnis (parallel, wenn möglich). 2. Behandle Kapsel-Versionierung (überspringe v1). 3. Führe die Analyse (wie bei Single Project) für *jede* Kapsel durch. 4. Sammle *alle* Ergebnisse aller Kapseln.
    * Erweitern Sie `generators/report.py`, um `generate_corpus_report` zu implementieren.
    * Implementieren Sie die Cross-Project-Aggregationslogik (z.B. "Pattern 'god-module-large' gefunden in 8 von 10 Projekten") basierend auf den Config-Schwellwerten (`cross_project_pattern_min_projects`).

---

### Phase 4: Tests & Robustheit (Qualitätssicherung)

**Ziel:** Sicherstellen, dass die implementierte Logik korrekt, robust und performant ist.

1.  **Unit-Tests (`tests/unit/`):**
    * Implementieren Sie `test_config_hierarchy.py`: Testen Sie, dass CLI-Flags die Env-Vars überschreiben, die User-Config überschreiben, usw.
    * Implementieren Sie `test_capsule_versioning.py`: Testen Sie, dass eine v1-Kapsel korrekt übersprungen wird oder eine Warnung auslöst.
    * Testen Sie die Analyzer-Logik isoliert.

2.  **Integrations-Tests (`tests/integration/`):**
    * Verwenden Sie `typer.testing.CliRunner`.
    * Implementieren Sie `test_cli_capsule.py`: Testen Sie `meta-audit capsule create ... --content-mode signature` und prüfen Sie die erstellte Datei.
    * Implementieren Sie `test_cli_analyze.py`: Testen Sie `meta-audit analyze corpus ... --filter category:security` und prüfen Sie die YAML/JSON-Ausgabe.
    * Implementieren Sie `test_corpus_cross_project.py` mit 3+ Test-Kapseln, um die Cross-Project-Logik zu validieren.

3.  **Performance-Tests (`tests/performance/`):**
    * (Optional, aber empfohlen) Implementieren Sie `test_large_capsule_performance.py` (z.B. mit `pytest-benchmark`), um die Analyse einer 100MB-Kapsel zu messen.

---

### Phase 5: Refinement & Zukünftige Erweiterungen

**Ziel:** Implementierung der "Nice-to-have"-Features und Vorbereitung für zukünftige Module.

1.  **Report-Befehle (`src/meta_audit/cli/commands/report.py`):**
    * Implementieren Sie `report view` (zeigt einen existierenden YAML/JSON-Bericht hübsch an).
    * Implementieren Sie `report export --format html` (kann zunächst ein Platzhalter sein oder eine sehr einfache HTML-Tabelle generieren).
    * Implementieren Sie `report compare` (zum Vergleichen von zwei Berichtsdateien).

2.  **Vorbereitung für Erweiterungen:**
    * Stellen Sie sicher, dass die `@register_analyzer`-Dokumentation klar ist.
    * Fügen Sie Platzhalter für zukünftige Analyzer (z.B. `llm_analyzer.py`) oder Exporter (`html_exporter.py`) hinzu, um die Architektur zu demonstrieren.