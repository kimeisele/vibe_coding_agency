"""
REST API Server - Enable remote Agent access to KDAF

Purpose: Allow Claude Code (and other agents) to run KDAF workflows remotely
Philosophy: Same logic as CLI, different interface

Usage:
    python3 shared/api/server.py --port 5000

Endpoints:
    POST /api/v1/analyze           → Run full or partial workflow
    GET  /api/v1/status/<project>  → Get project status
    GET  /api/v1/health            → Health check
"""

from flask import Flask, request, jsonify
from pathlib import Path
import sys
import logging
from datetime import datetime

# Add orchestration to path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from orchestration import WorkflowOrchestrator, StateManager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monorepo root
REPO_ROOT = Path(__file__).parent.parent.parent.absolute()
CLIENTS = REPO_ROOT / "clients"

@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Vibe Coding Agency KDAF API",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    """
    Run KDAF analysis workflow

    Request Body:
    {
        "project_path": "/path/to/project" OR "client_name/project_name",
        "phases": ["1", "2", "3", "4"] OR "full",
        "async": false
    }

    Response:
    {
        "status": "success" | "error",
        "project_id": "...",
        "phases_run": [...],
        "errors": [...],
        "final_state": {...},
        "report_path": "..." (if Phase 4 complete)
    }
    """
    try:
        data = request.json

        if not data:
            return jsonify({
                "status": "error",
                "error": "Request body required"
            }), 400

        # Parse project path
        project_path_str = data.get('project_path')
        if not project_path_str:
            return jsonify({
                "status": "error",
                "error": "project_path required"
            }), 400

        # Resolve project path
        project_path = _resolve_project_path(project_path_str)
        if not project_path:
            return jsonify({
                "status": "error",
                "error": f"Project not found: {project_path_str}"
            }), 404

        # Parse phases
        phases_input = data.get('phases', 'full')
        if phases_input == 'full':
            phases = ['1', '2', '3', '4']
        elif isinstance(phases_input, list):
            phases = phases_input
        else:
            phases = str(phases_input).split(',')

        # Async mode (future enhancement)
        is_async = data.get('async', False)

        logger.info(f"Starting analysis: project={project_path}, phases={phases}")

        # Run orchestrator
        orchestrator = WorkflowOrchestrator(project_path)
        result = orchestrator.run_analysis(phases)

        # Build response
        response = {
            "status": "success" if not result['errors'] else "partial_success",
            "project_id": result['final_state']['project_id'],
            "project_name": result['final_state']['project_name'],
            "client": result['final_state']['client'],
            "phases_run": result['phases_run'],
            "errors": result['errors'],
            "final_state": result['final_state']
        }

        # Add report path if Phase 4 complete
        if '4' in [p['phase'] for p in result['phases_run'] if p['status'] == 'COMPLETE']:
            phase_4_result = [p for p in result['phases_run'] if p['phase'] == '4'][0]['result']
            response['report_path'] = phase_4_result['report_path']

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/v1/status/<project_identifier>', methods=['GET'])
def get_status(project_identifier):
    """
    Get project status

    Args:
        project_identifier: "client_name/project_name" or absolute path

    Response:
    {
        "status": "success",
        "project_id": "...",
        "project_name": "...",
        "client": "...",
        "phase_statuses": {...},
        "confidence": "...",
        "next_action": "...",
        "last_updated": "..."
    }
    """
    try:
        # Resolve project path
        project_path = _resolve_project_path(project_identifier)
        if not project_path:
            return jsonify({
                "status": "error",
                "error": f"Project not found: {project_identifier}"
            }), 404

        # Get state
        state_manager = StateManager(project_path)
        summary = state_manager.get_summary()

        return jsonify({
            "status": "success",
            **summary
        }), 200

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/v1/projects', methods=['GET'])
def list_projects():
    """
    List all projects

    Response:
    {
        "status": "success",
        "projects": [
            {
                "client": "...",
                "project_name": "...",
                "path": "...",
                "last_updated": "..."
            }
        ]
    }
    """
    try:
        projects = []

        for client_dir in CLIENTS.iterdir():
            if not client_dir.is_dir() or not client_dir.name.startswith('client_'):
                continue

            client_name = client_dir.name.replace('client_', '')

            for project_dir in client_dir.iterdir():
                if not project_dir.is_dir():
                    continue

                # Check for state.json
                state_file = project_dir / "state.json"
                if state_file.exists():
                    state_manager = StateManager(project_dir)
                    summary = state_manager.get_summary()

                    projects.append({
                        "client": client_name,
                        "project_name": project_dir.name,
                        "path": str(project_dir),
                        "last_updated": summary['last_updated'],
                        "confidence": summary['confidence'],
                        "next_action": summary['next_action']
                    })

        return jsonify({
            "status": "success",
            "count": len(projects),
            "projects": projects
        }), 200

    except Exception as e:
        logger.error(f"Project listing failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Helper functions

def _resolve_project_path(identifier: str) -> Path:
    """
    Resolve project path from various formats:
    - Absolute path: "/path/to/project"
    - Relative: "client_name/project_name"
    - Project name only: "project_name" (searches all clients)
    """
    # Try as absolute path
    path = Path(identifier)
    if path.is_absolute() and path.exists():
        return path

    # Try as client/project
    if '/' in identifier:
        parts = identifier.split('/')
        if len(parts) == 2:
            client_name, project_name = parts
            project_path = CLIENTS / f"client_{client_name}" / project_name
            if project_path.exists():
                return project_path

    # Try searching by project name
    project_name = identifier
    for client_dir in CLIENTS.iterdir():
        if client_dir.is_dir() and client_dir.name.startswith('client_'):
            project_path = client_dir / project_name
            if project_path.exists():
                return project_path

    return None

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="KDAF REST API Server")
    parser.add_argument('--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    logger.info(f"Starting KDAF API server on {args.host}:{args.port}")

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
