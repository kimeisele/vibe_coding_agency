"""
REST API für Agents (Claude Code, Gemini, etc.)
- Agents rufen HTTP-Endpoints auf
- Bekommen JSON zurück
- Können weitere API-Calls machen
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from typing import Dict, Any

from orchestrator.core import NotebookOrchestrator


class AgencyAPI:
    """REST API für Agent-Integration."""
    
    def __init__(self, notebooks_dir: str = "./notebooks", projects_dir: str = "./projects"):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.orchestrator = NotebookOrchestrator(notebooks_dir, projects_dir)
        self._setup_routes()
    
    def _setup_routes(self):
        """Registriere alle API-Endpoints."""
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health Check."""
            return jsonify({"status": "healthy", "service": "agency-api"})
        
        @self.app.route("/api/v1/run", methods=["POST"])
        def run_workflow():
            """
            Starte einen Workflow.
            
            POST /api/v1/run
            {
                "notebook_type": "analysis",
                "project_name": "acme-corp",
                "client_request": "Unsere Django-App ist langsam",
                "code_path": "/path/to/code",
                "tech_stack": "django"
            }
            """
            try:
                data = request.get_json()
                
                # Validierung
                required = ["notebook_type", "project_name", "client_request"]
                if not all(k in data for k in required):
                    return jsonify({
                        "status": "error",
                        "error": f"Missing required fields: {required}"
                    }), 400
                
                result = self.orchestrator.run(
                    notebook_type=data["notebook_type"],
                    project_name=data["project_name"],
                    client_request=data["client_request"],
                    code_path=data.get("code_path"),
                    tech_stack=data.get("tech_stack"),
                    **{k: v for k, v in data.items() 
                       if k not in required + ["code_path", "tech_stack"]}
                )
                
                if result["status"] == "error":
                    return jsonify(result), 500
                
                return jsonify(result), 200
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e)
                }), 500
        
        @self.app.route("/api/v1/status/<project_id>", methods=["GET"])
        def get_status(project_id):
            """
            Hole Status eines Projekts.
            
            GET /api/v1/status/acme-corp-django
            """
            status = self.orchestrator.get_project_status(project_id)
            return jsonify(status), 200
        
        @self.app.route("/api/v1/list-notebooks", methods=["GET"])
        def list_notebooks():
            """
            Liste verfügbare Notebook-Templates.
            
            GET /api/v1/list-notebooks
            """
            notebooks_dir = Path(self.orchestrator.notebooks_dir)
            notebooks = [f.name for f in notebooks_dir.glob("*.ipynb")]
            
            return jsonify({
                "status": "success",
                "notebooks": notebooks,
                "count": len(notebooks)
            }), 200
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Starte API-Server."""
        self.app.run(host=host, port=port, debug=debug)


# Standalone: Flask App exportieren für Production
def create_app(notebooks_dir: str = "./notebooks", projects_dir: str = "./projects"):
    """Factory für API-Erstellung (z.B. für Gunicorn)."""
    api = AgencyAPI(notebooks_dir, projects_dir)
    return api.app


if __name__ == "__main__":
    api = AgencyAPI()
    print("Starting Agency API on http://0.0.0.0:5000")
    print("Documentation:")
    print("  POST   /api/v1/run                      - Run workflow")
    print("  GET    /api/v1/status/<project_id>     - Get status")
    print("  GET    /api/v1/list-notebooks          - List templates")
    print("  GET    /health                         - Health check")
    api.run(debug=True)
