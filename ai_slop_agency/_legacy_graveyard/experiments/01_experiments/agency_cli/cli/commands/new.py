import click
from core.project_manager import create_project

@click.command()
@click.argument('project_name')
@click.option('--client-input', prompt='Client request (raw text)', 
              help='Initial client message/request')
def new(project_name: str, client_input: str):
    """Creates a new project workspace with all protocol templates."""
    try:
        project_path = create_project(project_name, client_input)
        click.echo(f"✅ Project created successfully at: {project_path}")
        click.echo("\n📋 NEXT STEPS (HUMAN):")
        click.echo(f"1. Open {project_path / '01_semantic_understanding.md'}")
        click.echo("2. Fill in the [FILL: ...] sections.")
        click.echo("3. Identify research topics and run 'agency research <topic>'.")
    except FileExistsError as e:
        click.echo(f"❌ Error: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred: {e}", err=True)
