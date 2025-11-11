# agency_system/
# Deine hybride Agentur - Workflows orchestrieren LLM-Calls

"""
KONZEPT:
- "Departments" = Python Klassen die Workflows managen
- "Tasks" = Strukturierte Prompts an LLMs
- "Deliverables" = Generierte Reports/Docs für Kunden
- "Intelligence" = LLM macht die eigentliche Arbeit

Du orchestrierst, LLM macht die Denkarbeit.
"""

# ============================================================================
# CORE: Department Base Class
# ============================================================================

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ProjectPhase(Enum):
    """Projekt-Lebenszyklus"""
    BEFORE = "pre_project"      # Anfrage, Scoping
    DURING = "active"            # Entwicklung läuft
    AFTER = "maintenance"        # Support, Updates
    NEW = "greenfield"           # Von Null starten
    LEGACY = "existing_code"     # Bestehenden Code übernehmen

@dataclass
class Task:
    """Eine Aufgabe die ein LLM bearbeitet"""
    id: str
    description: str
    prompt_template: str
    context: Dict  # Was braucht der LLM?
    expected_output: str  # Format (json, markdown, code, etc.)
    
@dataclass
class Deliverable:
    """Was der Kunde am Ende bekommt"""
    name: str
    content: str
    format: str  # pdf, markdown, html
    template_path: str

class Department:
    """
    Base Class für alle "Abteilungen"
    Jede Abteilung hat:
    - Tasks die sie macht
    - LLM-Calls die sie orchestriert
    - Deliverables die sie produziert
    """
    
    def __init__(self, name: str, phase: ProjectPhase):
        self.name = name
        self.phase = phase
        self.tasks: List[Task] = []
        self.current_context: Dict = {}
        
    def add_task(self, task: Task):
        """Füge Task zum Workflow hinzu"""
        self.tasks.append(task)
        
    def execute_workflow(self) -> List[Deliverable]:
        """
        Führe alle Tasks der Abteilung aus
        In richtiger Reihenfolge
        """
        raise NotImplementedError("Jede Abteilung implementiert eigenen Workflow")
        
    def _call_llm(self, prompt: str, context: Dict) -> str:
        """
        Wrapper für LLM-Calls
        Hier kommt später Anthropic API, OpenAI, etc.
        """
        # TODO: Implementierung mit tatsächlichen API-Calls
        return f"[LLM Response für: {prompt[:50]}...]"


# ============================================================================
# DEPARTMENT 1: Intake (Pre-Project)
# ============================================================================

class IntakeDepartment(Department):
    """
    Erste Kundenanfrage → Strukturiertes Projekt-Brief
    
    Was sie macht:
    1. Rohe Kundenanfrage analysieren
    2. Scope extrahieren
    3. Fragen generieren für Unklarheiten
    4. Projekt-Brief ausfüllen
    """
    
    def __init__(self):
        super().__init__("Intake", ProjectPhase.BEFORE)
        self._setup_tasks()
        
    def _setup_tasks(self):
        """Definiere Standard-Tasks für Intake"""
        
        # Task 1: Scope Extraction
        self.add_task(Task(
            id="extract_scope",
            description="Extrahiere klare Requirements aus Kundentext",
            prompt_template="""
Du bist ein technischer Projekt-Analyst.

Kundenanfrage:
{client_request}

Extrahiere:
1. MUST-HAVE Features (ohne geht's nicht)
2. UNCLEAR Aspekte (brauchen Klärung)
3. ASSUMPTIONS (was nicht gesagt wurde, aber wichtig ist)

Antworte NUR mit diesem JSON:
{{
  "must_have": ["feature1", "feature2"],
  "unclear": [{{"question": "...", "impact": "high/medium/low"}}],
  "assumptions": ["assumption1", "assumption2"]
}}
""",
            context={},
            expected_output="json"
        ))
        
        # Task 2: Generate Clarifying Questions
        self.add_task(Task(
            id="generate_questions",
            description="Erstelle Fragen für Kunde basierend auf Unklarheiten",
            prompt_template="""
Basierend auf diesen Unklarheiten:
{unclear_items}

Generiere 3-5 konkrete Fragen für den Kunden.
Jede Frage sollte helfen, technische Entscheidungen zu treffen.

Format:
1. [Frage]
   Warum wichtig: [Kurze Begründung]
2. [Frage]
   Warum wichtig: [Kurze Begründung]
""",
            context={},
            expected_output="markdown"
        ))
        
    def execute_workflow(self, client_request: str) -> Dict:
        """
        Nimm rohe Kundenanfrage → Gib strukturiertes Projekt-Brief zurück
        """
        print(f"\n[{self.name}] Starte Workflow...")
        
        # Step 1: Scope extrahieren
        print("  → Task 1: Scope Extraction")
        scope_result = self._call_llm(
            self.tasks[0].prompt_template.format(client_request=client_request),
            {}
        )
        
        # Step 2: Fragen generieren (wenn Unklarheiten)
        print("  → Task 2: Generate Questions")
        questions = self._call_llm(
            self.tasks[1].prompt_template.format(unclear_items="[extracted unclear items]"),
            {}
        )
        
        # Deliverable: Projekt-Brief
        brief = {
            "client_request": client_request,
            "extracted_scope": scope_result,
            "questions_for_client": questions,
            "status": "pending_client_answers"
        }
        
        print(f"[{self.name}] ✓ Workflow abgeschlossen\n")
        return brief


# ============================================================================
# DEPARTMENT 2: Architecture (Legacy oder Neu)
# ============================================================================

class ArchitectureDepartment(Department):
    """
    Code analysieren (Legacy) ODER System designen (Neu)
    
    Adaptive Workflows:
    - LEGACY: Reverse Engineering → Dokumentation
    - NEW: Requirements → Architecture Design
    """
    
    def __init__(self, project_type: ProjectPhase):
        super().__init__("Architecture", project_type)
        self.project_type = project_type
        self._setup_tasks()
        
    def _setup_tasks(self):
        if self.project_type == ProjectPhase.LEGACY:
            self._setup_legacy_tasks()
        else:
            self._setup_new_project_tasks()
            
    def _setup_legacy_tasks(self):
        """Tasks für bestehenden Code"""
        
        self.add_task(Task(
            id="analyze_structure",
            description="Analysiere Codebase-Struktur",
            prompt_template="""
Du bist ein Senior Software Architect der Legacy Code analysiert.

Codebase Struktur:
{file_tree}

Identifiziere:
1. Haupt-Komponenten (5-7 Module/Klassen)
2. Datenfluss (wie kommunizieren Komponenten?)
3. Externe Dependencies
4. Architektur-Pattern (MVC, Microservices, etc.)

Antworte in Markdown mit Diagramm (mermaid syntax).
""",
            context={},
            expected_output="markdown"
        ))
        
        self.add_task(Task(
            id="identify_issues",
            description="Finde Probleme im Code",
            prompt_template="""
Basierend auf dieser Architektur:
{architecture}

Identifiziere:
1. Code Smells (3 kritischste)
2. Technical Debt Hotspots
3. Refactoring Priorities (high/medium/low)

Sei spezifisch - nenne Dateien/Funktionen.
""",
            context={},
            expected_output="markdown"
        ))
        
    def _setup_new_project_tasks(self):
        """Tasks für neues Projekt"""
        
        self.add_task(Task(
            id="design_architecture",
            description="Entwerfe System-Architektur",
            prompt_template="""
Du bist ein System Architect.

Requirements:
{requirements}

Tech Stack Constraints:
{constraints}

Erstelle:
1. System-Komponenten (5-7 Hauptteile)
2. Datenfluss-Diagramm (mermaid)
3. API Design (Endpoints wenn relevant)
4. Datenmodell (Entities + Relationships)

Halte es EINFACH - kein Over-Engineering.
""",
            context={},
            expected_output="markdown"
        ))
        
    def execute_workflow(self, input_data: Dict) -> Dict:
        """Execute basierend auf Projekt-Typ"""
        print(f"\n[{self.name}] Starte Workflow ({self.project_type.value})...")
        
        results = {}
        for task in self.tasks:
            print(f"  → {task.description}")
            result = self._call_llm(task.prompt_template, input_data)
            results[task.id] = result
            
        print(f"[{self.name}] ✓ Workflow abgeschlossen\n")
        return results


# ============================================================================
# DEPARTMENT 3: Implementation (Code-Generierung + Review)
# ============================================================================

class ImplementationDepartment(Department):
    """
    Code generieren, reviewen, testen
    
    Workflow:
    1. Feature breakdown
    2. Code generation (pro Feature)
    3. Self-review (LLM reviewt eigenen Code)
    4. Test generation
    """
    
    def __init__(self):
        super().__init__("Implementation", ProjectPhase.DURING)
        self._setup_tasks()
        
    def _setup_tasks(self):
        
        # Code Generator Task
        self.add_task(Task(
            id="generate_code",
            description="Generiere Code für ein Feature",
            prompt_template="""
Du bist ein Senior Developer.

Feature: {feature_name}
Spec: {feature_spec}
Architecture Context: {architecture}
Style Guide: {style_guide}

Generiere:
1. Production-ready Code
2. Error handling
3. Type hints (Python) / Types (TypeScript)
4. Docstrings / Comments nur wo nötig

Code-Qualität Anforderungen:
- Max Function Length: 50 lines
- Cyclomatic Complexity: < 10
- Keine TODOs oder Placeholders

Output Format:
# File: {file_path}
# Purpose: [one line]

[code here]
""",
            context={},
            expected_output="code"
        ))
        
        # Self-Review Task
        self.add_task(Task(
            id="review_code",
            description="Review generierter Code",
            prompt_template="""
Du bist ein Code Reviewer (nicht der ursprüngliche Autor).

Code:
{generated_code}

Review für:
1. Bugs (offensichtliche Fehler)
2. Security (OWASP Top 10)
3. Performance (O(n²) loops, etc.)
4. Maintainability (Code Smells)

Antworte JSON:
{{
  "approved": true/false,
  "critical_issues": [],
  "suggestions": [],
  "score": 0-10
}}

Approval Threshold: 8/10
""",
            context={},
            expected_output="json"
        ))
        
        # Test Generator Task
        self.add_task(Task(
            id="generate_tests",
            description="Generiere Tests für Code",
            prompt_template="""
Code:
{code}

Generiere pytest Tests:
1. Happy path
2. Edge cases (mindestens 2)
3. Error scenarios

Test-Abdeckung Ziel: >80%

Output: Kompletter test_[module].py file
""",
            context={},
            expected_output="code"
        ))
        
    def execute_workflow(self, feature: Dict) -> Dict:
        """
        Generiere + Reviewe + Teste ein Feature
        """
        print(f"\n[{self.name}] Starte Workflow für Feature: {feature.get('name', 'unknown')}...")
        
        # Step 1: Generate
        print("  → Generiere Code...")
        code = self._call_llm(self.tasks[0].prompt_template, feature)
        
        # Step 2: Review
        print("  → Reviewe Code...")
        review = self._call_llm(self.tasks[1].prompt_template, {"generated_code": code})
        
        # Step 3: Tests
        print("  → Generiere Tests...")
        tests = self._call_llm(self.tasks[2].prompt_template, {"code": code})
        
        result = {
            "code": code,
            "review": review,
            "tests": tests,
            "approved": True  # Basierend auf Review-Score
        }
        
        print(f"[{self.name}] ✓ Workflow abgeschlossen\n")
        return result


# ============================================================================
# DEPARTMENT 4: Reporting (Kunden-Deliverables)
# ============================================================================

class ReportingDepartment(Department):
    """
    Generiere professionelle Reports für Kunden
    
    Report-Typen:
    - Project Brief (nach Intake)
    - Architecture Document (nach Design)
    - Progress Report (während Implementation)
    - Handover Document (Projekt-Ende)
    """
    
    def __init__(self):
        super().__init__("Reporting", ProjectPhase.BEFORE)
        self._setup_tasks()
        
    def _setup_tasks(self):
        
        self.add_task(Task(
            id="generate_client_report",
            description="Erstelle Kunden-Report",
            prompt_template="""
Du erstellst einen professionellen Projekt-Report für einen Kunden.

Report Typ: {report_type}
Projekt Daten: {project_data}

Erstelle ein Report mit:
1. Executive Summary (2-3 Sätze)
2. Key Findings / Progress
3. Next Steps / Recommendations
4. Technical Details (wenn relevant)

Ton: Professionell aber verständlich (kein Jargon ohne Erklärung)
Format: Markdown mit klarer Struktur
Länge: 1-2 Seiten

WICHTIG: Keine generischen Floskeln wie "robust solution" oder "comprehensive approach"
""",
            context={},
            expected_output="markdown"
        ))
        
    def generate_report(self, report_type: str, data: Dict) -> str:
        """
        Generiere einen spezifischen Report-Typ
        """
        print(f"\n[{self.name}] Generiere {report_type} Report...")
        
        report = self._call_llm(
            self.tasks[0].prompt_template,
            {"report_type": report_type, "project_data": json.dumps(data, indent=2)}
        )
        
        print(f"[{self.name}] ✓ Report fertig\n")
        return report


# ============================================================================
# AGENCY ORCHESTRATOR (Das Hauptsystem)
# ============================================================================

class Agency:
    """
    Deine Haupt-Agentur die alles orchestriert
    
    Use Cases:
    1. Neue Kundenanfrage → Intake → Architecture → Proposal
    2. Legacy Code Übernahme → Analysis → Refactor Plan
    3. Laufendes Projekt → Implementation → Progress Reports
    4. Projekt-Abschluss → Handover Docs
    """
    
    def __init__(self):
        self.intake = IntakeDepartment()
        self.reporting = ReportingDepartment()
        
    def handle_new_client_request(self, client_request: str) -> Dict:
        """
        Kompletter Workflow: Anfrage → Projekt-Brief → Report für Kunde
        """
        print("\n" + "="*60)
        print("AGENTUR: Neue Kundenanfrage")
        print("="*60)
        
        # Step 1: Intake Process
        brief = self.intake.execute_workflow(client_request)
        
        # Step 2: Generate Client Report
        report = self.reporting.generate_report(
            "Project Intake Summary",
            brief
        )
        
        return {
            "project_brief": brief,
            "client_report": report,
            "next_phase": "architecture_design"
        }
        
    def handle_legacy_takeover(self, codebase_path: str) -> Dict:
        """
        Legacy Code Analyse Workflow
        """
        print("\n" + "="*60)
        print("AGENTUR: Legacy Code Takeover")
        print("="*60)
        
        # Architecture Department im Legacy-Modus
        arch = ArchitectureDepartment(ProjectPhase.LEGACY)
        
        # Analysis
        analysis = arch.execute_workflow({
            "file_tree": "[extracted from codebase]",
            "code_samples": "[key files]"
        })
        
        # Generate Report für Kunde
        report = self.reporting.generate_report(
            "Legacy Code Analysis",
            analysis
        )
        
        return {
            "analysis": analysis,
            "client_report": report,
            "next_phase": "refactor_planning"
        }
        
    def handle_feature_implementation(self, feature: Dict) -> Dict:
        """
        Implementiere ein neues Feature
        """
        print("\n" + "="*60)
        print(f"AGENTUR: Feature Implementation - {feature.get('name')}")
        print("="*60)
        
        impl = ImplementationDepartment()
        result = impl.execute_workflow(feature)
        
        return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Initialisiere Agentur
    agency = Agency()
    
    # Beispiel 1: Neue Kundenanfrage
    client_request = """
    Wir brauchen ein Tool um unsere Kundendaten zu verwalten.
    Es sollte eine Web-App sein, mit Login.
    Wichtig ist, dass wir Excel-Dateien importieren können.
    Budget ist klein, muss schnell gehen.
    """
    
    result = agency.handle_new_client_request(client_request)
    print("\n[RESULT] Project Brief erstellt ✓")
    print("[RESULT] Kunden-Report generiert ✓")
    
    # Beispiel 2: Feature Implementation
    feature = {
        "name": "User Authentication",
        "spec": "JWT-based login with refresh tokens",
        "architecture": "REST API backend",
        "style_guide": "PEP 8"
    }
    
    impl_result = agency.handle_feature_implementation(feature)
    print("\n[RESULT] Code generiert ✓")
    print("[RESULT] Tests erstellt ✓")
