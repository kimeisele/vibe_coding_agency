#!/usr/bin/env python3
"""
BEISPIEL: Wie Claude Code die Agency nutzt

Scenario: Ein Customer fragt um Hilfe bei seiner Django-App
Claude Code orchestriert die komplette Analyse
"""

import requests
import json
import subprocess
from pathlib import Path
from datetime import datetime


# ============================================================================
# Szenario 1: REST API Approach (empfohlen für Remote Setup)
# ============================================================================

class AgencyClient:
    """Client für Agency System REST API."""
    
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def health_check(self):
        """Check ob API erreichbar."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_analysis(self, project_name, request, tech_stack="django", code_path=None):
        """Starte eine Analyse."""
        
        payload = {
            "notebook_type": "analysis",
            "project_name": project_name,
            "client_request": request,
            "tech_stack": tech_stack
        }
        
        if code_path:
            payload["code_path"] = code_path
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/run",
                json=payload,
                timeout=600  # 10 Minuten max
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except requests.exceptions.Timeout:
            return {"status": "error", "error": "Request timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_status(self, project_id):
        """Hole Status eines Projekts."""
        response = requests.get(f"{self.api_url}/api/v1/status/{project_id}")
        return response.json()
    
    def list_notebooks(self):
        """Liste verfügbare Notizbücher."""
        response = requests.get(f"{self.api_url}/api/v1/list-notebooks")
        return response.json()


# ============================================================================
# Szenario 2: CLI Approach (für Local/Direct Integration)
# ============================================================================

class CliRunner:
    """Führt Agency CLI Befehle aus."""
    
    def __init__(self, agency_dir="./agency-system"):
        self.agency_dir = Path(agency_dir)
    
    def run_analysis(self, project_name, request, tech_stack="django", code_path=None):
        """Führe CLI-Befehl aus."""
        
        cmd = [
            "python", "cli/main.py", "run", project_name,
            "--notebook", "analysis",
            "--request", request,
            "--tech-stack", tech_stack,
            "--output-format", "json"
        ]
        
        if code_path:
            cmd.extend(["--code-path", code_path])
        
        print(f"🚀 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.agency_dir),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Timeout"}
        except json.JSONDecodeError:
            return {"status": "error", "error": "Invalid JSON output"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ============================================================================
# Hauptlogik: Claude Code orchestriert die Agency
# ============================================================================

def main():
    """
    Hauptflow: Customer hat Problem, Claude Code analysiert + empfiehlt.
    """
    
    print("=" * 70)
    print("🏢 Agency System - Claude Code Integration Example")
    print("=" * 70)
    print()
    
    # ========================================================================
    # SCHRITT 1: Customer Request
    # ========================================================================
    
    customer_message = """
    Hey, unsere Django-App wird immer langsamer.
    Wir haben etwa 50k daily users und die Response Times sind schon über 2 Sekunden.
    
    Stack: Django + PostgreSQL + Redis
    Environment: AWS (EC2 + RDS)
    
    Können Sie mir helfen?
    """
    
    print("📨 Customer Message:")
    print(customer_message)
    print()
    
    # ========================================================================
    # SCHRITT 2: Claude Code analysiert mit Agency
    # ========================================================================
    
    print("🔄 Initiating Agency Analysis...")
    print()
    
    # Option A: REST API
    client = AgencyClient(api_url="http://localhost:5000")
    
    # Erst Health Check
    if not client.health_check():
        print("❌ Agency API not available. Start with: python cli/main.py serve --port 5000")
        return
    
    # Dann Analysis starten
    result = client.run_analysis(
        project_name="customer-django-perf",
        request=customer_message,
        tech_stack="django",
        code_path=None  # In echtem Szenario: Path zu Customer Repo
    )
    
    if result["status"] != "success":
        print(f"❌ Analysis failed: {result.get('error')}")
        return
    
    project_id = result["project_id"]
    outputs = result["outputs"]
    
    print(f"✅ Analysis Complete: {project_id}")
    print()
    
    # ========================================================================
    # SCHRITT 3: Claude Code interpretiert Findings
    # ========================================================================
    
    print("📊 Analysis Results:")
    print("-" * 70)
    
    if "semantic_understanding" in outputs:
        print("\n### Semantic Understanding (Parsed Request):")
        print(json.dumps(outputs["semantic_understanding"], indent=2))
    
    if "research_results" in outputs:
        print("\n### Research Findings:")
        print(json.dumps(outputs["research_results"], indent=2))
    
    if "validation_results" in outputs:
        print("\n### Code Validation Results:")
        print(json.dumps(outputs["validation_results"], indent=2))
    
    if "final_report" in outputs:
        print("\n### Final Report:")
        print(outputs["final_report"])
    
    print("-" * 70)
    print()
    
    # ========================================================================
    # SCHRITT 4: Claude Code generiert Empfehlungen
    # ========================================================================
    
    print("💬 Claude Code Synthesis & Recommendations:")
    print()
    
    synthesis = """
    ## Analysis Complete für: customer-django-perf
    
    ### 🔍 Was wir gefunden haben:
    
    1. **Performance-Bottlenecks identifiziert:**
       - N+1 database queries in user listing endpoint
       - Missing database indexes on foreign keys
       - Caching not configured for frequently accessed data
    
    2. **Code Quality Findings:**
       - Moderate technical debt
       - Test coverage at 65% (good, but could be better)
       - Most dependencies are up-to-date
    
    3. **Infrastructure:**
       - AWS setup is standard but not optimized
       - Database connection pooling could be improved
    
    ### 📋 Recommended Action Plan:
    
    **Phase 1: Diagnostic (2 hours)**
    - Profile your application with Django Debug Toolbar
    - Identify exact slow queries
    - Measure baseline performance
    
    **Phase 2: Optimization (3-5 days)**
    - Fix N+1 queries with select_related/prefetch_related
    - Add database indexes
    - Implement caching layer (Redis)
    - Optimize asset serving
    
    **Phase 3: Validation (2 days)**
    - Load testing with same traffic patterns
    - Performance benchmarking
    - Production readiness checks
    
    ### 💰 Estimated Effort:
    - Total Duration: 5-7 days
    - Complexity: Medium (known patterns)
    - Confidence: HIGH (based on standard Django optimization practices)
    
    ### ✅ Next Steps:
    1. Would you like us to start with Phase 1 (Diagnostic)?
    2. We can have a detailed technical deep-dive call
    3. Or jump directly to Phase 2 if you prefer faster turnaround
    
    **Let's make your app fast again!** 🚀
    """
    
    print(synthesis)
    print()
    
    # ========================================================================
    # SCHRITT 5: Claude Code könnte weitere Actions durchführen
    # ========================================================================
    
    print("🔗 Mögliche weitere Actions:")
    print()
    print("□ Send proposal email to customer")
    print("□ Schedule technical deep-dive call")
    print("□ Create Jira ticket for Phase 1")
    print("□ Set up automated performance monitoring")
    print("□ Generate technical documentation")
    print()
    
    # ========================================================================
    # SCHRITT 6: Projektinformationen speichern
    # ========================================================================
    
    print("💾 Project Information:")
    print("-" * 70)
    print(f"Project ID: {project_id}")
    print(f"Status: Analysis Complete")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Executed Notebook: {result['executed_notebook']}")
    print()


def advanced_example():
    """Erweiterte Beispiele"""
    
    print("\n" + "=" * 70)
    print("🚀 Advanced Example: Multiple Workflows")
    print("=" * 70)
    print()
    
    client = AgencyClient()
    
    if not client.health_check():
        print("API not available")
        return
    
    # ========================================================================
    # Beispiel 1: Multiple Analysen hintereinander
    # ========================================================================
    
    projects = [
        {
            "name": "legacy-rails-app",
            "request": "We have a legacy Rails app that needs modernization",
            "tech": "rails"
        },
        {
            "name": "react-performance",
            "request": "React app is slow, need optimization",
            "tech": "react"
        },
        {
            "name": "nodejs-security",
            "request": "Node.js API needs security audit",
            "tech": "node"
        }
    ]
    
    results = {}
    
    for proj in projects:
        print(f"🔄 Analyzing: {proj['name']}")
        result = client.run_analysis(
            project_name=proj["name"],
            request=proj["request"],
            tech_stack=proj["tech"]
        )
        
        if result["status"] == "success":
            results[proj["name"]] = result
            print(f"✅ {proj['name']}: COMPLETE\n")
        else:
            print(f"❌ {proj['name']}: FAILED - {result['error']}\n")
    
    # Alle Ergebnisse zusammenfassen
    print("\n📊 Batch Analysis Results:")
    print(f"Completed: {len([r for r in results.values() if r['status'] == 'success'])}")
    print(f"Failed: {len([r for r in results.values() if r['status'] == 'error'])}")
    
    # ========================================================================
    # Beispiel 2: Status tracking
    # ========================================================================
    
    print("\n🔍 Checking Project Status:")
    
    for proj_name, result in results.items():
        if result["status"] == "success":
            status = client.get_status(result["project_id"])
            print(f"\n{proj_name}:")
            print(f"  Project Dir: {status['project_dir']}")
            print(f"  Notebooks: {len(status['executed_notebooks'])}")


if __name__ == "__main__":
    # Hauptbeispiel
    main()
    
    # Erweiterte Beispiele (auskommentiert)
    # advanced_example()
