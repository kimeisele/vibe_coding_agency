# REGRESSION PREVENTION PLAN - 2 WOCHEN ROADMAP

**Status:** Starting Now (11. Nov 2025)
**Ziel:** Regressionen SICHTBAR machen + verhindern
**Nicht:** Perfekt Code schreiben, Alles refaktorieren, Theory machen

---

## SITUATION (REALITÄT, NICHT THEORY)

### Was wir WISSEN:
- ✅ 66 Test-Dateien existieren
- ✅ CLI Entry Point (`cli_entrypoint`) existiert
- ❌ Tests hängen oder sind zu langsam → **TEST-INFRASTRUCTURE BROKEN**
- ❌ Unklar: Tests testen Real Code oder nur Mocks
- ❌ Unklar: Was ist der "richtige" Output eigentlich?

### Das EIGENTLICHE Problem:
```
Tests sagen "PASS"
→ Aber in Realität ist Output falsch/unterschiedlich
→ Weil Tests gegen Mocks laufen, nicht gegen Real Data
→ Du merkst Bug erst nach Release
```

---

## PLAN: 2 WOCHEN (KONKRETE TASKS, NICHT BLABLA)

### WOCHE 1: VISIBILITY + QUICK WINS (2-3 Tage)

#### ⚡ TASK 1.1: Smoke Test - "Does basic CLI work?" (30 min)
**Was:** Ein echtes End-to-End Test ohne Mocks
```python
# tests/smoke/test_cli_smoke.py
def test_cli_runs_without_crashing():
    """REALITY CHECK: Does the CLI actually start?"""
    result = subprocess.run(["toolkit", "--help"], capture_output=True)
    assert result.returncode == 0
    assert b"Agency Toolkit" in result.stdout
```

**Warum:** Wenn das nicht läuft, ist alles andere Zeitverschwendung.
**Erfolg:** Green ✅

---

#### ⚡ TASK 1.2: Find ONE Report Output & Save as Golden Master (1-2 Stunden)
**Was:**
1. Einen echten Workflow laufen lassen
2. Output als "This is correct" speichern
3. Snapshot Test schreiben

```python
# tests/regression/test_report_generation.py
def test_report_output_stable():
    """OUTPUT REGRESSION TEST: Did we break the report?"""
    config = load_real_config()
    output = generate_report(config)

    # Compare against golden master
    assert_matches_snapshot(output, "report_golden_master.txt")
```

**Warum:** Sofort sehen wenn Output sich ändert
**Erfolg:** Snapshot existiert + Test läuft

---

#### ⚡ TASK 1.3: Config Loading Test (1-2 Stunden)
**Was:** Test mit REAL Config-Dateien, nicht Mocks
```python
# tests/integration/test_config_loading.py
def test_config_priority_real_files():
    """CONFIG INTEGRATION TEST: Which config wins?"""
    # Create real files
    write_default_config()
    write_user_config()
    write_project_config()

    # Load real
    config = load_config_real()

    # Assert priority: Project > User > Default
    assert config.get("setting_x") == "from_project_config"
```

**Warum:** Config-Bugs sind invisible, das macht sie visible
**Erfolg:** Test läuft, zeigt Config-Verhalten

---

#### ⚡ TASK 1.4: CI Quality Gate Fix (30 min)
**Was:** `.github/workflows/ci.yml` ändern
```yaml
# BEFORE
- name: Quality Audit
  run: radon cc . -a -j
  continue-on-error: true  # ← PROBLEM: Bricht nicht ab

# AFTER
- name: Quality Audit
  run: radon cc . -a --fail-under=5  # ← Jetzt bricht es ab bei Complexity > 5
  continue-on-error: false
```

**Warum:** Zukünftige God-Functions werden sofort erkannt
**Erfolg:** CI schlägt fehl bei Complexity > 5

---

#### ⚡ TASK 1.5: Document the 11 Ignored Linting Rules (1 Stunde)
**Was:** Für jeden `lint.ignore` in `pyproject.toml`:
- Warum ist er ignoriert?
- Ist das bewusst oder Debt?

```
E501 (Line too long)
  → Reason: Will fix in refactor
  → Action: Check if lines are actually refactored

F401 (Unused imports)
  → Reason: Unknown
  → Action: FIX NOW (15 min) or mark as Tech Debt
```

**Erfolg:** Dokumentation + Entscheidung für jeden Rule

---

### WOCHE 2: SYSTEMISCHE PREVENTION (2-3 Tage)

#### ⚡ TASK 2.1: Contract Test - KDAF Orchestrator (2 Stunden)
**Was:** Test der Schnittstelle ohne Mocks
```python
# tests/integration/test_kdaf_orchestrator_contract.py
def test_orchestrator_input_output_contract():
    """API CONTRACT TEST: Orchestrator input/output behavior"""
    # Real input
    input_data = load_real_kdaf_input()

    # Real output
    output = orchestrator.execute(input_data)

    # Contract: Must have these fields, with these types
    assert_has_fields(output, ["status", "results", "timestamp"])
    assert isinstance(output.status, str)
    assert isinstance(output.results, list)
```

**Warum:** Wenn API sich ändert, brechen Tests sofort
**Erfolg:** Test läuft, dokumentiert API-Contract

---

#### ⚡ TASK 2.2: Integration Suite - 3 Critical Workflows (3-4 Stunden)
**Was:** 3 echte, wichtige Workflows testen (ohne Mocks)

```python
# tests/integration/test_critical_workflows.py

def test_workflow_1_full_analysis():
    """CRITICAL WORKFLOW 1: Full code analysis end-to-end"""
    result = run_full_workflow("real_project")
    assert result.success
    assert "report.pdf" in result.outputs

def test_workflow_2_report_generation():
    """CRITICAL WORKFLOW 2: Generate standard report"""
    result = run_report_workflow()
    assert len(result.outputs) > 0

def test_workflow_3_config_inheritance():
    """CRITICAL WORKFLOW 3: Config loading with priority"""
    result = run_with_mixed_configs()
    assert result.config.matches_expected_priority()
```

**Warum:** Real world wird getestet, nicht Mock world
**Erfolg:** 3 Integration Tests grün, zeigen echtes Verhalten

---

#### ⚡ TASK 2.3: Remove Mock Overuse (2-3 Stunden)
**Was:**
- Finde die 5 wichtigsten Mocks
- Entferne sie oder mach sie optional
- Lass Tests gegen Real Daten laufen

```python
# BEFORE
@patch('agency_toolkit.core.orchestrator.execute')
def test_something(mock_execute):
    mock_execute.return_value = {"fake": "data"}
    # Test tests Mock, not Real Code

# AFTER
def test_something():
    real_data = load_test_fixture()
    result = orchestrator.execute(real_data)
    # Test tests Real Code
```

**Erfolg:** Tests laufen gegen Real Code

---

## ERFOLGS-METRIKEN (Wie wir wissen ob's funktioniert)

### Nach WOCHE 1:
- [ ] Smoke Test läuft ✅
- [ ] Golden Master Snapshot existiert ✅
- [ ] Config Test zeigt Priority korrekt ✅
- [ ] CI Quality Gate reagiert auf Code Complexity ✅
- [ ] 11 Linting Rules dokumentiert + Entscheidungen getroffen ✅

### Nach WOCHE 2:
- [ ] Contract Test für Orchestrator grün ✅
- [ ] 3 Integration Tests für Critical Workflows grün ✅
- [ ] 5 Mocks entfernt/optional ✅
- [ ] Wenn Code ändert → Tests zeigen's sofort ✅

---

## REALISTISCHE TIMELINE

```
Tag 1 (2-3 Stunden):
  ✓ Smoke Test schreiben
  ✓ Golden Master speichern
  ✓ CI Quality Gate fixen

Tag 2-3 (2-3 Stunden):
  ✓ Config Test
  ✓ Linting Rules dokumentieren

Tag 4-5 (3-4 Stunden):
  ✓ Contract Tests
  ✓ Integration Tests

Tag 6 (1-2 Stunden):
  ✓ Mocks entfernen
  ✓ Alle zusammen testen
```

**Total:** ~10-15 Stunden über 2 Wochen = **1-2 Stunden pro Tag**

---

## WAS NICHT PASSIERT (noch nicht)

❌ God-Function Refactoring (zu früh)
❌ Tests umschreiben (brauchen wir nicht)
❌ Mutation Testing (später, wenn visibility gut)
❌ Alle Mocks entfernen (nur die schlimmsten)
❌ Neue Features bauen (fokus: Stabilität)

---

## KRITISCHER PUNKT

**Wenn Tests IMMER NOCH hängen:**
→ Wir machen zuerst Task 1.1 (Smoke Test)
→ Wenn der läuft, wissen wir: CLI funktioniert
→ Wenn der hängt, müssen wir erst das fixen

---

## NÄCHSTER SCHRITT

👉 **Jetzt:** Task 1.1 - Smoke Test schreiben
👉 **Dann:** Task 1.2 - Golden Master
👉 **Dann:** Sehen ob's funktioniert

**GO!**
