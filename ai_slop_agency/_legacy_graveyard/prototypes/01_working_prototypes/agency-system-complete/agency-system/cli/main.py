#!/usr/bin/env python3
"""
Agency CLI: Schlanke Fernbedienung für Notizbuch-Orchestrator.
- Für Claude Code (Agent) bedienbar
- Auch via HTTP möglich (siehe REST API)
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

from orchestrator.core import NotebookOrchestrator


# CLI Konfiguration
NOTEBOOKS_DIR = Path(__file__).parent.parent / "notebooks"
PROJECTS_DIR = Path(__file__).parent.parent / "projects"

orchestrator = NotebookOrchestrator(str(NOTEBOOKS_DIR), str(PROJECTS_DIR))


@click.group()
def cli():
    """Agency CLI - Orchestrate analysis notebooks for agents."""
    pass


@cli.command()
@click.argument("project_name")
@click.option("--notebook", "-n", default="analysis", 
              help="Notebook type: analysis, code_generation, refactoring")
@click.option("--request", "-r", prompt="Client request", 
              help="The raw client request/problem")
@click.option("--code-path", "-c", default=None,
              help="Path to client code for scanning")
@click.option("--tech-stack", "-t", default=None,
              help="Tech stack: django, react, node, etc.")
@click.option("--output-format", "-f", default="json",
              type=click.Choice(["json", "text", "markdown"]),
              help="Output format")
def run(
    project_name: str,
    notebook: str,
    request: str,
    code_path: Optional[str],
    tech_stack: Optional[str],
    output_format: str
):
    """
    Run a workflow notebook.
    
    Example:
        agency run acme-corp \\
            --notebook analysis \\
            --request "Django app is slow" \\
            --tech-stack django \\
            --code-path ./acme_code
    """
    click.echo(f"🚀 Starting workflow for: {project_name}")
    
    result = orchestrator.run(
        notebook_type=notebook,
        project_name=project_name,
        client_request=request,
        code_path=code_path,
        tech_stack=tech_stack
    )
    
    # Output formatting
    if result["status"] == "error":
        click.secho(f"❌ Error: {result.get('error')}", fg="red")
        sys.exit(1)
    
    if output_format == "json":
        click.echo(json.dumps(result, indent=2))
    elif output_format == "markdown":
        _print_markdown(result)
    else:
        _print_text(result)
    
    click.secho(f"✅ Project completed: {result['project_id']}", fg="green")


@cli.command()
@click.argument("project_id")
@click.option("--output-format", "-f", default="json",
              type=click.Choice(["json", "text"]))
def status(project_id: str, output_format: str):
    """
    Check project status.
    
    Example:
        agency status acme-corp-django-20251110_143000
    """
    result = orchestrator.get_project_status(project_id)
    
    if result["status"] == "not_found":
        click.secho(f"❌ Project not found: {project_id}", fg="red")
        sys.exit(1)
    
    if output_format == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Project: {project_id}")
        click.echo(f"Directory: {result['project_dir']}")
        click.echo(f"Notebooks: {len(result['executed_notebooks'])}")
        for nb in result['executed_notebooks']:
            click.echo(f"  - {Path(nb).name}")


@cli.command()
def list_notebooks():
    """
    List available notebook templates.
    
    Example:
        agency list-notebooks
    """
    notebooks = list(NOTEBOOKS_DIR.glob("*.ipynb"))
    
    if not notebooks:
        click.secho("No notebooks found.", fg="yellow")
        return
    
    click.echo("Available notebooks:")
    for nb in sorted(notebooks):
        click.echo(f"  📓 {nb.name}")


@cli.command()
@click.option("--port", "-p", default=5000, type=int)
@click.option("--host", "-h", default="0.0.0.0")
def serve(port: int, host: str):
    """
    Start REST API server for agents.
    
    Example:
        agency serve --port 5000
    """
    click.echo(f"🚀 Starting API server on {host}:{port}")
    click.echo("Endpoints:")
    click.echo(f"  POST   http://{host}:{port}/api/v1/run")
    click.echo(f"  GET    http://{host}:{port}/api/v1/status/<project_id>")
    click.echo(f"  GET    http://{host}:{port}/api/v1/list-notebooks")
    click.echo(f"  GET    http://{host}:{port}/health")
    
    from api.rest import create_app
    app = create_app(str(NOTEBOOKS_DIR), str(PROJECTS_DIR))
    app.run(host=host, port=port, debug=True)


# Helper functions for formatting
def _print_text(result: dict):
    """Print result in text format."""
    click.echo(f"\n{'='*60}")
    click.echo(f"Project: {result['project_id']}")
    click.echo(f"Status: {result['status']}")
    click.echo(f"Notebook: {result['executed_notebook']}")
    click.echo(f"{'='*60}\n")
    
    if "outputs" in result:
        click.echo("Outputs:")
        for key, value in result["outputs"].items():
            click.echo(f"\n  [{key}]")
            if isinstance(value, str):
                click.echo(f"    {value[:200]}...")
            else:
                click.echo(f"    {json.dumps(value, indent=6)[:200]}...")


def _print_markdown(result: dict):
    """Print result in markdown format."""
    click.echo(f"# Project: {result['project_id']}\n")
    click.echo(f"**Status:** {result['status']}\n")
    click.echo(f"**Executed Notebook:** {result['executed_notebook']}\n")
    
    if "outputs" in result:
        click.echo("## Outputs\n")
        for key, value in result["outputs"].items():
            click.echo(f"### {key.replace('_', ' ').title()}\n")
            if isinstance(value, str):
                click.echo(f"{value}\n")
            else:
                click.echo(f"```json\n{json.dumps(value, indent=2)}\n```\n")


if __name__ == "__main__":
    cli()
