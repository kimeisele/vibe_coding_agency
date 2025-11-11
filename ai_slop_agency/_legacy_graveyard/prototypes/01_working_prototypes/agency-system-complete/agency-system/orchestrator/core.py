"""
Core Orchestrator: Notizbuch-Ausführung mit Papermill
- Notizbuch laden
- Parameter injizieren
- Mit LLM-API ausführen (Web-Search, Analysis)
- Outputs strukturiert zurückgeben
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class NotebookOrchestrator:
    """Orchestriert die Ausführung von Analyse-Notizbüchern."""
    
    def __init__(self, notebooks_dir: str, projects_dir: str):
        self.notebooks_dir = Path(notebooks_dir)
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        
    def run(
        self,
        notebook_type: str,  # "analysis", "code_generation", "refactoring"
        project_name: str,
        client_request: str,
        code_path: Optional[str] = None,
        tech_stack: Optional[str] = None,
        **additional_params
    ) -> Dict[str, Any]:
        """
        Führt ein Notizbuch aus (vollständiger Workflow).
        
        Args:
            notebook_type: Welches Notizbuch (analysis_workflow, etc.)
            project_name: Name des Projekts
            client_request: Rohe Kundenanfrage
            code_path: Optional: Pfad zur Codebasis für Scans
            tech_stack: Optional: Django, React, Node, etc.
            
        Returns:
            {
                "status": "success|error",
                "project_id": "acme-corp-django",
                "executed_notebook": "/path/to/project/.../executed.ipynb",
                "outputs": {
                    "semantic_understanding": {...},
                    "research_results": [...],
                    "scan_results": {...},
                    "final_report": "markdown string"
                },
                "metadata": {
                    "execution_time": "2025-11-10T14:30:00Z",
                    "steps_completed": 4,
                    "errors": []
                }
            }
        """
        
        # 1. Projektverzeichnis erstellen
        project_id = f"{project_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # 2. Template-Notizbuch finden
        template_notebook = self._get_template_notebook(notebook_type)
        if not template_notebook.exists():
            return {
                "status": "error",
                "error": f"Template notebook not found: {notebook_type}",
                "project_id": project_id
            }
        
        # 3. Output-Notizbuch vorbereiten
        output_notebook = project_dir / f"{notebook_type}_executed.ipynb"
        
        # 4. Parameter für Papermill zusammenstellen
        params = {
            "project_name": project_name,
            "client_request": client_request,
            "code_path": code_path or "",
            "tech_stack": tech_stack or "unknown",
            "execution_time": datetime.now().isoformat(),
            **additional_params
        }
        
        # 5. Papermill ausführen
        try:
            print(f"[ORCHESTRATOR] Executing notebook: {template_notebook}")
            print(f"[ORCHESTRATOR] Project: {project_id}")
            print(f"[ORCHESTRATOR] Parameters: {json.dumps(params, indent=2)}")
            
            # Papermill ausführen (CLI-Command)
            cmd = [
                "papermill",
                str(template_notebook),
                str(output_notebook),
                # Parameter als Key=Value pairs
                *[f"--parameters-yaml" if i == 0 else "" 
                  for i in range(1)]  # Hack für YAML-Parameter
            ]
            
            # Einfacher: Parameter als Input-Datei
            params_file = project_dir / "parameters.json"
            with open(params_file, "w") as f:
                json.dump(params, f, indent=2)
            
            # Papermill mit Python-API aufrufen (besser als CLI)
            import papermill as pm
            
            pm.execute_notebook(
                str(template_notebook),
                str(output_notebook),
                parameters=params,
                kernel_name="python3",
                timeout=600,  # 10 Minuten max
                progress_bar=True
            )
            
            print(f"[ORCHESTRATOR] ✓ Notebook executed successfully")
            
            # 6. Outputs extrahieren
            outputs = self._extract_outputs(output_notebook)
            
            return {
                "status": "success",
                "project_id": project_id,
                "executed_notebook": str(output_notebook),
                "project_dir": str(project_dir),
                "outputs": outputs,
                "metadata": {
                    "execution_time": datetime.now().isoformat(),
                    "template": notebook_type,
                    "parameters": params
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "project_id": project_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "executed_notebook": str(output_notebook) if output_notebook.exists() else None
            }
    
    def _get_template_notebook(self, notebook_type: str) -> Path:
        """Finde Template-Notizbuch nach Typ."""
        mapping = {
            "analysis": "analysis_workflow.ipynb",
            "code_generation": "code_generation_workflow.ipynb",
            "refactoring": "legacy_refactoring_workflow.ipynb"
        }
        filename = mapping.get(notebook_type, f"{notebook_type}.ipynb")
        return self.notebooks_dir / filename
    
    def _extract_outputs(self, notebook_path: Path) -> Dict[str, Any]:
        """Extrahiere strukturierte Outputs aus ausgeführtem Notizbuch."""
        try:
            import nbformat
            
            with open(notebook_path, "r") as f:
                notebook = nbformat.read(f, as_version=4)
            
            outputs = {}
            current_section = None
            
            for cell in notebook.cells:
                # Markdown-Zellen als Sektionen erkennen
                if cell.cell_type == "markdown":
                    if cell.source.startswith("#"):
                        current_section = cell.source.split("\n")[0].replace("#", "").strip().lower()
                        outputs[current_section] = cell.source
                
                # Code-Output sammeln
                elif cell.cell_type == "code" and cell.get("outputs"):
                    for output in cell.outputs:
                        if output.output_type == "display_data":
                            if current_section:
                                if current_section not in outputs:
                                    outputs[current_section] = []
                                outputs[current_section].append(output.data)
                        elif output.output_type == "execute_result":
                            if current_section:
                                if current_section not in outputs:
                                    outputs[current_section] = []
                                outputs[current_section].append(output.data)
            
            return outputs
            
        except Exception as e:
            return {
                "error": f"Could not extract outputs: {str(e)}",
                "notebook_path": str(notebook_path)
            }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Hole Status eines Projekts."""
        project_dir = self.projects_dir / project_id
        
        if not project_dir.exists():
            return {"status": "not_found", "project_id": project_id}
        
        files = list(project_dir.glob("*.ipynb"))
        param_file = project_dir / "parameters.json"
        
        status = {
            "status": "found",
            "project_id": project_id,
            "project_dir": str(project_dir),
            "executed_notebooks": [str(f) for f in files],
            "has_parameters": param_file.exists()
        }
        
        if param_file.exists():
            with open(param_file) as f:
                status["parameters"] = json.load(f)
        
        return status
